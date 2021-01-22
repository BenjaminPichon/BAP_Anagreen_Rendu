"""This module contains the view for the index page"""

import config
import json
import importlib
import numpy as np
import flask
import time
import datetime
#from flask import session
from flask import Flask, session
from bokeh import events
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, tools, TableColumn, DataTable, PreText, CustomJS, ImageURL, \
    CDSView, GroupFilter, BoxEditTool, PointDrawTool
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from flask import Blueprint
from flask import jsonify
from sqlalchemy import create_engine
from shutil import copyfile
from config import engine
import bokeh_table as bt



# Route for handling the login page logic
login_bp = Blueprint('login', __name__)
@login_bp.route('/login.html', methods=['GET', 'POST'])
def login():
    error = None
    if flask.request.method == 'POST':
        if flask.request.form['username'] != 'admin' or flask.request.form['password'] != 'anayellow':
            error = 'Invalid Credentials. Please try again.'
        else:
            resp = flask.make_response(flask.redirect('index.html'))
            resp.set_cookie('auth', 'anayellow')
            return resp 
    return flask.render_template('login.html', 
        error=error, 
        config=config)

index_bp = Blueprint('index_page', __name__)

# Route for handling the index page (chosing case)
@index_bp.route("/")
@index_bp.route("/index.html")
def index_page():
	session.pop('gl_id_study_case', None) #reset id of the study case in the server side app's memory
	# # Render template
	study_cases = {
		"ID_Study_Case":[],
		"Name": [],
		"Path_to_plan":[],
		"company_name": []
	}

	query = "SELECT * FROM study_case"
	result = engine.execute(query)
	for row in result:
		print(row.items())
		for (key, val) in row.items():
			if key == "Path_to_plan" and val == "":
				study_cases[key].append("pas-d-image-disponible.jpg")
			elif key == "company_name" and val is None:
				study_cases[key].append("")
			else:
				study_cases[key].append(val)

	source= ColumnDataSource(study_cases)
	
	study_cases_array = []

	for step in range(len(study_cases["ID_Study_Case"])): #fill an array of study case information
		study_cases_array.append(dict(
			id=study_cases["ID_Study_Case"][step],
			name= study_cases["Name"][step],
			company_name = study_cases["company_name"][step],
			path_to_map = "../static/"+study_cases["Path_to_plan"][step],
		))
	print ("ICI LE PRINT DE STUDY CASE :"+str(type(study_cases_array[0]['path_to_map'])))	
	myscript200, mydiv200 = components(bt.table(source, column_list=['id', 'name'], width=800))
	html = flask.render_template(
		'index.html',
		page_id=0,
		config=config,
		script200=myscript200,
		div200=mydiv200,
		tl=study_cases_array,
		resources=INLINE.render()
	)

	return encode_utf8(html)
    
@index_bp.route("/ajax_index", methods=['GET', 'POST'])
def ajax():
	if flask.request.args['action'] == "set_study_case_id":
		data = json.loads(flask.request.form["idsc"])
		session['gl_id_study_case'] = data #save id of study case in server's memory

	if flask.request.args['action'] == "add_new_case":
		data = json.loads(flask.request.form["data"])
		case = (
			data["name"],
			data["company"],
			"",
		)
		engine.execute("INSERT INTO study_case (Name , company_name , Path_to_plan) VALUES(?,?,?)",case)
		
	return "ok"


 
