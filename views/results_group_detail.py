"""This module contains the view for the details of groups of the result page"""

import numpy as np
import config
import json
import importlib
import flask

from bokeh import events
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, tools, TableColumn, DataTable, PreText, CustomJS, ImageURL, \
    CDSView, GroupFilter, BoxEditTool, PointDrawTool
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from flask import Blueprint
from sqlalchemy import create_engine
from config import engine

results_group_detail_bp = Blueprint('results_group_detail_bp', __name__)

@results_group_detail_bp.route("/")
@results_group_detail_bp.route("/results_group_detail.html")
def index_page():


    id = flask.request.args['id']
    resultid = flask.request.args['resultid']

    # Get JS and HTML code
    # script, divs = components({"flux_map": flux_map})
    json_data = json.dumps({
        "id": id,
    })
                            
    # Render template
    html = flask.render_template(
        'results_group_detail.html',
        page_id=3,
        config=config,
        id=id,
        resultid=resultid,
        json_data=json_data,
    )
    return encode_utf8(html)

    
 
 