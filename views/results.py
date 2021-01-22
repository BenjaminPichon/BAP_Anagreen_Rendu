"""This module contains the view for the result page"""

from pprint import pprint

import flask
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
from flask import Flask, session

from sqlalchemy import create_engine
from config import engine

from algorithmes_simulation import Principale
from algorithmes_simulation.classes import Flux
from views.results_graphs import flux_diag, flux_map

id_study_case = 0

results_bp = Blueprint('results_page', __name__)

@results_bp.route("/results.html", methods=['GET', 'POST'])
def results_page():
    if session.get('gl_id_study_case', None) != None:
        id_study_case=session.get('gl_id_study_case', None)
    else:
        id_study_case = 0
    
    request_data = flask.request.form.to_dict()
    
    # don't save the cRSF token in param signature
    request_data['csrf_token'] = '' 
    
    # We load the page empty, display a progress modal and make an ajax request to launch calculation and wait for result
    query="SELECT value FROM configuration WHERE name = 'status'"
    result = engine.execute(query).fetchone()
    status = int(result[0])
    print ("ICI LE STATUS QUAND FONCTION APPELE :"+str(status))
    
    query="SELECT value FROM configuration WHERE name = 'current_simulation_status_code'"
    result = engine.execute(query).fetchone()
    code_status = result[0]
    
    if flask.request.form:
        # Saving Parametrization parameters in database
        engine.execute("DELETE FROM parametrization")
        engine.execute("DELETE FROM sqlite_sequence WHERE name='parametrization'")
        engine.execute("VACUUM")
        for data in request_data.items():
            engine.execute("INSERT INTO parametrization (name , value) VALUES(?, ?)", data)

    (signaturestr, save_parameters)=config.get_params_sig()

    # save simulation in history table
    if status==0 :
        compressed_params=bz2.compress(json.dumps(save_parameters).encode())
        inserted_key = engine.execute("INSERT INTO history (timestamp , parameters, parameters_sig, solution) VALUES(cast(strftime('%s','now') as int), ?, ?, ?) ",
            (compressed_params,
            signaturestr,
            '')).lastrowid
        engine.execute("UPDATE configuration SET value = ? WHERE name = 'history_id'",(inserted_key))
        importlib.reload(config)

    
    query="SELECT value FROM configuration WHERE name = 'params_sig'"
    result = engine.execute(query).fetchone()
    params_sig = str(result[0])
    
    
    if status==2 and params_sig!=signaturestr:
        engine.execute("UPDATE configuration SET value = 3 WHERE name = 'status' AND value=2")
        importlib.reload(config)
        status=3
    
    # No results for now, so we load an empty page (render template with empty array)
    if status==0 or status==1:
        engine.execute("UPDATE configuration SET value = ? WHERE name = 'params_sig'", (signaturestr))
        importlib.reload(config)
        
        solution = {
            "id": [],
            "rank": [],
            "savedEnergy": [],
            "capex": [],
            "roi": [],
            "opex": [],
            "storedEnergy": [],
            "CO2Savings": [],
            "score": []
        }
        source = ColumnDataSource(solution)
        # this function takes a list and make so that it becomes a list of dictionnaries
        tl = []
        myscript200, mydiv200 = components(bt.table(source, column_list=['rang', 'savedEnergy', 'capex', 'roi'], width=800))
        resources = INLINE.render()
        html = flask.render_template(
            'results.html',
            page_id=3,
            config=config,
            script200=myscript200,
            div200=mydiv200,
            tl=tl,
            resources=resources,
            simulation_status=status,
            simulation_status_code=code_status,
        )
        return encode_utf8(html)

    # Load solutions from DB
  
    solution = {
        "id": [],
        "rank": [],
        "Percent_MER": [],
        "savedEnergy": [],
        "capex": [],
        "roi": [],
        "opex": [],
        "CO2Savings": [],
        "score": []
    }
    query="SELECT id, rank, savedEnergy, capex, roi, opex, CO2Savings, score, Percent_MER FROM solution WHERE ID_Study_Case ="+str(id_study_case)+" ORDER BY rank"
    result = engine.execute(query)
    for row in result:
        for (key, val) in row.items():
            if val is not None:
                solution[key].append(round(val, 2))
            else:
                solution[key].append(val)
    
    source = ColumnDataSource(solution)
    # this function takes a list and make so that it becomes a list of dictionnaries
    tl = []
    for step in range(len(solution["rank"])):
        roi = "Non rentable" if solution["roi"][step] < 0 else solution["roi"][step]
        tl.append(dict(
            id=solution["id"][step],
            rank=solution["rank"][step],
            savedEnergy=solution["savedEnergy"][step],
            capex=solution["capex"][step],
            opex=solution["opex"][step],
            roi=roi,
            CO2Savings=solution["CO2Savings"][step],
            PERCENTofMER=solution["Percent_MER"][step],
            score=solution["score"][step]))

    myscript200, mydiv200 = components(bt.table(source, column_list=['rang', 'savedEnergy', 'capex', 'roi', 'CO2Savings', 'score'], width=800))
    resources = INLINE.render()
    html = flask.render_template(
        'results.html',
        page_id=3,
        files_sig=config.files_sig,
        status=config.status,
        script200=myscript200,
        div200=mydiv200,
        tl=tl,
        resources=resources,
        result_available=status,
        simulation_status=status,
        simulation_status_code=code_status,
    )
    return encode_utf8(html)

    
        
