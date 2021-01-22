"""This module contains the view for the details of the index page"""

import numpy as np
import flask
import config
import json
import importlib

from bokeh import events
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, tools, TableColumn, DataTable, PreText, CustomJS, ImageURL, \
    CDSView, GroupFilter, BoxEditTool, PointDrawTool
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from flask import Blueprint
from flask import Flask, session
from sqlalchemy import create_engine
from config import engine

id_study_case = 0
mapconfig= config.CaseConfig()
index_detail_bp = Blueprint('index_detail_bp', __name__)

@index_detail_bp.route("/")
@index_detail_bp.route("/index_detail.html")
def index_page():
    # Build bokeh models
    temperature_in_map = build_temperature_in()
    debit_map = build_debit()
    temperature_out_map = build_temperature_out()
    
    # Load flux from DB
    data_flux = {
        "id": [],
        "name": [],
        "hotcold": [],
        "color": [],
        "media": [],
        "posX": [],
        "posY": [],
        "posXend": [],
        "posYend": [],
        "fclass": []
    }
    
    id = flask.request.args['id']
    query="SELECT id, name , hotcold, color,  media, posX, posY, posXend, posYend, fclass FROM flux WHERE id=?"
    result = engine.execute(query,(id))
    for row in result:
        for (key, val) in row.items():
            data_flux[key].append(val)

    if session.get('gl_id_study_case', None) != None:
        id_study_case=session.get('gl_id_study_case', None)
    else:
        id_study_case = 0
    mapconfig.select_flux(int(id_study_case))
    mapconfig.select_notouch_zones(int(id_study_case))
    # Get JS and HTML code
    script, divs = components({"temperature_in_map": temperature_in_map,
                                "debit_map": debit_map,
                                "temperature_out_map": temperature_out_map})
    json_data = json.dumps({"data_flux": mapconfig.data_flux,
                            "data_notouch_zones": mapconfig.data_notouch_zones,
    })
    
    # Render template
    html = flask.render_template(
        'index_detail.html',
        resources=INLINE.render(),
        page_id=1,
        config=config,
        script=script,
        json_data=json_data,
        data_flux=data_flux,
        div_debit_map=divs["debit_map"],
        div_temperature_in_map=divs["temperature_in_map"],
        div_temperature_out_map=divs["temperature_out_map"],
    )
    return encode_utf8(html)
    
    
def build_temperature_in():

    id = flask.request.args['id']
    data_flux = {
        "tempIn": [],
        "timestamp"  : []
    }
    query="SELECT tempIn, timestamp FROM raw_TS LEFT JOIN time ON (raw_TS.time_id=time.id) WHERE flux_id=?"
    result = engine.execute(query,(id))
    for row in result:
            data_flux["tempIn"].append(row[0])
            data_flux["timestamp"].append(row[1])
    
    data_tempin = {
        "x": data_flux["timestamp"],
        "y": data_flux["tempIn"],
    }
    souce_tempin = ColumnDataSource(data_tempin, name="name_souce_tempin")    

    data_flux_out = {
        "tempOut": [],
        "timestamp"  : []
    }
    query="SELECT tempOut, timestamp FROM raw_TS LEFT JOIN time ON (raw_TS.time_id=time.id) WHERE flux_id=?"
    result = engine.execute(query,(id))
    for row in result:
            data_flux_out["tempOut"].append(row[0])
            data_flux_out["timestamp"].append(row[1])
    
    data_tempOut = {
        "x": data_flux_out["timestamp"],
        "y": data_flux_out["tempOut"],
    }
    souce_tempOut = ColumnDataSource(data_tempOut, name="name_souce_tempOut")   

    # Build tuple containing all the tools to use
    flux_map_tools = (
        "pan",                # pan/drag tools
        "wheel_zoom",                       # scroll/pinch tools
        "zoom_in", "zoom_out", "reset",     # actions
        "crosshair"    # inspectors
    )

    # Build figure
    temperature_in_map = figure(plot_width=700, plot_height=300, tools=flux_map_tools,  border_fill_color = "#F8F9FA", x_axis_label="time (Days)", y_axis_label="temperature (T°C)", title="Temperature")

    renderer2 = temperature_in_map.line(x='x', y='y', source=souce_tempin,  color='green',  name="scratter_dots",  legend="temperature in")
    renderer2out = temperature_in_map.line(x='x', y='y', source=souce_tempOut,  color='blue',  name="scratter_dots_out",  legend="temperature out")
    
    # put the click_policy afer adding plots/lines...
    temperature_in_map.legend.click_policy="hide"
    return temperature_in_map
    
    
    
