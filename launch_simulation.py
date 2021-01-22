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
import sys
from sqlalchemy import create_engine
from config import engine



anagreen_main.id_study_case=sys.argv[1] #transmit id_study_case

simulPID=process = os.getpid()
print('====================== simulPID='+str(simulPID))

(energydf, network_list, signaturestr, ranking_list, exchanger_computed_data) = anagreen_main.main() #Retrieve result from the simulation 


print('====================== signaturestr='+str(signaturestr))

# Make totals in solutions
solutions={}
for idx in range(0, energydf.shape[0]):
    networknum=int(energydf.iloc[idx]['networkNumber'])
    if networknum not in solutions.keys():
        solutions[networknum]={
            'networknum':networknum,
            'rank':0,
            'totalRecycledEnergy':0,
            'totalStoredEnergy':0,
            'CO2Savings':0,
            'score':0,
        }
    solutions[networknum]['totalRecycledEnergy']+=energydf.iloc[idx]['totalRecycledEnergy']
    solutions[networknum]['totalStoredEnergy']+=energydf.iloc[idx]['totalStoredEnergy']
    
# Sore them in a list
solution_list=[]
for (key,ele) in solutions.items():
    solution_list.append(ele)
 
# Sort list by rank and update rank
solution_list = sorted(solution_list, key=lambda solution_list: solution_list['totalRecycledEnergy'], reverse=True)
rank=1
for key in solution_list:
    key['rank']=rank
    rank+=1

 # sort by ID
solution_list = sorted(solution_list, key=lambda solution_list: solution_list['networknum'])    

# Insert in DB
engine.execute("DELETE FROM solution")
engine.execute("DELETE FROM sqlite_sequence WHERE name='solution'") # reset autoincrement id
for i in range(0, len(solution_list)):
    to_add = (
        solution_list[i]["rank"],
        solution_list[i]["totalRecycledEnergy"],
        solution_list[i]["totalStoredEnergy"],
        solution_list[i]["CO2Savings"],
        solution_list[i]["score"],
        0,
        0,
        0,
		sys.argv[1] #the study case ID
    )
    engine.execute("INSERT INTO solution (rank , savedEnergy, storedEnergy, CO2Savings, score, capex, opex, roi, ID_Study_Case) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", to_add)
    


# get network infos to store in DB
netwoks_list=[]
solution_num=1
for solution in network_list:
    group_num=1
    for group in solution:
        for flux in group:
            netwoks_list.append({
                'flux_id':flux.id,
                'groupe':group_num,
                'solution_id':solution_num,
				'id_study_case':sys.argv[1],
            })
        group_num+=1
    solution_num+=1


#Insert in DB
engine.execute("DELETE FROM network")
engine.execute("DELETE FROM sqlite_sequence WHERE name='network'") # reset autoincrement id
for i in range(0, len(netwoks_list)):
    to_add = (
        netwoks_list[i]["flux_id"],
        netwoks_list[i]["groupe"],
        netwoks_list[i]["solution_id"],
		netwoks_list[i]["id_study_case"]
    )
    engine.execute("INSERT INTO network (flux_id , groupe, solution_id,ID_Study_Case) VALUES(?, ?, ?, ?)", to_add)

