# -*- coding: utf-8 -*-
"""
Created on 2018-07-25

This module is supposed to hold configuration options that are used throughout the app, but it is also currently
 used to define and share test data across the app.
"""
 
import os
import glob
import hashlib
import bz2
from bokeh.models import ColumnDataSource
from sqlalchemy import create_engine

# Database connection using SQLAlchemy (DB abstraction)
# http://docs.sqlalchemy.org/en/latest/core/engines.html#sqlite
# "from config import engine" to use it in the program
engine = create_engine('sqlite:///anagreen.sqlite')

#Variable contening the root path of the projet, useful for the upload method of the map
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

 ###################### BEGINNING OF CLASS ##################################

class CaseConfig:

        # will contain flux from DB
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
            "fclass": [],
            "active": [],
            "ID_Study_Case":[]
        }

        data_notouch_zones = {
            "id": [],
            "x": [],
            "y": [],
            "w": [],
            "h": [],
            "name": [],
            "color": [],
            "ID_Study_Case":[]
        }

     
        def __init__(self):
            self.source_notouch_zones = None
            self.souce_flux = None
            self.case_id = 0
            self.case_name = ""
            self.case_company = ""
            self.path_to_map = ""
       
             
        def setValues(self, id_study_case):
            self.case_id = id_study_case
            study_cases = { #array that will be displayed as a table in index
                    "ID_Study_Case":[],
                    "Name": [],
                    "Path_to_plan":[],
                    "company_name": []
                    }
            query = "SELECT ID_Study_Case, Name, Path_to_plan, company_name FROM study_case WHERE ID_Study_Case = " +str(id_study_case)
            result = engine.execute(query)
            for row in result:
                    for (key, val) in row.items():
                            study_cases[key].append(val)
            
            for step in range(len(study_cases["ID_Study_Case"])):
                    self.case_name = study_cases["Name"][step]
                    self.path_to_map = study_cases["Path_to_plan"][step]
                    self.case_company = study_cases["company_name"][step]
                            
        def select_flux(self, id_study_case): #search flux and fills the DataSource for bokeh map
                query="SELECT id, name , hotcold, color, media, posX, posY, posXend, posYend, fclass, active, ID_Study_Case FROM flux WHERE ID_Study_Case ="+str(id_study_case)+" ORDER BY name COLLATE NOCASE"
                result = engine.execute(query)
                for row in result:
                    for (key, val) in row.items():
                        self.data_flux[key].append(val)
                self.souce_flux = ColumnDataSource(self.data_flux, name="name_souce_flux")

        def select_notouch_zones(self, id_study_case): #search notouch zones and fills the DataSource for bokeh map
                query="SELECT id, x, y, w, h, name, color, ID_Study_Case FROM notouch_zone WHERE ID_Study_Case ="+str(id_study_case)+" ORDER BY name COLLATE NOCASE"
                result = engine.execute(query)
                for row in result:
                        for (key, val) in row.items():
                                self.data_notouch_zones[key].append(val)

                self.source_notouch_zones = ColumnDataSource(self.data_notouch_zones, name="name_souce_notouchezone")

        def generate_ColumnDataSource_flux(self, title):
            return ColumnDataSource(self.data_flux, name="bokeh_souce_flux_"+title)
            

        #def get_data_source_flux_end(self):
            #return ColumnDataSource(self.data_flux)



 
 ############################ END OF CLASS ####################################
         
 
 
# minimum size for zones 
MIN_ZONE_SIZE_W = 0.5
MIN_ZONE_SIZE_H = 0.5
 
"""Parameter names to be used as string keys of dictionnaries. Thoses dictionnary will be used for passing data to 
CustomJS functions. Therefore, the strings here should not be the string representation of a number, or contain 
spaces, so as to avoid syntax errors from javascript."""
PARAMETER_PROG_NAMES = [
    "Energysaved",
    "C02savings",
    "CAPEX",
    "ROI",
    "Operationalcosts"
]
PARAMETER_DISPLAY_NAMES = [
    "Puissance echangée",
    "CO2 évités (kt eq CO2)",
    "CAPEX",
    "ROI",
    "Cout des opérations"
]
PARAMETER_DISPLAY_NAMES_UNITS = {
    "Energysaved" : "Puissance échangée (kW)",
    "C02savings" :"CO2 évités (kt eq CO2)",
    "CAPEX" : "CAPEX (Euros)",
    "ROI" : "ROI (Years)",
    "Operationalcosts" : "Coût des opérations (Euros/an)" ,
}


# map picture => 11 pixels, 1 meter
# 1772 pixels width = 161.1 meters
# 1044 pixels height = 94.9 meters
#path_to_map = "plan-isidio-ag.jpg"
map_bottom_left_corner_location = {"x": 0, "y": 0}
map_upper_right_corner_location = {"x": 161.1, "y": 94.9}


''' useful functions '''

# return the index of the line where table['id'][index]==id
def get_index_by_id(id,table):
    result=-1
    print ("Table ID here : "+str(table['id']))
    for (index, val) in enumerate(table['id']):
        if val == id:
            result = index
    return result


# check scripts signature, to apprend to end of file to prevent cache if files changed
def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()
files_sig=''
listfiles=[]
listfiles += glob.glob("./static/js/*")
listfiles += glob.glob("./static/styles/*")
for files in listfiles:
    files_sig += sha256_checksum(files)
files_sig = hashlib.sha256(files_sig.encode('utf-8')).hexdigest()


# Calculate signature of input parameters and save them in save_parameters
def get_params_sig():
    signature=hashlib.sha256() # good practice: use sha2/3, sha1/md5 are not secure anymore
    save_parameters={}
    query="SELECT * FROM flux ORDER BY name"
    result = engine.execute(query)
    save_parameters['flux']=[]
    for row in result:
        save_parameters['flux'].append(dict(row))
        for (key, val) in row.items():
            signature.update((str(key)+str(val)).encode('utf-8'))
    query="SELECT * FROM notouch_zone ORDER BY name"
    result = engine.execute(query)
    save_parameters['notouch_zone']=[]
    for row in result:
        save_parameters['notouch_zone'].append(dict(row))
        for (key, val) in row.items():
            signature.update((str(key)+str(val)).encode('utf-8'))
    query="SELECT * FROM raw_TS ORDER BY id"
    result = engine.execute(query)
    save_parameters['raw_TS']=[]
    for row in result:
        save_parameters['raw_TS'].append(dict(row))
        for (key, val) in row.items():
            signature.update((str(key)+str(val)).encode('utf-8'))
    query="SELECT * FROM parametrization ORDER BY id"
    result = engine.execute(query)
    save_parameters['parametrization']=[]
    for row in result:
        save_parameters['parametrization'].append(dict(row))
        for (key, val) in row.items():
            signature.update((str(key)+str(val)).encode('utf-8'))
    signaturestr=signature.hexdigest()  
    return (signaturestr, save_parameters)
    

# We load the page empty, display a progress modal and make an ajax request to launch calculation and wait for result
query="SELECT value FROM configuration WHERE name = 'status'"
result = engine.execute(query).fetchone()
status = int(result[0])
