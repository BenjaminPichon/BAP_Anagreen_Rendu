"""This module contains the view for the details of the result page"""

import numpy as np
import math
import flask
from bokeh import events
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, tools, TableColumn, DataTable, PreText, CustomJS, ImageURL, \
    CDSView, GroupFilter, BoxEditTool, PointDrawTool, Label, Arrow, VeeHead
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from flask import Blueprint
from flask import Flask, session
import config
import json
import importlib
from sqlalchemy import create_engine
from config import engine

from views.results_graphs import flux_diag, flux_map

id_study_case = 0
mapconfig= config.CaseConfig() #object to configure map according with the study case (config.py)

results_detail_bp = Blueprint('results_detail', __name__)

@results_detail_bp.route("/")
@results_detail_bp.route("/results_detail.html")
def index_page():

    
    if session.get('gl_id_study_case', None) != None:
        id_study_case=session.get('gl_id_study_case', None)
    else:
        id_study_case = 0
    if int(id_study_case) > 0:
        mapconfig.setValues(int(id_study_case))
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
        mapconfig.select_flux(int(id_study_case)) #filling
        mapconfig.select_notouch_zones(int(id_study_case)) #filling
    solution = {
        "id": [],
        "rank": [],
        "savedEnergy": [],
        "capex": [],
        "roi": [],
        "opex": [],
        "CO2Savings": [],
        "score": [],
        "storedEnergy": []
    }
    query="SELECT id, rank, savedEnergy, capex, roi, opex, CO2Savings, score, storedEnergy  FROM solution ORDER BY rank"
    result = engine.execute(query)
    for row in result:
        for (key, val) in row.items():
            solution[key].append(val)

