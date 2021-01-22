# -*- coding: utf-8 -*-
"""
Created on Wed May 23 17:35:29 2018

@author: nicolamartin
"""

id_study_case=0
def main() :
    print ("je suis appelé")

    # Always import sys because it is needed everywhere
    import sys
    import copy 
    import os
    import pandas as pd 
    import numpy as np
    sys.path.append('./toolkit/')
    import class_ as cl
    import functions as fct
    import time
    import config
    from sqlalchemy import create_engine
    from config import engine
    import importlib
    import Ranking
    import Echangeurs

    # =============================================================================
    # Read data from database
    # =============================================================================
    
    
    # load param_sig
    (signaturestr, save_parameters)=config.get_params_sig()
    
    # loading parametrization parameters
    query="SELECT * FROM parametrization ORDER BY id"
    result = engine.execute(query)
    parametrization={}
    for row in result:
        parametrization[row['name']]=row['value']
        
    # Load in variable
    Tpinch_param = int(parametrization['param_tpinch'])
    
    
    # count number of flux
    nbrFluxHot  = engine.execute("SELECT count(*) FROM flux WHERE hotcold = 'hot' AND ID_Study_Case =" +str(id_study_case))
    nbrFluxHot  = nbrFluxHot.fetchone()[0]
    nbrFluxCold = engine.execute("SELECT count(*) FROM flux WHERE hotcold = 'cold' AND ID_Study_Case =" +str(id_study_case))
    nbrFluxCold = nbrFluxCold.fetchone()[0]
    nflux = engine.execute("SELECT count(*) FROM flux WHERE ID_Study_Case =" +str(id_study_case))
    nflux = nflux.fetchone()[0]
    
    print("Number of cold flux is : "+str(nbrFluxCold))
    print("Number of hot flux is : "+str(nbrFluxHot))
    print("Total number of flux is : "+str(nflux))
    
    query="SELECT flux_id, tempIn, timestamp FROM raw_TS LEFT JOIN time ON (raw_TS.time_id=time.id)"
    
    df_temp = pd.read_sql_query(query, engine)
    
    #%%
    # Create flux object from df
    
    fluxIndexList = pd.read_sql_query("SELECT id FROM flux WHERE ID_Study_Case =" +str(id_study_case), engine).values.flatten().tolist()
    lflux = []
    for id_ in fluxIndexList :
        ff = cl.flux(
                id=id_, 
                name=engine.execute('SELECT name FROM flux WHERE id={}'.format(id_)).fetchone()[0], 
                exchanger="ech1", 
                type=engine.execute('SELECT media FROM flux WHERE id={}'.format(id_)).fetchone()[0], 
                timeserieIn=pd.read_sql_query("SELECT tempIn FROM raw_TS LEFT JOIN time ON (raw_TS.time_id=time.id) WHERE flux_id={}".format(id_), engine).values.flatten().tolist(), 
                timeserieOut=pd.read_sql_query("SELECT tempOut FROM raw_TS LEFT JOIN time ON (raw_TS.time_id=time.id) WHERE flux_id={}".format(id_), engine).values.flatten().tolist(),
                pressure=pd.read_sql_query("SELECT Pression FROM raw_TS LEFT JOIN time ON (raw_TS.time_id=time.id) WHERE flux_id={}".format(id_), engine).values.flatten().tolist(),
                d=pd.read_sql_query("SELECT D FROM raw_TS LEFT JOIN time ON (raw_TS.time_id=time.id) WHERE flux_id={}".format(id_), engine).values.flatten().tolist(),
                sensor=["capt1","capt2"],
                hotCold=engine.execute('SELECT hotcold FROM flux WHERE id={}'.format(id_)).fetchone()[0],
                flow=pd.read_sql_query("SELECT flow FROM raw_TS LEFT JOIN time ON (raw_TS.time_id=time.id) WHERE flux_id={}".format(id_), engine).values.flatten().tolist(),  
                Cp=pd.read_sql_query("SELECT Cp FROM raw_TS LEFT JOIN time ON (raw_TS.time_id=time.id) WHERE flux_id={}".format(id_), engine).values.flatten().tolist()
                )
        lflux.append(ff)
    lfluxHot=[]
    lfluxCold=[]
    
    for flux in lflux :
        if flux.hotCold == 'hot' :
            lfluxHot.append(flux)
        elif flux.hotCold == 'cold' :
            lfluxCold.append(flux)
        else:
            print("Type of flux not understood : "+str(flux.hotCold))
            sys.exit(1)
    if len(lfluxCold) +len(lfluxHot) != len(lflux):
        print("Flux must be either hot or cold")
        sys.exit(1)
    
    #%%
    # =============================================================================
    # Set user Variables
    # =============================================================================
    
    pid=os.getpid()
    engine.execute("UPDATE configuration SET value = ? WHERE name = 'current_simulation_pid'",(pid))
    engine.execute("UPDATE configuration SET value = 1 WHERE name = 'status'")
    importlib.reload(config)
    print('SET SIMUL STATUS=1')
    print('SET SIMUL PID='+str(pid))
    
    verbose = True
    logfile = False
    logFileName = 'output_anagreen_main.txt'
    
    Tpinch = Tpinch_param
    
    if logfile == True :
        sys.stdout = open(logFileName, 'w', encoding='utf8')
    
    
    #%%
    # =============================================================================
    # create all system configurations
    # =============================================================================
    
    network_list = fct.generate_networks(lfluxHot, lfluxCold)
    ranking_list = []
    exchanger_computed_data = []
    # =============================================================================
    # 2 ANALYSES DES FLUX
    # =============================================================================
    
    # TODO : implement flexible numsteps 
    
    minNumStep = 10000
    for flux in lflux : 
        if (len(flux.timeserieIn) == 0) or (len(flux.timeserieOut) == 0) : 
            print("Missing value in the temp TS of flux {}".format(flux.name))
            sys.exit(0)
        if len(flux.timeserieIn) < minNumStep :
            minNumStep = len(flux.timeserieIn)
        elif len(flux.timeserieOut) < minNumStep :
            minNumStep = len(flux.timeserieOut)
            
    
    numSteps = minNumStep
    
    energydf         = pd.DataFrame(columns=[])
    wrongWayExchange = list()
    QList            = list()
    costList         = list()
    
    for currStep in range(numSteps) :
        # Write progress into database so it is displayed onto the screen
        progress = (currStep+1) / numSteps *100
        # not secured way of doing it
        engine.execute("UPDATE configuration SET value = {} WHERE name = 'progress'".format(progress))
        # time.sleep(3*3)
        print(progress)
        
        if verbose == True :
            print("####################")
            print("       STEP "+str(currStep))
            print("####################")
        step = currStep
        
        lflux_shifted = fct.shift_temp(lflux, Tpinch)
        nchaud, nfroid = fct.compute_nflux(lflux)
        temp_list = fct.make_temp_list(lflux_shifted, step)
        
        # compute cascade 
        casc, MER = fct.compute_cascade(lflux_shifted, step=step, verbose=True)
        # plot cascade
    #    fct.plot_cascade(casc, temp_list)
        
        cold_utility = casc[-1]
        hot_utility  = casc[0]
        if verbose == True :
            print("L'utilite froide est de : {} KW".format(cold_utility))
            print("L'utilite chaude est de : {} KW".format(hot_utility))
            print("Le minimum d'energie requis (MER) est de : {} KW".format(MER))
        # print("L'énergie totale récupérable ou exergie est : {} KW".format(casc))
    
        # =============================================================================
        # Analyse the recycled or stored energy for all the created HEN
        # =============================================================================
    
        # Loop over all networks
        cpeau            = 4180
        i= 0
        for hen_id, hen in enumerate(network_list) :

            totalRecycledEnergy         = 0
            totalStoredEnergy           = 0
            totRecycledEnergyFromStorage   = 0
            storedEnergy = 0
            if verbose == True :
                print("======================= \nProcessing Network #{}# \n=======================".format(hen_id))
            # loop over each couple of flux
            for couple in hen :
                hotFlux = next((i for i in couple if i.hotCold =='hot'), None)
                coldFlux = next((i for i in couple if i.hotCold =='cold'), None)
                if verbose == True :
                    print("==> Assessing the exploitability of the couple : {} - {}".format(couple[0].name,couple[1].name))
                # Computing Qf and QC
                Thi = hotFlux.timeserieIn[step]
                Tho = hotFlux.timeserieOut[step]
                deltaTCoupleHot = Thi - Tho
                Qh =  deltaTCoupleHot * hotFlux.Cp[step] # TODO Cp = cp x flow NOT IMPLEMENT SO FAR
                Cp_f = coldFlux.Cp[step]
                Cp_c = hotFlux.Cp[step]
                Tci = coldFlux.timeserieIn[step]
                Tco = coldFlux.timeserieOut[step]
                deltaTCoupleCold = Tco - Tci
                Pc = hotFlux.pressure[step]
                Pf = coldFlux.pressure[step]
                Dc = hotFlux.d[step]
                Df = coldFlux.d[step]
                i = i + 1
                #### CODE ECHANGEUR ####

                
                #### PROVISOIR : on prend que la 5e température de sortie de chaque flux (état actuel : 5 lignes de température par flux dans raw_TS) ####
                #### Si on prend toutes les températures, la ranking list va faire 90 entrées pour un cas d'étude de 6 flux, aulieu de 18 (car 18*5=90) ####
                print("############ EXCHANGER FUNCTION #########################")
                if step == (numSteps-1):
                    print("############ RANKING###################################")
                    print((couple[0].id,couple[1].id))
                    resultRanking = Ranking.Ranking.score(Tho,Tco,Pc,Pf,10000,Dc,Df,couple[0].id,couple[1].id)
                    ranking_list.append(resultRanking)
                    print("############ END RANKING###################################")
                    tab_data_exch=[]
                    for id_exch in resultRanking["ID_Exchanger_Type"]:
                        if id_exch == 1: #coaxial
                            data_Exch=Echangeurs.Echangeurs.Coaxial(Dc,Df,Cp_c,Cp_f,Thi,Tho,Tci,Tco)
                            tab_data_exch.append((1,data_Exch))
                        elif id_exch == 2: #tube
                            data_Exch=Echangeurs.Echangeurs.Tubular(Dc,Df,Cp_c,Cp_f,Thi,Tho,Tci,Tco)
                            tab_data_exch.append((2,data_Exch))
                        #else: #plated
            
                            #data_Exch=Echangeurs.Echangeurs.Plated()

                            #left to implement
                        

                        
                    exchanger_computed_data.append(tab_data_exch)
                    
                    
                print("############ END EXCHANGER FUNCTION #########################")
                Qc =  deltaTCoupleCold * coldFlux.Cp[step]
                QList.append([step, hen_id, str(couple[0].name+"-"+couple[1].name), Qc, Qh])
                if verbose == True :
                    print ("==++> Qh : {}".format(Qh))
                    print ("==++> Qc : {}".format(Qc))
                # studying different cases based on Qh and Qc diff
                if np.abs(Thi-Tci) < Tpinch : # test OK needs to take absolute value so we can proceed with other tests
                    print("WARNING: difference of temperature ({}) between the two flux is bellow the pinch ({} deg)".format(np.abs(Thi-Tci), Tpinch))
                    print("WARNING: no energy will be recycled.")
                    recycledEnergy = 0
                    # intervention d'une PAC possible ici  
                else :
                    #Test OK
                    if Thi < Tci : # risk of exchanging in the wrong direction
                        print ("WARNING: heat exchange going is the wrong direction.")
                        wrongWayExchange.append([step, hen_id, 1])
                        recycledEnergy = 0
                    else :
                        #Test OK
                        if Qh < 0 :
                            print("WARNING: Flux {} inexploitable.".format(hotFlux.name))
                            print("WARNING: Qh ({}) < 0".format(Qh))
                            recycledEnergy = 0
                        #Test OK
                        elif Qc < 0 :
                            print("WARNING: Flux {} inexploitable.".format(coldFlux.name))
                            print("WARNING: Qc ({}) < 0".format(Qc))
                            # Consider possibility to improve. Change into hot flux and store or recycle energy. 
                            recycledEnergy = 0
                        #TEST TODO
                        if Qc >= Qh : # means that there is more need of cold than there is of heat offer 
                            print("Qc >= Qh")
                             # all the energy can be directly recycled without need for storage
                             # BUT the energy left Qc - Qh is a need which is not satisfied
                             # thereforer it should be takin into storage or added as a cost
                            recycledEnergy = Qh
                            # if storage is empty add as a cost
    #                        if storedEnergy >= Qc-Qh :
    #                            recycledEnergyFromStorage = Qc-Qh
                            # if storage as enough energy take from storage and update storage
    #                        else :
    #                            costList.append = [step, hen_id, Qc-Qh]
                            
                        elif Qc < Qh : # means that there is more heat offer than there is cold need => potential storage
                            print("Qc < Qh")
                            recycledEnergy = Qc
                            storedEnergy   = Qh - Qc # only the remaining energy is eligible for storage
                totalRecycledEnergy             += recycledEnergy
                totalStoredEnergy               += storedEnergy
    #            totRecycledEnergyFromStorage    += recycledEnergyFromStorage
            if verbose == True :
                print("The total amount of saved energy for this HEN of flux is : {}".format(totalRecycledEnergy))
                print("The total amount of stored energy for this HEN of flux is : {}".format(totalStoredEnergy))
            # fill the dataframe with freshly computed results
            temp = pd.DataFrame([{"step" : step, "MER" : MER , "networkNumber": hen_id, 
                                  "totalRecycledEnergy": totalRecycledEnergy,
                                  "totalStoredEnergy": totalStoredEnergy,
                                  "totRecycledEnergyFromStorage" : totRecycledEnergyFromStorage,
                                  "MER" : MER}])
            energydf = energydf.append(temp, ignore_index=True)
    #        savedEnergyList.append([hen_id, totalRecycledEnergy])
    
    # sort on the HEN number so it is easier to read
    energydf = energydf.sort_values('networkNumber')
    
    # Create a DF out of a list for easier visualisation
    Qdf                = pd.DataFrame(columns=['step', 'hen_id', 'couple', 'Qc', 'Qh'], data=QList)
    wrongWayExchangedf = pd.DataFrame(columns=['step', 'HENID' ,'wrongWayExchangeNumber'], data=wrongWayExchange)
    
    
    # get the total saved energy per HEN and stores it into a dataframe. 
    # this is only done for convenient printing.
    totSavedEnergyPerHendf = pd.DataFrame(columns=["HEN number", "TotalSavedEnergy" ])
    
    # =============================================================================
    #  WHAT TO DO WHEN ALGO DONE
    # =============================================================================
    
    
    # look in run.py for values of status
    engine.execute("UPDATE configuration SET value = 2 WHERE name = 'status'")
    importlib.reload(config)
    
    

