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

help_bp = Blueprint('help_bp', __name__)

@help_bp.route("/")
@help_bp.route("/help.html")
def index_page():




    # Get JS and HTML code
    # script, divs = components({"flux_map": flux_map})
                 
    # Render template
    html = flask.render_template(
        'help.html',
        page_id=10,
        config=config,
        id=id,

    )
    return encode_utf8(html)

    
 