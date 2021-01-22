"""This module contains the view for the parametrization page.

We use the flask_wtf module to create a form (imported in forms.py). The form is rendered by passing the form object
to the template. When the user clicks the submit button, the form is submitted to the results page, which performs
the validation of the data (checking that the data matches expected format). If the data could not be validated,
the results page redirects the client to this page, where validation is re-run to get validation errors,
that are displayed alongside erroneous fields for convenience. """

import flask
import config

from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from flask import Blueprint
from flask_wtf import FlaskForm
from wtforms import SubmitField, FloatField, RadioField
from wtforms.validators import DataRequired
from sqlalchemy import create_engine
from config import engine



parametrization_bp = Blueprint('parametrization_page', __name__)


@parametrization_bp.route("/parametrization.html", methods=['GET', 'POST'])
def parametrization_page():
    # Create
    myform = create_new_param_form()

    # Get Fields object from the Form object. They are needed by the template.
    param_fields = {}
    for param_prog_name in config.PARAMETER_PROG_NAMES:
        param_fields.update({"min_input_" + param_prog_name: getattr(myform, "min_input_" + param_prog_name)})
        param_fields.update({"max_input_" + param_prog_name: getattr(myform, "max_input_" + param_prog_name)})
        param_fields.update({"weight_input_" + param_prog_name: getattr(myform, "weight_input_" + param_prog_name)})

    # If this page was loaded after a redirect from the results page, the "validate_on_submit" method reads the POSTed
    # form data and runs validation to get validation errors. Those are loaded in myform.
    if myform.validate_on_submit():
        return "<html>The results page could not validate your form but the parametrisation page sees no validation " \
               "errors, there seems to be a problem with the server.</html> "

    # Render template
    html = flask.render_template(
        'parametrization.html',
        resources=INLINE.render(),
        page_id=2,
        config=config,
        param_fields=param_fields,
        form=myform,
        parameters_disp_units=config.PARAMETER_DISPLAY_NAMES_UNITS,
        parameters_names=zip(config.PARAMETER_DISPLAY_NAMES, config.PARAMETER_PROG_NAMES)
    )
    return encode_utf8(html)


    
    
    
def create_new_param_form(*args, **kwargs):
    """Create and return a new parametrization form.

    First we declare a new class with the search_method and input fields, then we instantiate it and dynamically add
    fields corresponding to the parameter inputs, then we return the form object."""
    class ParametrizationForm(FlaskForm):
        search_method = RadioField(choices=[("genetic", "Genetic Algorithm"), ("exhaustive", "Exhaustive search")], default='exhaustive')
        submit = SubmitField('Lancer la simulation')


    # link to DB
    # loading parametrization parameters
    query="SELECT * FROM parametrization ORDER BY id"
    result = engine.execute(query)
    parametrization={}
    for row in result:
        parametrization[row['name']]=row['value'] 
    ParametrizationForm.fields = {}
    
    param_tpinch_defval=10
    if "param_tpinch" in parametrization:
        param_tpinch_defval=parametrization["param_tpinch"]
    setattr(ParametrizationForm, "param_tpinch", FloatField(validators=[DataRequired()], default=param_tpinch_defval))

    for param_prog_name in config.PARAMETER_PROG_NAMES:
        min_defval=5
        max_defval=5
        weight_defval=1
        if param_prog_name=="Energysaved":
            max_defval=100000
        if param_prog_name=="C02savings":
            max_defval=1000
        if param_prog_name=="CAPEX":
            max_defval=1000000
        if param_prog_name=="ROI":
            max_defval=100000
        if param_prog_name=="Operationalcosts":
            max_defval=5
       
        if "min_input_" + param_prog_name in parametrization:
            min_defval=parametrization["min_input_" + param_prog_name]
            max_defval=parametrization["max_input_" + param_prog_name]
            weight_defval=parametrization["weight_input_" + param_prog_name]
    
        setattr(ParametrizationForm, "min_input_" + param_prog_name, FloatField(validators=[DataRequired()], default=min_defval))
        setattr(ParametrizationForm, "max_input_" + param_prog_name, FloatField(validators=[DataRequired()], default=max_defval))
        setattr(ParametrizationForm, "weight_input_" + param_prog_name, FloatField(validators=[DataRequired()], default=weight_defval))

    return ParametrizationForm(*args, **kwargs)