#    for hen in range(len(network_list)) :
#        totalSavedEnergy = savedEnergydf.savedEnergy[savedEnergydf.networkNumber==hen].sum()
#        temp = [{"HEN number" : hen, "TotalSavedEnergy" : totalSavedEnergy}]
#        totSavedEnergyPerHendf = totSavedEnergyPerHendf.append(temp)
#    
    #print(tabulate(totSavedEnergyPerHendf, headers='keys', tablefmt='psql'))
    ## =============================================================================
    ## Compute stored energie
    ## we consider that each couple of flux can store energy and that when storage
    ## is empty then it should be added as a cost. Nevertheless when the storage is
    ## used we can consider this energy as recycled energy, which should be added to
    ## the corresponding sum in the 
    ## =============================================================================
    #hendf = pd.DataFrame(columns=["step","networkNumber", "fluxCouple", "currStorage", "energyCost", "recycledEnergyFromStorage"])
    #for idHen, hen in enumerate(network_list) :
    #    print("# Studiyng network nbr #"+str(idHen))
    #    for idCouple, couple in enumerate(hen) :
    #        print("# # Studiyng couple nbr #"+str(idCouple))
    #        prevStorage = 0
    #        currStorage = 0
    #        energyCost  = 0
    #        # find whose hot or cold in the couple studied
    #        for currStep in range(numSteps) :
    #            print("# # # Studiyng step nbr #"+str(currStep))
    #            print("temp chaude flux chaud "+str(couple[0].timeserieIn[currStep]))
    #            print("temp froide flux chaud "+str(couple[0].timeserieOut[currStep]))
    #            print("temp chaude flux froid"+str(couple[1].timeserieIn[currStep]))
    #            print("temp froide flux froid "+str(couple[1].timeserieOut[currStep]))
    #
    #            # probably need to be implemented the check that DT hot correspond to hot flux 
    #            deltaTHot  = couple[0].timeserieIn[currStep] - couple[0].timeserieOut[currStep] 
    #            deltaTCold = couple[1].timeserieOut[currStep] - couple[1].timeserieIn[currStep]
    #            print("Delta hot "+str(deltaTHot))
    #            print("Delta cold "+str(deltaTCold))
    #            # here is missing the possibility to have a varying Cp or flow
    #            # one just needs to add [currStep] to take it into account
    #            Qh = deltaTHot * couple[0].flow * couple[0].Cp
    #            Qc = deltaTCold  * couple[1].flow * couple[1].Cp
    #            print("Qh "+str(Qh))
    #            print("Qc "+str(Qc))
    #            DQ = Qh - Qc
    #            print("DQ "+str(DQ))
    ##            currStorage = DQ + prevStorage
    ##            print("currStorage :"+str(currStorage))
    ##            prevStorage = currStorage
    #            if  prevStorage + DQ < 0 : # has to be a + cause DQ is neg when consuming energy
    #                # There is not enough in the storage
    #                # Take all the energy available and mark the rest as cost
    #                print("info: not enough in storage")
    #                print("info: Current storage is {}".format(currStorage))
    #                print("info: Required energy is {}".format(DQ))
    #                energyCost = np.abs(DQ) - prevStorage
    #                recycledEnergyFromStorage = prevStorage
    #                # since we took all the energy back we set currStorage to 0
    #                currStorage = 0
    #            elif prevStorage + DQ >= 0 :
    #                print("info: enough energy in storage")
    #                print("info: Current storage is {}".format(currStorage))
    #                print("info: Required energy is {}".format(DQ))
    #                print("info: recycled energy is {}".format(DQ))
    #                recycledEnergyFromStorage = np.abs(DQ)
    #                currStorage = prevStorage + DQ
    #            else :
    #                print("ALERT: A problem occured while computing the storage state.")
    #            temp =  pd.DataFrame([{"step" : currStep, "networkNumber" : idHen, "fluxCouple" : couple, "currStorage" : currStorage, "energyCost" : energyCost, "recycledEnergyFromStorage" : recycledEnergyFromStorage}])
    #            hendf = hendf.append(temp)
    #
    #TotalStoragePerHen = []
    #for idHen in range(len(network_list)) : 
    #    TotalStoragePerHen.append([idHen,hendf[hendf.networkNumber==idHen].currStorage.tolist()[-1]]) 
    #    
    #def plot_storage_hen(hendf, nbrOfHen) :
    #    f, ax = plt.subplots()
    #    for henId in range(nbrOfHen) :
    #        data = hendf[hendf.networkNumber==henId].currStorage.reset_index(drop=True)
    #        ax.plot(data, label='HEN #{}'.format(henId))
    #        plt.title("Current energy stored")
    #        plt.ylabel("Energy")
    #        plt.xlabel("Step")
    #        plt.legend()
    #    f, ax = plt.subplots()
    #    for henId in range(nbrOfHen) :
    #        data = hendf[hendf.networkNumber==henId].recycledEnergyFromStorage.reset_index(drop=True)
    #        ax.plot(data, label='HEN #{}'.format(henId))
    #        plt.title("Energy recycled from storage")
    #        plt.ylabel("Energy")
    #        plt.xlabel("Step")
    #        plt.legend()
    #    f, ax = plt.subplots()
    #    for henId in range(nbrOfHen) :
    #        data = hendf[hendf.networkNumber==henId].energyCost.reset_index(drop=True)
    #        ax.plot(data, label='HEN #{}'.format(henId))
    #        plt.title("Cost in energy")
    #        plt.ylabel("Energy")
    #        plt.xlabel("Step")
    #        plt.legend()
    #    return
    
    # =============================================================================
    #  LOGGING IN FILES SO WE CAN RE READ
    # =============================================================================
    
    # energydf.to_csv("energydf.csv")
    # for objId, obj in enumerate(lflux) :
        # fct.save_obj(obj, "flux{}.obj".format(objId))
    #print(exchanger_computed_data)
    #print(len(exchanger_computed_data))
    #print(ranking_list)
    return energydf, network_list, signaturestr, ranking_list, exchanger_computed_data
    