def build_debit():

    id = flask.request.args['id']
    data_flux = {
        "flow": [],
        "timestamp"  : []
    }
    query="SELECT flow, timestamp FROM raw_TS LEFT JOIN time ON (raw_TS.time_id=time.id) WHERE flux_id=?"
    result = engine.execute(query,(id))
    for row in result:
            data_flux["flow"].append(row[0])
            data_flux["timestamp"].append(row[1])
    
    data_tempin = {
        "x": data_flux["timestamp"],
        "y": data_flux["flow"],
    }
    souce_flow = ColumnDataSource(data_tempin, name="name_souce_flow")    

    data_flux_out = {
        "tempOut": [],
        "timestamp"  : []
    }
    query="SELECT tempOut, timestamp FROM raw_TS LEFT JOIN time ON (raw_TS.time_id=time.id) WHERE flux_id=?"
    result = engine.execute(query,(id))
    for row in result:
            data_flux_out["tempOut"].append(row[0])
            data_flux_out["timestamp"].append(row[1])
    
    data_tempOut = {
        "x": data_flux_out["timestamp"],
        "y": data_flux_out["tempOut"],
    }
    souce_tempOut = ColumnDataSource(data_tempOut, name="name_souce_tempOut")   

    # Build tuple containing all the tools to use
    flux_map_tools = (
        "pan",                # pan/drag tools
        "wheel_zoom",                       # scroll/pinch tools
        "zoom_in", "zoom_out", "reset",     # actions
        "crosshair"    # inspectors
    )

    # Build figure
    temperature_in_map = figure(plot_width=700, plot_height=300, tools=flux_map_tools,  border_fill_color = "#F8F9FA", x_axis_label="time (Days)", y_axis_label="flow (m³.s⁻¹)", title="Flow")

    renderer2 = temperature_in_map.line(x='x', y='y', source=souce_flow,  color='green',  name="scratter_dots")
    
    # put the click_policy afer adding plots/lines...
    temperature_in_map.legend.click_policy="hide"
    return temperature_in_map
    
    
def build_temperature_out():
    id = flask.request.args['id']
    data_flux = {
        "timestamp"  : [],
        "tempOut": [],
        "tempIn": [],
        "tempDelta": [],
        "Cp"  : [],
        "flow"  : [],
        "energy"  : [],
    }
    query="SELECT timestamp, tempOut, tempIn, Cp, flow FROM raw_TS LEFT JOIN time ON (raw_TS.time_id=time.id) WHERE flux_id=?"
    result = engine.execute(query,(id))
    for row in result:
            data_flux["timestamp"].append(row[0])
            data_flux["tempOut"].append(row[1])
            data_flux["tempIn"].append(row[2])
            data_flux["tempDelta"].append(abs(row[1]-row[2]))
            data_flux["Cp"].append(row[3])
            data_flux["flow"].append(row[4])
            data_flux["energy"].append(abs(row[1]-row[2])*row[3]*row[4])
    
    data_energy = {
        "x": data_flux["timestamp"],
        "y": data_flux["energy"],
    }   

    average = np.mean(data_flux["energy"])
    standard_deviation  = np.std(data_flux["energy"])
    list_average=[]
    list_standard_deviation=[]
    list_standard_deviation_bot=[]
    for val in data_flux["timestamp"]:
        list_average.append(average)
        list_standard_deviation.append(average+standard_deviation)
        list_standard_deviation_bot.append(average-standard_deviation)
        
    # need reverse to draw the pach zone (we draw first top line then bottom line in reverse
    reversed_timestamps=list(reversed(data_flux["timestamp"]))
    reversed_list_standard_deviation_bot=list(reversed(list_standard_deviation_bot))
    
    data_average = {
        "x": data_flux["timestamp"],
        "y": list_average,
    } 
    data_standard_deviation = {
        "x": data_flux["timestamp"] + reversed_timestamps,
        "y": list_standard_deviation + reversed_list_standard_deviation_bot,
    }
    souce_energy = ColumnDataSource(data_energy, name="name_souce_tempOut")    
    souce_average = ColumnDataSource(data_average, name="name_souce__average")    
    souce_standard_deviation = ColumnDataSource(data_standard_deviation, name="name_souce_standard_deviation")    

    # Build tuple containing all the tools to use
    flux_map_tools = (
        "pan",                # pan/drag tools
        "wheel_zoom",                       # scroll/pinch tools
        "zoom_in", "zoom_out", "reset",     # actions
        "crosshair"    # inspectors
    )

    # Build 
    temperature_out_map = figure(plot_width=700, plot_height=300, tools=flux_map_tools,  border_fill_color = "#F8F9FA", x_axis_label="time (Days)", y_axis_label="energy (J)", title="Energy")

    renderer2 = temperature_out_map.patch(x='x', y='y', source=souce_standard_deviation,  color='#ddddff',  name="scratter_dots4",  legend="standard deviation")
    renderer2 = temperature_out_map.line(x='x', y='y', source=souce_energy,  color='green',  name="scratter_dots2",  legend="energy")
    renderer2 = temperature_out_map.line(x='x', y='y', source=souce_average,  color='orange',  name="scratter_dots3",  legend="average energy")
    
    # put the click_policy afer adding plots/lines...
    temperature_out_map.legend.click_policy="hide"
    return temperature_out_map
