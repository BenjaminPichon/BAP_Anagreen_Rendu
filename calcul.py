# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 10:13:04 2018

@author: nicolamartin
"""
### NMA

from sqlalchemy import create_engine
from config import engine
import pandas as pd
import numpy as np
import time

# This portion of the code will let you compute several quantities on the raw sensor data


# read data from the DB
nflux = engine.execute("SELECT count(*) FROM flux")
nflux = nflux.fetchone()[0]
# print("nflux is"+str(nflux))

# temporary fix because nflux counting is wrong
nflux=5
df = pd.read_sql_query("SELECT * FROM raw_TS", engine)

for id_ in range(1,nflux) :
    # print(id_)
    # compute delta temp
    dIn   = df.tempIn[df.flux_id==id_]
    dOut  = df.tempOut[df.flux_id==id_]
    deltaT = dIn - dOut
    # write the delta in the corresponding column
    df.loc[df['flux_id']==id_, 'DT'] = deltaT

# df.to_sql('DT', con=engine, if_exists='replace')


def wait_results():
    time.sleep(900)
    return

#result = engine.execute(query,(id))
#    data_flux = {
#        "tempOut": [],

#        "step"    : []
#    }
#   query="SELECT tempOut, step FROM sensor_output WHERE flux_id=?"
#    for row in result:
#        data_flux["tempOut"].append(row[0])
#        data_flux["step"].append(row[1])
 
#    data_tempout = {
#        "x": data_flux["step"],
#        "y": data_flux["tempOut"],
#    }
    
#    souce_tempout = ColumnDataSource(data_tempout, name="name_souce_tempin") 

# write data in the DB

    ### NMA   