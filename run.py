"""This is the main script to run to launch the app."""



"""
How the code works:

First, read the wiki page that explain the project.

The database is the central element, it contains the simulation parameters (flux, firbidden area/zones, prameters data...), the simulation results, and configuration information.
For now, we use a SQLite datbase (useful for prototyping and local storage, it's a simple file like a configuraion/xml/json file and don't require a service to un), but in the future
it needs to be scaled to something else when more user and data will be processed.
SQLAlchemy is used so ther's not a lot of work to do (only need to correct specific things like removing VAcUUM only used in sqlite, and updating index)

Database updates are mainly done with AJAX requests (update a zone/flux position, press a button, ...)

The simulation iself is 2 ajax requests (section results_ajax of results.py)
- "wait_results" > will launch the simulation in a separate thread (PID is saved in DB)
- "progress_results" > will check simulation progress state (and manage eror/crash of it)

The simulation will then have a status:
- 0 > result cleared (new installation / Clear result clicked, or reset database clicked)
- 1 > calculation in progress
- 2 > calculation finished
- 3 > parameters have changed (so results doesn't match new parameters)
- 4 > error during simulation (look at the console details)



"""




import os.path
import flask
import sys
sys.path.append("./algorithmes_simulation")
from shutil import copyfile
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
#from flask import session
from flask import Flask, session
database_version='1.6'
application_version='1.0.1'


# there are two database, one model and one active. 
# when "reset" button is pressed, model is copied to active
# active is not stored in Git (update too frequently), so if it's not here, initialize with model (if the model is at the good version
# if active is outdated model is copied to active (if model is outdated, we exit with error)
if os.path.isfile("./anagreen.sqlite"):
    engine = create_engine('sqlite:///anagreen.sqlite', poolclass=NullPool)
    query="SELECT value FROM configuration WHERE name = 'version'"
    result = engine.execute(query).fetchone()
    result2=str(result['value'])
    engine.dispose()
    if database_version != str(result2):
        print('Database vesion obsolete, removing...')
        os.remove("./anagreen.sqlite") 


if not os.path.isfile("./anagreen.sqlite"):
    
    engine = create_engine('sqlite:///anagreen_modele.sqlite', poolclass=NullPool)
    query="SELECT value FROM configuration WHERE name = 'version'"
    result = engine.execute(query).fetchone()
    result2=str(result['value'])
    engine.dispose()
    if database_version != str(result2):
        print('Database synchro problem, version mismatch betweed code and database modele')
        sys.exit(1)
    else:
        copyfile("./anagreen_modele.sqlite", "./anagreen.sqlite")





from views.flux_detail import flux_detail_bp
from views.index import index_bp
from views.index import login_bp
from views.setup import setup_bp
from views.index_detail import index_detail_bp
from views.parametrization import parametrization_bp
from views.results import results_bp
from views.results_detail import results_detail_bp
from views.results_group_detail import results_group_detail_bp
from views.help import help_bp
from views.history import history_bp
from views.new_case import new_case_bp


app = flask.Flask(__name__)

app.config['SECRET_KEY'] = 'onVcG2UaW5EVdIvb8BTQd2PXCXA3Jo8YsK'
app.secret_key='onVcG2UaW5EVdIvb8BTQd2PXCXA3Jo8YsK'

"""A secret key is needed for flask-WTForms to generate CSRF tokens."""

"""The blueprint mechanism of flask is used to separate the codebase into separate modules. In this app, each view has
its own module, and each of them defines a blueprint that is used just as you'd use the "app" object (defining the
route of the view, for example). The "register_blueprint" method of "app" allows our app to integrate and serve the
views."""
app.register_blueprint(login_bp)
app.register_blueprint(index_bp)
app.register_blueprint(setup_bp)
app.register_blueprint(index_detail_bp)
app.register_blueprint(flux_detail_bp)
app.register_blueprint(parametrization_bp)
app.register_blueprint(results_bp)
app.register_blueprint(results_detail_bp)
app.register_blueprint(results_group_detail_bp)
app.register_blueprint(history_bp)
app.register_blueprint(help_bp)
app.register_blueprint(new_case_bp)


# Need to secure this with a token instead of storing the password
@app.before_request
def check_valid_login():
    login_valid = 'auth' in flask.request.cookies and flask.request.cookies['auth']=='anayellow'
    if(flask.request.endpoint and 
        'static' not in flask.request.endpoint and 
        not login_valid and 
        not flask.request.path == '/login.html'):
        return flask.redirect('login.html')


app.run(host='0.0.0.0', port=50007, debug=True)
