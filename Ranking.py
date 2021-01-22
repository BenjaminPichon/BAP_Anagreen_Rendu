# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 11:57:40 2018

@author: sbouaraba
"""

#TESTS EXCEL 
import numpy as np
import pandas as pd
#import xlutils.copy
import openpyxl
from pandas import ExcelWriter
from pandas import ExcelFile
import config
from sqlalchemy import create_engine
from config import engine
import importlib

#def Choix_echangeur(Tc_e,Tf_e,Pc,Pf,DP):
#Tc_e et Tc_f les températures des fluides
#Pf et Pc Pression fluide froid et chaud
#DP pertes de charges maximal authorisés
#
class Ranking:
    
    def score(Tc_e,Tf_e,Pc,Pf,DP,Dc,Df,hotflux_id,coldflux_id):
        #Dc et Df en m^3/s


        data_exchanger = {
            "ID_Exchanger_Type": [],
            "Name": [],
            "Temp_Min": [],
            "Temp_Max": [],
            "Pmax_Tubes": [],
            "Pmax_Callandre": [],
            "Temp_Point": [],
            "P_Point": []
        }

        query="SELECT * FROM exchanger_type"
        result = engine.execute(query)
        for row in result:
            for (key, val) in row.items():
                data_exchanger[key].append(val)




##        file=pd.ExcelFile(r'Results.xlsx') 
##        df = pd.read_excel(file, sheet_name='Data')
########################### 
##        print("Column headings:")
##        print(df.columns)
##        print(df['Temperature Max'])
##
###########################
##        for i in df.index:
##            print(df['Temperature Max'][i])

#########################    

        #T_min = df['Temperature Min']
        #T_max = df['Temperature Max']
        #Pt_max = df['Pression Max tubes']
        #Pc_max = df['Pression Max callandre']
        T_min = data_exchanger['Temp_Min']
        T_max = data_exchanger['Temp_Max']
        Pt_max = data_exchanger['Pmax_Tubes']
        Pc_max = data_exchanger['Pmax_Callandre']
#        D_min = df['Debit min']
#        D_max = df['Debit max']
#    Compa_max= df['Compacite max']
#    Compa_min = df['Compacite min']
        T_point= np.zeros(len(T_min), dtype='d')
        Pf_point= np.zeros(len(T_min), dtype='d')
        Pc_point= np.zeros(len(T_min), dtype='d')
#        Df_point= np.zeros(10, dtype='d')
#        Dc_point= np.zeros(10, dtype='d')
        #for i in df.index:
       
        for i in range(len(T_min)): 
            if((T_min[i]<Tf_e) and (Tc_e<T_max[i])):
                T_point[i]=1

            if((Pf<Pt_max[i]) and (Pc<Pc_max[i])):
                Pc_point[i]=1

            if((Pc<Pt_max[i]) and (Pf<Pc_max[i])):
                Pf_point[i]=1
#    if((Dc<D_max[i]) and (Dc>D_min[i])):
#       Dc_point[i]=1             
#    if((Df<D_max[i]) and (Df>D_min[i])):
#       Df_point[i]=1  
        
###Calcul nb de point pour classement

        #Pond_T=df['Temperature point']
        #Pond_P=df['Pression point']
        Pond_T=data_exchanger['Temp_Point']
        Pond_P=data_exchanger['P_Point']
#        Pond_Q=df['Debit (m^3/s)'] 
        score= np.zeros(len(T_min), dtype='d')
        #for i in df.index:
        for i in range(len(T_min)):
            score[i]= T_point[i]*Pond_T[i] + Pc_point[i]*Pond_P[i] + Pf_point[i]*Pond_P[i] 
    #+Df_point[i]*Pond_Q[i]+Df_point[i]*Pond_Q[i]

        #for i in range(len(score)):
        #    print(score[i])

        #utility=df['Type echangeur']
        utility=data_exchanger['Name'] 
        #utility.name='Type echangeur'
        result ={
            "ID_Exchanger_Type": [],
            "ID_Hot_Flux": [],
            "ID_Cold_Flux": [],
            "Score": []
        }
        for i in range(len(utility)):
            print((utility[i],score[i]))
            result['ID_Exchanger_Type'].append(data_exchanger['ID_Exchanger_Type'][i])
            result['ID_Hot_Flux'].append(hotflux_id)
            result['ID_Cold_Flux'].append(coldflux_id)
            result['Score'].append(score[i])


        #s = pd.Series(score,name = 'score')
        #frames = [s,utility]
        #result = pd.concat(frames, axis=1)
        #test = result.sort_values(['score'], ascending=[False])
        #print(result)
        
        # ###Ouverture du fichier Excel pour écriture
        # file = R'Results.xlsx'
        # wb = openpyxl.load_workbook(filename=file)
        # G=range(0,len(test.index)-1)
        # print(G)
        # # Classement
        # sc = wb.get_sheet_by_name('Score')
        # for i in range(0,len(test.index)-1):
            # B='B'+str(i+3)
            # sc[B]=test.iloc[i][0]
            # C='C'+str(i+3)
            # sc[C]=test.iloc[i][1]
            
        # wb.save(file)
#    type=0
        return(result)