#--AA--
    hotFlux = {
        "id_flux": [],
        "number": [],
        "name": [],
        "hotcold": [],
        "tempIn": [],
        "tempOut": []
        }
    coldFlux = {
        "id_flux": [],
        "number": [],
        "name": [],
        "hotcold": [],
        "tempIn": [],
        "tempOut": []
        }
    query="SELECT id_flux, number, name, hotcold, tempIn, tempOut FROM flux_v2 WHERE ID_Study_Case = "+ str(id_study_case) +" AND hotcold = 'hot' ORDER BY number"
    result = engine.execute(query)
    for row in result:
        for (key, val) in row.items():
            hotFlux[key].append(val)
            
    query="SELECT id_flux, number, name, hotcold, tempIn, tempOut FROM flux_v2 WHERE ID_Study_Case = "+ str(id_study_case) +" AND hotcold = 'cold' ORDER BY number"
    result = engine.execute(query)
    for row in result:
        for (key, val) in row.items():
            coldFlux[key].append(val)

    ssFlux = {
        "id_ssflux": [],
        "numFlux": [],
        "numSsFlux": [],
        "typeFlux": [],
        "name": [],
        "Te": [],
        "Ts": [],
        }
    query="SELECT id_ssflux, numFlux, numSsFlux, typeFlux, name, Te, Ts FROM ssflux LEFT JOIN flux_v2 ON ssflux.numFlux = flux_v2.number AND ssflux.typeFlux = flux_v2.hotcold  WHERE id_solution = "+ str(solution["id"][0]) +" ORDER BY numFlux, numSsFlux"
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
        "perteChaud": [],
        "coutTotal": [],
        "longTuyau": [],
        "capexEch": [],
        "opexEch": [],
        "co2Ech": [],
        "ecoTotEch": [],
        "triEch": [],
        "vanEch": [],
        "ipEch": [] ,
        "surfEch": [] ,
        "nameF": [],
        "nameC": []        
        }
    # query="SELECT id_exchanger, numFluxF, numSsFluxF, numFluxC, numSsFluxC, type, puissE, cout, perteFroid, perteChaud,  coutTotal, longTuyau, capexEch, opexEch, co2Ech, ecoTotEch, triEch, vanEch, ipEch, name AS nameF" \
    #     +" FROM exchanger LEFT JOIN flux_v2 ON exchanger.numFluxF = flux_v2.number AND flux_v2.hotcold = 'f' WHERE id_solution = "+ str(solution["id"][0]) +" ORDER BY id_exchanger"
    query="SELECT id_exchanger, numFluxF, numSsFluxF, numFluxC, numSsFluxC, type, puissE, cout, perteFroid, perteChaud,  coutTotal, longTuyau, capexEch, opexEch, co2Ech, ecoTotEch, triEch, vanEch, ipEch, surfEch, ff.name AS nameF, fc.name AS nameC" \
        +" FROM exchanger LEFT JOIN flux_v2 AS ff ON exchanger.numFluxF = ff.number AND ff.hotcold = 'f' LEFT JOIN flux_v2 AS fc ON exchanger.numFluxC = fc.number AND fc.hotcold = 'c' WHERE id_solution = "+ str(solution["id"][0]) +" ORDER BY id_exchanger"
    result = engine.execute(query)
    for row in result:
        for (key, val) in row.items():
            exc[key].append(val)
            print(key, val)


    #tableau pour l'affichage des details des echangeurs dans le dashboard
    tabExc = []
    for i in range(len(exc["id_exchanger"])):
        tmp = []
        tmp.append(exc["id_exchanger"][i])
        tmp.append(exc["nameC"][i])
        tmp.append(exc["nameF"][i])
        tmp.append(format_number(exc["puissE"][i],5))
        tmp.append(exc["type"][i])
        tmp.append(format_number(exc["surfEch"][i],2))
        tmp.append(format_number(exc["coutTotal"][i],2) + " €")
        tmp.append(format_number(exc["longTuyau"][i],5))
        tmp.append(format_number(exc["capexEch"][i],2) + " €")
        tmp.append(format_number(exc["opexEch"][i],2) + " €")
        tmp.append(format_number(exc["triEch"][i],2) )
        tmp.append(format_number(exc["vanEch"][i],2) + " €")
        tmp.append(format_number(exc["ipEch"][i],2))
        tmp.append(format_number(exc["co2Ech"][i],8))
        tmp.append(format_number(exc["ecoTotEch"][i],2) + " €")

        tabExc.append(tmp)


    util = {
            
        "id_utility": [],
        "numFlux": [],
        "numSsFlux": [],
        "type": [],
        "puissE": []
        }
    query="SELECT id_utility, numFlux, numSsFlux,type, puissE FROM utility WHERE id_solution = "+ str(solution["id"][0]) +" ORDER BY id_utility"

    result = engine.execute(query)
    for row in result:
        for (key, val) in row.items():
            util[key].append(val)
    
    id = flask.request.args['id']

    # Load flux from DB
    current_solution = {
        "id": [],
        "rank": [],
        "savedEnergy": [],
        "capex": [],
        "roi": [],
        "opex": [],
        "CO2Savings": [],
        "score": [],
        "storedEnergy": []
    }

    
    # query="SELECT id, rank, savedEnergy, capex, roi, opex, CO2Savings, score, storedEnergy, capex_ech, capex_pompes, capex_tuyauterie, capex_etude, capex_install, capex_reglage, capex_admin, opex_pompes, opex_utilites, opex_maint, opex_entretien, opex_taxe, opex_assurance, opex_frais, kpi_mer, kpi_prctMer, kpi_nbUti, kpi_nbEch, kpi_enEch,  pincementF, pincementC  FROM solution  WHERE id=?"
    query="SELECT id, rank, savedEnergy, capex, roi, opex, CO2Savings, score, storedEnergy, capex_ech, capex_pompes, capex_tuyauterie, capex_etude, capex_install, capex_reglage, capex_admin, opex_pompes, opex_utilites, opex_maint, opex_entretien, kpi_mer, kpi_prctMer, kpi_nbUti, kpi_nbEch, kpi_enEch, kpi_puissEch,  pincementF, pincementC, script, div_flux_map, div_flux_diag  FROM solution  WHERE id=?"
    result = engine.execute(query,(id))
    current_solution = []
    for row in result:
        current_solution.append(dict(
        id=row["id"],
        rank=row["rank"],
        savedEnergy=row["savedEnergy"],
        capex=format_number(row["capex"],2),
        opex=format_number(row["opex"],2),
        CO2Savings=row["CO2Savings"],
        score=row["score"],
        roi=row["roi"], 
        capex_ech=format_number(row["capex_ech"],2),
        capex_pompes=format_number(row["capex_pompes"],2),
        capex_tuyauterie=format_number(row["capex_tuyauterie"],2),
        capex_etude=format_number(row["capex_etude"],2),
        capex_install=format_number(row["capex_install"],2),
        capex_reglage=format_number(row["capex_reglage"],2),
        capex_admin=format_number(row["capex_admin"],2),
        opex_pompes=format_number(row["opex_pompes"],2),
        opex_utilites=format_number(row["opex_utilites"],2),
        opex_maint=format_number(row["opex_maint"],2),
        opex_entretien=format_number(row["opex_entretien"],2),
        kpi_mer=format_number(row["kpi_mer"],5),
        kpi_prctMer=format_number(row["kpi_prctMer"] * 100,5),
        kpi_nbUti=row["kpi_nbUti"],
        kpi_puissEch=format_number(row["kpi_puissEch"],5),
        kpi_nbEch=row["kpi_nbEch"],
        kpi_enEch=format_number(row["kpi_enEch"]  / 1000,5),
        pincementC=row["pincementC"],
        pincementF=row["pincementF"],
        energieRequise=format_number(row["kpi_mer"] * (1 + row["kpi_prctMer"]),5),
        exchangers=tabExc))

        script = row["script"]
        div_flux_map = row["div_flux_map"]
        div_flux_diag = row["div_flux_diag"]
        
    json_data = json.dumps({
        "solution": solution,
    })

    
    
    #Si finalement le code de div_flux_map requiert qty_groups,linear_meters ou distance_all_lines,
    #ou encore des elements de json_data, c'est que trop de code a été refactorisé.
    #Il faudra reprendre des versions precedentes le code qui calcule ces valeurs
    html = flask.render_template(
        'results_detail.html',
        resources=INLINE.render(),
        page_id=3,
        config=config,
        script=script,
        json_data=json_data,
        current_solution= current_solution,
        div_flux_map=div_flux_map,
        div_flux_diag=div_flux_diag,
    )
    return encode_utf8(html)

#Transforme un nombre Val en chaine propice a l'affichage, avec les chiffres de la partie entiere par groupe de trois
#et la partie decimale arrondie a Rnd chiffres apres la virgule.
def format_number(val, rnd):
    euc = divmod(val, 1)

    tmpDec = str(round(euc[1], rnd))
    tmpEnt = euc[0]

    if(tmpDec[0] == "1"):
        tmpEnt += 1
        rnd = 0

    tmpEnt = str(tmpEnt)
        
    partDec = tmpDec[2:len(tmpDec)]
    partEnt = tmpEnt[0:-2]

    if rnd == 0:
        res = ""
    else:
        res = "." + partDec

    count = 0
    # print(euc, partEnt, partDec)
    for i in range(len(partEnt)):
        ii = len(partEnt) - i - 1
        if count == 3:
            count = 1
            res = partEnt[ii] + " " + res
        else:
            count += 1
            res = partEnt[ii] + res
    
    return res
            


    