@results_bp.route("/results_ajax", methods=['GET', 'POST'])
def ajax():
    if session.get('gl_id_study_case', None) != None:
        id_study_case=session.get('gl_id_study_case', None)
    else:
        id_study_case = 0

    # A AFFINER
    if flask.request.args['action'] == "reset_results":
        engine.execute("DELETE FROM network WHERE ID_Study_Case=" + str(id_study_case))
        engine.execute("DELETE FROM sqlite_sequence WHERE name='network'") # reset autoincrement id
        engine.execute("DELETE FROM solution WHERE ID_Study_Case=" + str(id_study_case))
        engine.execute("DELETE FROM sqlite_sequence WHERE name='solution'") # reset autoincrement id
        engine.execute("DELETE FROM ssflux ")
        # engine.execute("DELETE FROM ssflux WHERE ID_Study_Case=" + str(id_study_case))
        engine.execute("DELETE FROM sqlite_sequence WHERE name='ssflux'") # reset autoincrement id
        engine.execute("DELETE FROM exchanger")
        # engine.execute("DELETE FROM exchanger WHERE ID_Study_Case=" + str(id_study_case))
        engine.execute("DELETE FROM sqlite_sequence WHERE name='exchanger'") # reset autoincrement id
        engine.execute("DELETE FROM utility")
        # engine.execute("DELETE FROM exchanger WHERE ID_Study_Case=" + str(id_study_case))
        engine.execute("DELETE FROM sqlite_sequence WHERE name='utility'") # reset autoincrement id
        engine.execute("UPDATE configuration SET value = 0 WHERE name = 'status'")
        engine.execute("VACUUM")
        importlib.reload(config)
        return "OK"
        
    if flask.request.args['action'] == "wait_results":
        if session.get('gl_id_study_case', None) != None:
            id_study_case=session.get('gl_id_study_case', None)
        else:
            id_study_case = 0

        pid=os.getpid()

        engine.execute("UPDATE configuration SET value = ? WHERE name = 'current_simulation_pid'",(pid))
        engine.execute("UPDATE configuration SET value = 1 WHERE name = 'status'")
        importlib.reload(config)
        print('SET SIMUL PID='+str(pid))


        print("***ALGO START***")
        ensFlux, deltaTmin, pos_flux = data_injector(id_study_case)

        # reseaux = AlgoFinal.AlgoFinal(1/11,1772,1044,pos_flux, ensFlux, deltaTmin)
        # reseaux = Principale.AlgoFinal(1/11,1772,1044,pos_flux, ensFlux, deltaTmin)
        reseaux = Principale.AlgoFinal(0.05,400,400,pos_flux, ensFlux, deltaTmin)
        print("***ALGO DONE***")
        engine.execute("UPDATE configuration SET value = 2 WHERE name = 'status'")
        importlib.reload(config)
        process_results(reseaux)

        return "SIMULATION FINISHED"
        
    if flask.request.args['action'] == "progress_results":
        query="SELECT value FROM configuration WHERE name = 'progress'"
        result = engine.execute(query).fetchone()
        progress= result[0]
        
        query2="SELECT value FROM configuration WHERE name = 'status'"
        result2 = engine.execute(query2).fetchone()
        status=result2[0]
        
        query3="SELECT value FROM configuration WHERE name = 'current_simulation_pid'"
        result3 = engine.execute(query3).fetchone()
        pid = int(result3[0])
        
        valid=True
        status_name=''
        if status == '1':
            # Check if PID exist
            exist=psutil.pid_exists(pid)
            if not exist:
                status_name='STATUS_NOEXIST'
                valid=False
            else:
                p = psutil.Process(pid)
                pstat = p.status()
                if pstat != psutil.STATUS_RUNNING:
                    print('PID NOt RUNNING:'+str(pid))
                    valid=False
                    # p.kill() # maybe kill the process?
                if pstat == psutil.STATUS_RUNNING:
                    status_name='STATUS_RUNNING'
                if pstat == psutil.STATUS_SLEEPING:
                    status_name='STATUS_SLEEPING'
                if pstat == psutil.STATUS_DISK_SLEEP:
                    status_name='STATUS_DISK_SLEEP'
                if pstat == psutil.STATUS_STOPPED:
                    status_name='STATUS_STOPPED'
                if pstat == psutil.STATUS_TRACING_STOP:
                    status_name='STATUS_TRACING_STOP'
                if pstat == psutil.STATUS_ZOMBIE:
                    status_name='STATUS_ZOMBIE'
                if pstat == psutil.STATUS_DEAD:
                    status_name='STATUS_DEAD'
                # print(status_name)
            if not valid:
                engine.execute("UPDATE configuration SET value = 4 WHERE name = 'status'")
                status='4'
        
        engine.execute("UPDATE configuration SET value = ? WHERE name = 'current_simulation_status_code'",(status_name))
        importlib.reload(config)

        return progress+'@'+status+'@'+str(pid)+'@'+str(valid)+'@'+status_name


