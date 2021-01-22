import flask
from sqlalchemy import create_engine
from config import engine


from flask import Blueprint
from flask import Flask

new_case_bp = Blueprint('new_case',__name__)

"""
@new_case_bp.route('/new_study_case.html', methods=['GET', 'POST'])
def newCase():
    if flask.request.method == 'POST':
        case = (
            flask.request.form['casename'],
            flask.request.form['company_name'],
            "",
        )
        engine.execute("INSERT INTO study_case (Name , company_name , Path_to_plan) VALUES(?,?,?)",case)
        return flask.render_template('setup.html')

    return flask.render_template('new_study_case.html')
"""


