"""This module contains the view for the history page. """

from pprint import pprint
import flask
from flask import Flask, session
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from flask import Blueprint, url_for
from werkzeug.utils import redirect
import bokeh_table as bt
import calcul as cal
import hashlib
import anagreen_main
import config
import importlib
import copy
import json
import time
import os
import psutil
import bz2


from sqlalchemy import create_engine
from config import engine


history_bp = Blueprint('history_page', __name__)

        
@history_bp.route("/history_ajax", methods=['GET', 'POST'])
def ajax():

    if flask.request.args['action'] == "history_preview":
        id=int(flask.request.args['id'])
        query="SELECT * FROM history WHERE id=?"
        result = engine.execute(query,(id)).fetchone()
        compressed_solution = result['solution']
        solution=bz2.decompress(compressed_solution).decode()
        return solution
        
    if flask.request.args['action'] == "history_restore":
        id=int(flask.request.args['id'])
        query="SELECT * FROM history WHERE id=?"
        result = engine.execute(query,(id)).fetchone()
        
        parameters_sig = result['parameters_sig']
        timestamp = result['timestamp']
        compressed_params = result['parameters']
        compressed_solution = result['solution']
        
        timestamp=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(int(timestamp)))
        parameters=bz2.decompress(compressed_params).decode()
        solution=bz2.decompress(compressed_solution).decode()
        
        #restore data in the database
        parameters=json.loads(parameters)
        solution=json.loads(solution)
        restore_data={**parameters, **solution}
        
        
        for (table, data) in restore_data.items():
            
            # restore tables
            # For the insert, multiple queies would be really slow, so we use
            # INSERT INTO table (columnA, columnB, ...) VALUES (?, ?, ...), (?, ?, ...), ...
            # the list of columns is stored in list_keys
            # the multiples (?, ?, ...) are stored in all_list_spchr
            # and we store the values that will replace the ? in the list all_list_val
            
            engine.execute("DELETE FROM "+table)
            engine.execute("DELETE FROM sqlite_sequence WHERE name=?",(table)) # reset autoincrement id
        
            all_list_val=[]
            all_list_spchr=[]
            for line in data:
                list_keys=[]
                list_val=[]
                list_spchr=[]
                for (cell_key, cell_val) in line.items():
                    list_keys.append(cell_key)
                    list_val.append(cell_val)
                    all_list_val.append(cell_val)
                    list_spchr.append('?')
                tulpe_spchr="("+ ", ".join(list_spchr) +")" 
                all_list_spchr.append(tulpe_spchr)
            list_keys=', '.join(list_keys)
            all_list_spchr=', '.join(all_list_spchr)
            query="INSERT INTO "+table+" ("+list_keys+") VALUES "+all_list_spchr+""
            engine.execute(query, all_list_val)
            
            # print(query)
                
        engine.execute("UPDATE configuration SET value = ? WHERE name = 'parameters_sig'",(parameters_sig))
        engine.execute("UPDATE configuration SET value = 2 WHERE name = 'status'")
        importlib.reload(config)
        
        engine.execute("VACUUM")
        importlib.reload(config)
        return "OK"
        
        
        
@history_bp.route("/history.html", methods=['GET', 'POST'])
def results_page():

    query="SELECT value FROM configuration WHERE name = 'status'"
    result = engine.execute(query).fetchone()
    status = int(result[0])
    
    query="SELECT value FROM configuration WHERE name = 'params_sig'"
    result = engine.execute(query).fetchone()
    params_sig = str(result[0])
    
    (signaturestr, save_parameters)=config.get_params_sig()
    
    params_changed=0
    if status==2 and params_sig!=signaturestr:
        params_changed=1

    # Load solutions from DB
    solution = {
        'id': [],
        'timestamp': [],
        'solution_len': [],
        'parameters_sig': [],
        'parameters_sig_short': []
    }
    if session.get('gl_id_study_case', None)!=None:
        id_study_case = session.get('gl_id_study_case', None)
    else :
        id_study_case = "0"
    query="SELECT id, timestamp, parameters_sig, length(solution) as solution_len FROM history WHERE ID_Study_Case = "+str(id_study_case)+"  ORDER BY timestamp DESC"
    result = engine.execute(query)
    for row in result:
        for (key, val) in row.items():
            if key == "timestamp":
                val=str(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(int(val))))
            if key == "parameters_sig":
                solution['parameters_sig_short'].append(val[0:12])
            solution[key].append(val)
    
    
    source = ColumnDataSource(solution)
    # this function takes a list and make so that it becomes a list of dictionnaries
    tl = []
    for step in range(len(solution['id'])):
        tl.append(dict(
            id=solution['id'][step],
            timestamp=solution['timestamp'][step],
            solution_len=solution['solution_len'][step],
            parameters_sig_short=solution['parameters_sig_short'][step],
            parameters_sig=solution['parameters_sig'][step]))

    myscript200, mydiv200 = components(bt.table(source, column_list=['id', 'timestamp', 'parameters_sig'], width=800))
    resources = INLINE.render()
    html = flask.render_template(
        "history.html",
        page_id=4,
        files_sig=config.files_sig,
        status=config.status,
        params_changed=params_changed,
        script200=myscript200,
        div200=mydiv200,
        tl=tl,
        resources=resources,
    )
    return encode_utf8(html)