for i in range(len(ranking_list)): #code to insert data processed by anagreen_main etc... each "i" corresponds to a subtable related to a single couple
    data_sol = {
        "solution_id": [],
        "flux_id": [],
        "groupe": []
    }
    highest_score=max(ranking_list[i]["Score"]) # get the highest score of exchanger ranking for the current couple of flux
    id_highest_score =ranking_list[i]["Score"].index(max(ranking_list[i]["Score"])) #get index of the highest score
    id_exch=ranking_list[i]["ID_Exchanger_Type"][id_highest_score] #get id of the exchanger with the highest score
    id_hotflux=ranking_list[i]["ID_Hot_Flux"][0] #id of the hot flux of the couple
    id_coldflux=ranking_list[i]["ID_Cold_Flux"][0] #id of the cold flux of the couple
    query="SELECT solution_id, flux_id, groupe FROM network WHERE flux_id ="+str(id_hotflux)+" OR flux_id="+str(id_coldflux)
    result=engine.execute(query)
    for row in result:
        for (key, val) in row.items():
            data_sol[key].append(val)
    for j in range(len(data_sol["solution_id"])): #for each solution id 
        if data_sol["flux_id"][j]==id_hotflux: #if it's the hotflux, we search the coldflux
            
            query="SELECT solution_id, flux_id, groupe FROM network WHERE flux_id ="+str(id_coldflux)+" AND groupe =" +str(data_sol["groupe"][j])+" AND solution_id ="+str(data_sol["solution_id"][j])
        elif data_sol["flux_id"][j]==id_coldflux: #if it's the coldflux, we search the hotflux
            query="SELECT solution_id, flux_id, groupe FROM network WHERE flux_id ="+str(id_hotflux)+" AND groupe =" +str(data_sol["groupe"][j])+" AND solution_id ="+str(data_sol["solution_id"][j])
        result=engine.execute(query)
        data_sol2 = { 
            "solution_id": [],
            "flux_id": [],
            "groupe": []
        }
        for row in result:
            for (key, val) in row.items():
                data_sol2[key].append(val)
        if len(data_sol2["solution_id"])==1: #the length of data_sol2 should be 1 because it's the second flux of a couple
            phi = 0
            h_global = 0
            price = 0
            S2 = 0
            index = 0
            for k in range(len(exchanger_computed_data[i])):
                if exchanger_computed_data[i][k][0]== id_exch: #get the index "k" of the exchanger id to take it as reference for further searches 
                    index= k

                    break
            if id_exch==1:
                    #when function return one single S, we name it S2 here, that's why there's no S1 for coaxial and tubular exchangers
                    phi =exchanger_computed_data[i][index][0][0] #Coaxial phi
                    h_global =exchanger_computed_data[i][index][0][1]
                    S2 =exchanger_computed_data[i][index][0][2]
                    price=exchanger_computed_data[i][index][0][5]
                
            elif id_exch==2:

                    phi =exchanger_computed_data[i][index][1][0] #tubular phi
                    h_global =exchanger_computed_data[i][index][1][1]
                    S2 =exchanger_computed_data[i][index][1][2]
                    price=exchanger_computed_data[i][index][1][5]
            else:
                print("PLATED NOT YET IMPLEMENTED")
                
                
    
            engine.execute("UPDATE network set ID_Exchanger_Type=?, Exchanger_Score=?, Phi = ?, h_global = ?, S2 = ?, Price = ? WHERE flux_id= ? AND groupe = ? AND solution_ID = ?",
            id_exch,
            highest_score,
            phi,
            h_global,
            S2,
            price,      
            data_sol["flux_id"][j],
            data_sol["groupe"][j],
            str(data_sol["solution_id"][j])
            )
        elif len(data_sol2["solution_id"])>1: #if data_sol2 contains more than one entry,
            #it means there were something wrong because in each solution, one flux has only one other  flux in its couple
            print("Inconsistent result")


          
engine.execute("VACUUM")




#save solution result in history
query="SELECT value FROM configuration WHERE name = 'history_id'"
result = engine.execute(query).fetchone()
history_id = str(result[0])

save_solution={}
query="SELECT * FROM network ORDER BY id"
result = engine.execute(query)
save_solution['network']=[]
for row in result:
    save_solution['network'].append(dict(row))
query="SELECT * FROM solution ORDER BY rank"
result = engine.execute(query)
save_solution['solution']=[]
for row in result:
    save_solution['solution'].append(dict(row))
        
        
compressed_solution=bz2.compress(json.dumps(save_solution).encode())
engine.execute("UPDATE history set solution=?, ID_Study_Case=? WHERE id=? AND parameters_sig=?",
    (compressed_solution,
     sys.argv[1],
    history_id,
    signaturestr))