def process_results(reseaux):
    query2="SELECT value FROM configuration WHERE name = 'status'"
    result2 = engine.execute(query2).fetchone()
    status=result2[0]

    if status == '2':
        print ("MER",reseaux.KPI.mer,"kW | pourcentage MER",reseaux.KPI.prctMer,"% | nombre utilités",reseaux.KPI.nbUti,"| nombre échangeur",reseaux.KPI.nbEch)
        score = 100
        rank = 1
        roi = reseaux.KPI.cap/(reseaux.KPI.ecoElec-reseaux.KPI.op)
        id_study_case = session.get('gl_id_study_case', None)
        
        solution = (
            rank,
            reseaux.KPI.enEch, #puissance echangé 
            reseaux.KPI.co2, #saved CO2
            score, 
            reseaux.KPI.cap, # CAPEX
            reseaux.KPI.op, # OPEX
            id_study_case,
            (reseaux.KPI.prctMer)*200, # % MER
            roi,
            reseaux.KPI.capex_ech,
            reseaux.KPI.capex_pompes,
            reseaux.KPI.capex_tuy,
            reseaux.KPI.capex_etude,
            reseaux.KPI.capex_install, 
            reseaux.KPI.capex_reglage, 
            reseaux.KPI.capex_admin, 
            reseaux.KPI.opex_pompes,  
            reseaux.KPI.opex_utilites,  
            reseaux.KPI.opex_maint, 
            reseaux.KPI.opex_entretien, 
            reseaux.KPI.mer,
            reseaux.KPI.prctMer,
            reseaux.KPI.puissEch,
            reseaux.KPI.nbUti,
            reseaux.KPI.nbEch,
            reseaux.KPI.enEch,
            reseaux.pincementF,
            reseaux.pincementC
            
        )
        print (solution)
        engine.execute("INSERT INTO solution (rank, savedEnergy, CO2Savings, score, capex, opex, ID_Study_Case, Percent_MER, roi, capex_ech, capex_pompes, capex_tuyauterie, capex_etude, capex_install, capex_reglage, capex_admin, opex_pompes, opex_utilites, opex_maint, opex_entretien, kpi_mer, kpi_prctMer, kpi_puissEch, kpi_nbUti, kpi_nbEch, kpi_enEch, pincementF, pincementC) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", solution)

        #-AA-
        res = engine.execute('SELECT seq from sqlite_sequence where name="solution"')
        # engine.execute("INSERT INTO solution (rank, savedEnergy, CO2Savings, score, capex, opex, ID_Study_Case, Percent_MER, roi, capex_ech, capex_pompes, capex_tuyauterie, capex_etude, capex_install, capex_reglage, capex_admin, opex_pompes, opex_utilites, opex_maint, opex_entretien, opex_taxe, opex_assurance, opex_frais, kpi_mer, kpi_prctMer, kpi_nbUti, kpi_nbEch, kpi_enEch, pincementF, pincementC) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); SELECT last_insert_rowid();", solution)

        for row in res:
            solId = row[0]

        print('-------------Sous-flux :-------------------')
        for row in reseaux.listeSsFlux:
            sf = (
                row.refFlux[0], #numFlux,
                row.refFlux[1], #numSsFlux,
                row.typeFlux,
                row.Te,
                row.Ts,
                solId
                #id_study_case,
                

            )
            print(sf)
            print("x:",row.x, "y:",row.y)
            engine.execute("INSERT INTO ssflux (numFlux, numSsFlux, typeFlux, Te, Ts, id_solution) VALUES(?, ?, ?, ?, ?, ?)", sf)

        print("\n")

        print('-------------Echangeurs :-------------------')
        for row in reseaux.listeCouple:
            ech = (
                
                row.ssFluxF[0],#numFluxF,
                row.ssFluxF[1],#numSsFluxF,
                row.ssFluxC[0],#numFluxC,
                row.ssFluxC[1],#numSsFluxC,
                row.puissE,
                row.objEch.typee,
                row.objEch.cout,
                row.objEch.perteFroid,
                row.objEch.perteChaud,
                row.couttot, #cout de l'échangeur + tuyauterie associée
                row.lontuy,#longueur de la tuyauterie associée
                row.capexech, #capex de l'échangeur + tuyauterie
                row.opexech, #opex de l'échangeur + tuyauterie
                row.co2ech, #co2 sauvé par l'échangeur
                row.ecototech, #économie réalisée par l'échangeur
                row.triech, #TRI de échangeur + tuyauterie
                row.vanech, #VAN de échangeur + tuyauterie
                row.ipech, #IP de échangeur + tuyauterie  
                row.objEch.surfEch,
                solId
 
            )
            print(ech)
            engine.execute("INSERT INTO exchanger (numFluxF, numSsFluxF, numFluxC, numSsFluxC,puissE, type,  cout, perteFroid, perteChaud, coutTotal, longTuyau, capexEch, opexEch, co2Ech, ecoTotEch, triEch, vanEch, ipEch,surfEch, id_solution) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ech)
           
        print("\n") 
        print('-------------Utilites :-------------------')
        for row in reseaux.listeUtilite:
            print(str(row.ssFlux)+" "+str(type(row.ssFlux)))
            if not type(row.ssFlux) is tuple:
                ssf0 = row.ssFlux.refFlux[0]
                ssf1 = row.ssFlux.refFlux[1]
            else:
                ssf0 = row.ssFlux[0]
                ssf1 = row.ssFlux[1]

            ut = (
                
                ssf0,#numFlux,
                ssf1,#numSsFlux,
                row.puissE,
                row.typeUtil,
                solId,

            )
            print(ut)
            engine.execute("INSERT INTO utility (numFlux, numSsFlux, puissE, type, id_solution) VALUES(?, ?, ?, ?, ?)", ut)
           
        print("\n")
        print('-------------Graphiques -------------------')
        ssFlux = {
            "id_ssflux": [],
            "numFlux": [],
            "numSsFlux": [],
            "typeFlux": [],
            "name": [],
            "Te": [],
            "Ts": [],
            }
        query="SELECT id_ssflux, numFlux, numSsFlux, typeFlux, name, Te, Ts FROM ssflux LEFT JOIN flux_v2 ON ssflux.numFlux = flux_v2.number AND ssflux.typeFlux = flux_v2.hotcold  WHERE id_solution = "+ str(solId) +" ORDER BY numFlux, numSsFlux"
        result = engine.execute(query)
        for row in result:
            for (key, val) in row.items():
                # print(str(key)+" "+str(val))
                ssFlux[key].append(val)
                
        exc = {
                
            "id_exchanger": [],
            "numFluxF": [],
            "numSsFluxF": [],
            "numFluxC": [],
            "numSsFluxC": [],
            "type": [],
            "puissE": [],
            "cout": [],
            "perteFroid": [],
            "perteChaud": []
            }
        query="SELECT id_exchanger, numFluxF, numSsFluxF, numFluxC, numSsFluxC, type, puissE, cout, perteFroid, perteChaud FROM exchanger WHERE id_solution = "+ str(solId) +" ORDER BY id_exchanger"
        result = engine.execute(query)
        for row in result:
            for (key, val) in row.items():
                exc[key].append(val)

        util = {
                
            "id_utility": [],
            "numFlux": [],
            "numSsFlux": [],
            "type": [],
            "puissE": []
            }
        query="SELECT id_utility, numFlux, numSsFlux,type, puissE FROM utility WHERE id_solution = "+ str(solId) +" ORDER BY id_utility"

        result = engine.execute(query)
        for row in result:
            for (key, val) in row.items():
                util[key].append(val)
        mapconfig = config.CaseConfig()
        mapconfig.setValues(int(solId))
        mapconfig.data_flux = {
            "id": [],
            "name": [],
            "hotcold": [],
            "color": [],
            "media": [],
            "posX": [],
            "posY": [],
            "posXend": [],
            "posYend": [],
            "fclass": [],
            "active": [],
            "ID_Study_Case":[]
        }
        mapconfig.data_notouch_zones = {
            "id": [],
            "x": [],
            "y": [],
            "w": [],
            "h": [],
            "name": [],
            "color": [],
            "ID_Study_Case":[]
        }
        mapconfig.souce_flux=None #init
        mapconfig.source_notouch_zones=None #init
        mapconfig.select_flux(int(solId)) #filling
        mapconfig.select_notouch_zones(int(solId)) #filling

        # Build bokeh models
        flux_map_res = flux_map.flux_map.build_flux_map_v2(config, mapconfig, solId)
        # flux_diag = build_flux_diag(list_lines, hotFlux, coldFlux, current_solution, ssFlux, exc, util)
        flux_diag_res = flux_diag.flux_diag.build_flux_diag(ssFlux, exc, util, config)

        # Get JS and HTML code
        script, divs = components({"flux_map": flux_map_res, "flux_diag": flux_diag_res})
        print(divs)
        sd = (
            script,
            divs["flux_map"],
            divs["flux_diag"],
            solId
        )

        print(sd)
        engine.execute("UPDATE solution SET script=?, div_flux_map=?, div_flux_diag=? WHERE id=?", sd)
           



    
def data_injector(id_study_case):
    ensFlux=[] #contient l'ensemble (ens) des flux

    pos_flux = {}

    query="SELECT number, name, hotcold, posX, posY, posXend, posYend, tempIn, tempOut, cp, rho, mu, muExp, lambda, lambdaExp, pressure, pressureExp, debVol, debVolExp  FROM flux_v2 WHERE ID_Study_Case ="+str(id_study_case)
    result = engine.execute(query)
    for row in result:
        # for (key, val) in row.items():
        #     pos_flux[key].append(int(val))
        f = Flux.Flux(row["hotcold"], row["tempIn"],row["tempOut"],row["cp"],row["rho"],row["mu"]*10**row["muExp"],row["lambda"]*10**row["lambdaExp"],row["pressure"]*10**row["pressureExp"],row["debVol"]*10**row["debVolExp"],row["name"])
        print("ensflux.append",row["hotcold"], row["tempIn"],row["tempOut"],row["cp"],row["rho"],row["mu"]*10**row["muExp"],row["lambda"]*10**row["lambdaExp"],row["pressure"]*10**row["pressureExp"],row["debVol"]*10**row["debVolExp"],row["name"])
        f.numero = row["number"]
        ensFlux.append(f)

        if row["hotcold"] == 'f':
            nf = - row["number"]
        else:
            nf = row["number"]
        pos_flux[nf] = {
            "posX": int(row["posX"]),
            "posY": int(row["posY"]),
            "posXend": int(row["posXend"]),
            "posYend": int(row["posYend"])
        }
            

    
    deltaTmin = 10
    return ensFlux, deltaTmin, pos_flux
            



    
        
