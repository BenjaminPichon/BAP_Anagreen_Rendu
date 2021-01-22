# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 14:50:20 2019

@author: abonicel

Finished on Thu July 11
"""

import time
import pickle
from operator import itemgetter

from predimensionnement import Predimensionnement
from creation_reseau_statique import ReseauEchangeursMER14
from couts import Cost

def AlgoFinal(r_echelle,m,n, pos_flux=None, ensFlux=None, deltaTmin=None):
    debut=time.time()
    
    reseau=ReseauEchangeursMER14.HEN(ensFlux, deltaTmin)
#    
#    with open('objReseauIni3', 'wb') as fichier:#écriture de l'objet reseauFinal dans un fichier
#    	mon_depickler = pickle.Pickler(fichier)
#    	mon_depickler.dump(fichier)
    
    
    ######TEST DU CONTINU SUR CAS SIMPLE##############
    #Si les positions ne sont pas fournies, les charger depuis les fichiers binaires contenus dans le dossier Donnees
    if pos_flux is None:

        with open('donnees\listePosChaudDeb', 'rb') as fichier:
            mon_depickler = pickle.Unpickler(fichier)
            listePosChaudDeb = mon_depickler.load()
        
        with open('donnees\listePosChaudFin', 'rb') as fichier:
            mon_depickler = pickle.Unpickler(fichier)
            listePosChaudFin = mon_depickler.load()
        
        with open('donnees\listePosFroidDeb', 'rb') as fichier:
            mon_depickler = pickle.Unpickler(fichier)
            listePosFroidDeb = mon_depickler.load()
            
        with open('donnees\listePosFroidFin', 'rb') as fichier:
            mon_depickler = pickle.Unpickler(fichier)
            listePosFroidFin = mon_depickler.load()
        
        
        for ssflux in reseau.listeSsFlux:
            
            if ssflux.typeFlux == "c" :
                    
                ssflux.objFlux.xDeb,ssflux.objFlux.yDeb,ssflux.objFlux.xFin,ssflux.objFlux.yFin = listePosChaudDeb[ssflux.refFlux[0]-1][0],listePosChaudDeb[ssflux.refFlux[0]-1][1],listePosChaudFin[ssflux.refFlux[0]-1][0],listePosChaudFin[ssflux.refFlux[0]-1][1]
                print("Position : ", ssflux.objFlux.xDeb,ssflux.objFlux.yDeb,ssflux.objFlux.xFin,ssflux.objFlux.yFin)
                
            if ssflux.typeFlux == "f" :
                
                ssflux.objFlux.xDeb,ssflux.objFlux.yDeb,ssflux.objFlux.xFin,ssflux.objFlux.yFin = listePosFroidDeb[ssflux.refFlux[0]-1][0],listePosFroidDeb[ssflux.refFlux[0]-1][1],listePosFroidFin[ssflux.refFlux[0]-1][0],listePosFroidFin[ssflux.refFlux[0]-1][1]

    # for couple in reseau.listeCouple:
       
    #     print("chaud / froid",couple.ssFluxC,couple.ssFluxF)
   
    # longlist=len(reseau.listeSsFlux)
   
    # for k in range(len(reseau.listeCouple)):
    #     print("ref chaud et froid",reseau.listeCouple[k].ssFluxC,reseau.listeCouple[k].ssFluxF,"| puissE",reseau.listeCouple[k].puissE,"kW")
    
#    for i in range(longlist):
#        reseau.listeSsFlux[i].objFlux.xDeb,reseau.listeSsFlux[i].objFlux.yDeb,reseau.listeSsFlux[i].objFlux.xFin,reseau.listeSsFlux[i].objFlux.yFin=random.randint(0,400),random.randint(0,400),random.randint(0,400),random.randint(0,400)
    
    #Sinon, utiliser les positions fournies (par la plateforme)
    else:
        for ssflux in reseau.listeSsFlux:
            nf = ssflux.refFlux[0]
            if ssflux.typeFlux == "f" :
                nf = -nf
            ssflux.objFlux.xDeb = pos_flux[nf]["posX"]
            ssflux.objFlux.xFin = pos_flux[nf]["posXend"]
            ssflux.objFlux.yDeb = pos_flux[nf]["posY"]
            ssflux.objFlux.yFin = pos_flux[nf]["posYend"]

            ssflux.x,ssflux.y = ssflux.objFlux.xDeb,ssflux.objFlux.yDeb
      
        
#    for j in range(longlist):
#        reseau.listeSsFlux[j].x=reseau.listeSsFlux[j].objFlux.xDeb
#        reseau.listeSsFlux[j].y=reseau.listeSsFlux[j].objFlux.yDeb
#        print("la ref du ssflux est",reseau.listeSsFlux[j].refFlux,"| type flux",reseau.listeSsFlux[j].typeFlux,"| x",reseau.listeSsFlux[j].x,"| y",reseau.listeSsFlux[j].y,"| xFin",reseau.listeSsFlux[j].objFlux.xFin,"| yFin",reseau.listeSsFlux[j].objFlux.yFin)
#        
    E_ech=0
    for couple in reseau.listeCouple:
        E_ech+=couple.puissE
#    print("le ssflux chaud",couple.ssFluxC,"| le ssflux froid",couple.ssFluxF,"| la puissance échangée",couple.puissE,"kW")

    reseau.KPI.enEch=E_ech*8760
    print("Energie echangee",reseau.KPI.enEch,"kWh")
#    print("Le MER ",reseau.KPI.mer,"kW | pourcentage MER",reseau.KPI.prctMer,"% | nombre utilités",reseau.KPI.nbUti,"| nombre échangeur",reseau.KPI.nbEch,"| CAPEX",reseau.KPI.cap,"€ | OPEX",reseau.KPI.op,"| puissance échangée",reseau.KPI.enEch,"kW")
    
    # AlgorithmeThermique.Algo(reseau,r_echelle,m,n)
    Predimensionnement.Predimensionnement(reseau,r_echelle,m,n)
    
#    for ssflux in reseau.listeSsFlux:
#        if ssflux.objPip != 0 :
#            print("ref flux et type",ssflux.refFlux,ssflux.typeFlux,"pertes de charges",ssflux.objPip.pertes,"Pa")
    
#    for couple in reseau.listeCouple:
#        print("ref chaud et froid",couple.ssFluxC,couple.ssFluxF,"| pertes chaud et froid",couple.objEch.perteChaud,couple.objEch.perteFroid)
    
    print("Le MER ",reseau.KPI.mer,"kW | pourcentage MER",reseau.KPI.prctMer,"% | nombre utilités",reseau.KPI.nbUti,"| nombre échangeur",reseau.KPI.nbEch,"| CAPEX",reseau.KPI.cap,"€ | OPEX",reseau.KPI.op,"€ | co2",reseau.KPI.co2,"kt eq | Economie elec",reseau.KPI.ecoElec,"€ | Economie gaz",reseau.KPI.ecoGaz,"€ | Economie fioul",reseau.KPI.ecoFioul,"€ | puissance échangée",reseau.KPI.puissEch,"kW | cout ech",reseau.KPI.coutEch,"€ | cout pompe",reseau.KPI.coutPompe,"€ | cout fonc pompe",reseau.KPI.coutfoncpompe,"€ | cout fonc uti",reseau.KPI.coutfoncuti,"€ | nbpompe",reseau.KPI.nbpompe,"| puissance pompe",reseau.KPI.puissancepompe/1000,"kW | surface ech min",reseau.KPI.surfaceminech,"m² | surf ech max",reseau.KPI.surfacemaxech,"m² | puiss min ech",reseau.KPI.puissanceminech,"kW | puiss max ech",reseau.KPI.puissancemaxech,"kW | TRI",reseau.KPI.TRI,"années | VAN", reseau.KPI.van, "€ | IP ", reseau.KPI.ip, " | puissance utilite chaude",reseau.KPI.puissanceutilitechaude,"kW | puissance utilite froide",reseau.KPI.puissanceutilitefroide,"kW | cout tuyauterie",reseau.KPI.couttuyauterie,"€ | longueur tuyauterie",reseau.KPI.longueurtuyauterie,"m | économie totale",reseau.KPI.ecoTot,"€")
    
    print("\n------------------------------------------\n")
    for couple in reseau.listeCouple:
        print("type d'échangeur en place",couple.objEch.typee)
    print("\n------------------------------------------\n")


    # ##### Donne pour chaque échangeur : fluxchaud, fluxfroid, puissance échangée, pourcentage de puissance échangée par rapport à la puissance totale #####
    # listeech = []
    # for couple in reseau.listeCouple :
    #     listeech.append((couple.ssFluxC[0], couple.ssFluxF[0], round(couple.puissE,3) , round(couple.puissE*100/reseau.KPI.puissEch, 3)))
    # listeech = sorted(listeech, key = itemgetter(2), reverse = True)
    # print(listeech)

    
    fin=time.time()
    print("...l'algorithme a tourné pendant :",fin-debut,"s")
    
    # for couple in reseau.listeCouple :
    #     print(couple.objEch.typee)
    
    # with open('Reseau_Statique3flux_40echangeur', 'wb') as fichier:#écriture de l'objet reseauFinal dans un fichier
    #     mon_pickler = pickle.Pickler(fichier)
    #     mon_pickler.dump(reseau)

    return reseau


    ########################################################################################################
    ########## Calculs des TRI, IP, VAN par échangeur (nouveaux attributs de la classe échangeur) ##########
    ############################### Calculs faits dans Predimensionnement.py ###############################
    ########################################################################################################

    # print("Retour du fichier contenant les kpi : ", reseau.KPI)
    # print("Puissance échangée totale : ", reseau.KPI.puissEch, " kWh")

    # s = 0
    # for eltech in reseau.listeCouple :
    #     s += eltech.puissE
    # print(s, " kW")

    # sum = 0
    # for ech in reseau.listeCouple :
    #     print(ech.puissE)
    #     sum += ech.puissE
    # print("somme des puissances échangées par les échangeurs : ", sum, " kW")

    # listeinfoech = []
    # sumcout = 0
    # for cple in reseau.listeCouple :
    #     listeinfoech.append((cple.ssFluxC[0], cple.ssFluxF[0], round(cple.puissE,0) , round(cple.objEch.surfEch,2), round(cple.objEch.cout,0), cple.objEch.typee))
    #     sumcout += cple.objEch.cout

    # listeinfoech = sorted(listeinfoech, key = itemgetter(2), reverse = True)
    # print(listeinfoech)
    # print(round(sumcout, 0))


    # rendement = [0.8, 0.5]
    # pourcentage = [0.4, 0.6, 0, 0, 0, 0]
    # print("co2 sauvé au total : ", reseau.KPI.co2)
    # for ech in reseau.listeCouple :
    #     print(Cost.CO2(pourcentage, rendement, ech.puissE))

    # nbr_cycle = 8760 / reseauDynamique.dureeTot 
    # print("Durée totale du réseau : ", reseauDynamique.dureeTot)
    # print("Nombre de cycle nbr_cycle : ", nbr_cycle)

    # rendement = [0.8, 0.5] #valeurs des rendements de combustion et thermique/élec (tiré de algopiping)
    # pourcentage = [0.4, 0.6, 0, 0, 0, 0] #pourcentages des différentes sources de production d'électricité du site industriel : élec, gaz naturel, GPL, essence, diesel, charbon (tiré de algopiping)
    # taux_actualisation = 0.01 #hypothèse : taux d'actualisation 1%
    # duree_vie = 10 #hypothèse : durée de vie des équipements de récupération de chaleur 10 ans 
    # print("Le taux d'actualisation pris en compte est ", taux_actualisation*100, "%")
    # print("La durée de vie des systèmes de récupération de chaleur prise en compte est ", duree_vie, " ans")

    # # Cout Economisé
    # # Tiré de Cost --> Economie et Economie_tot
    # h_annee=8760
    # C_elec=0.0715 # en kWh
    # C_gaz=0.075 # en kWh
    # C_fioul=0.0917 # en kWh

    # Liste_numchaud = [] #contient le num du flux chaud de l'échangeur
    # Liste_numfroid = [] #contient le num du flux froid de l'échangeur
    # Liste_num = [] #contient les numéros donnés aux échangeurs
    # Liste_typeech = [] #contient les types d'échangeurs
    # Liste_surfech = [] #contient la surface des échangeurs
    # Liste_cout = [] #contient le coût d'achat des échangeurs + celui de la tuyauterie associée à l'échangeur
    # # Liste_coutbis = []
    # Liste_lontuy = []
    # Liste_capex = [] #contient le capex des échangeurs
    # Liste_opex = [] #contient l'opex des échangeurs
    # Liste_co2 = [] #contient l'économie en co2 réalisée grâce aux échangeurs
    # Liste_ecoelec = [] #contient l'économie d'électricité en € réalisée grâce aux échangeurs
    # Liste_ecogaz = [] #contient l'économie de gaz en € réalisée grâce aux échangeurs
    # Liste_ecofioul = [] #contient l'économie de fioul en € réalisée grâce aux échangeurs
    # Liste_ecotot = [] #contient l'économie totale en € réalisée grâce aux échangeurs
    # Liste_puissech = [] #contient la puissance des échangeurs
    # Liste_energieech = [] #contient l'énergie échangée par les échangeurs
    # # Liste_van = [[0]*(duree_vie+1)]*(len(reseauDynamique.listeMaxEchangeur)) #contient la van des échangeurs
    # Liste_van = [[0]*(duree_vie+1) for k in range(len(reseau.listeCouple))]
    # Liste_tri = [0]*(len(reseau.listeCouple)) #contient le tri des échangeurs
    # # Liste_ip = [[0]*(duree_vie+1)]*(len(reseauDynamique.listeMaxEchangeur)) #contient l'ip des échangeurs
    # Liste_ip = [[0]*(duree_vie+1) for k in range(len(reseau.listeCouple))]

    # ssFluxDictC = {}
    # ssFluxDictF = {}
    # for i in reseau.listeSsFlux:
    #     if i.typeFlux == 'c':
    #         if i.refFlux[0] not in ssFluxDictC:
    #             ssFluxDictC[i.refFlux[0]] = {}
    #         ssFluxDictC[i.refFlux[0]][i.refFlux[1]] = i
    #     else:
    #         if i.refFlux[0] not in ssFluxDictF:
    #             ssFluxDictF[i.refFlux[0]] = {}
    #         ssFluxDictF[i.refFlux[0]][i.refFlux[1]] = i

    # num = 1
    # for cple in reseau.listeCouple :
    #     Liste_num.append(num)
    #     num += 1

    #     Liste_numchaud.append(cple.ssFluxC[0])
    #     Liste_numfroid.append(cple.ssFluxF[0])

    #     Liste_typeech.append(cple.objEch.typee)
    #     Liste_surfech.append(cple.objEch.surfEch)
    #     Liste_cout.append(cple.objEch.cout)

    #     # listessfc = []
    #     # listessff = []
    #     # lontuy = 0
    #     # for tuplechaud in echangeur.listeSsFluxChaud :
    #     #     listessfc.append(tuplechaud[0])
    #     # for tuplefroid in echangeur.listeSsFluxFroid :
    #     #     listessff.append(tuplefroid[0])

    #     # for ssfc in listessfc : #parcourt les ssfluxchaud qui intéragissent avec l'échangeur
    #     #     Liste_cout[-1] += ssfc.objPip.coutTuy + ssfc.objPip.coutIso #ajoute le prix de la tuyauterie
    #     #     lontuy += ssfc.longTuy
    #     #     # if ssfc.objPomp != 0 :
    #     #     #    Liste_cout[-1] += ssfc.objPomp.coutInves #ajoute le prix des pompes
    #     # for ssff in listessff : #parcourt les ssfluxfroid qui intéragissent avec l'échangeur
    #     #     Liste_cout[-1] += ssff.objPip.coutTuy + ssff.objPip.coutIso #ajoute le prix de la tuyauterie
    #     #     lontuy += ssff.longTuy
    #     #     # if ssff.objPomp != 0 :
    #     #     #    Liste_cout[-1] += ssff.objPomp.coutInves #ajoute le prix des pompes

    #     lontuy = 0
    #     # print(cple.ssFluxC, cple.ssFluxF)
    #     # Liste_cout[-1] += cple.ssFluxC.objPip.coutTuy + cple.ssFluxC.objPip.coutIso
    #     Liste_cout[-1] += ssFluxDictC[cple.ssFluxC[0]][cple.ssFluxC[1]].objPip.coutTuy + ssFluxDictC[cple.ssFluxC[0]][cple.ssFluxC[1]].objPip.coutIso
    #     lontuy += ssFluxDictC[cple.ssFluxC[0]][cple.ssFluxC[1]].longTuy
    #     # Liste_cout[-1] += cple.ssFluxF.objPip.coutTuy + cple.ssFluxF.objPip.coutIso
    #     Liste_cout[-1] += ssFluxDictF[cple.ssFluxF[0]][cple.ssFluxF[1]].objPip.coutTuy + ssFluxDictF[cple.ssFluxF[0]][cple.ssFluxF[1]].objPip.coutIso
    #     lontuy += ssFluxDictF[cple.ssFluxF[0]][cple.ssFluxF[1]].longTuy

        
    #     Liste_lontuy.append(lontuy)
    #     # Liste_coutbis.append(Cost.Cout(echangeur.objEch.surfEch, echangeur.objEch.typee, echangeur.ssfluxchaudmax, echangeur.ssfluxfroidmax))
    #     Liste_capex.append(Cost.Capex(Liste_cout[-1])[0])
    #     Liste_opex.append(Cost.Opex(Liste_capex[-1])[0])
    #     Liste_co2.append(Cost.CO2(pourcentage, rendement, cple.puissE*8760*0.8)) 
    #     Liste_ecoelec.append(h_annee*cple.puissE*C_elec*pourcentage[0])
    #     Liste_ecogaz.append(h_annee*cple.puissE*C_gaz*pourcentage[1])
    #     Liste_ecofioul.append(h_annee*cple.puissE*C_fioul*pourcentage[2])
    #     Liste_ecotot.append(Cost.economie_tot(cple.puissE, 0.4, 0.6, 0))
    #     Liste_puissech.append(cple.puissE)
    #     Liste_energieech.append(cple.energE) 

    # print(Liste_num) #OK
    # print(Liste_numchaud)
    # print(Liste_numfroid)
    # print(Liste_typeech) #OK
    # print(Liste_surfech) #OK
    # print("la surface de l'échangeur le plus petit est de : ", min(Liste_surfech), " m²") #OK
    # print("la surface de l'échangeur le plus grand est de : ", max(Liste_surfech), " m²") #OK
    # print(Liste_cout) #OK
    # print("La somme des coûts des échangeurs est de ", sum(Liste_cout), " €") #OK
    # print(Liste_capex)
    # print("Le CAPEX total des échangeurs est de ", sum(Liste_capex), " €") #la vraie valeur est plus haute : prendre en compte pompes et utilités et...
    # print(Liste_opex)
    # print("L'OPEX total des échangeurs est de ", sum(Liste_opex), " €") #idem
    # print(Liste_lontuy)
    # print("La longueur de la tuyauterie est de ", sum(Liste_lontuy), " m")
    # print(Liste_co2)
    # print("L'économie en CO2 réalisée grâce aux échangeurs est de ", sum(Liste_co2), " kt eq CO2") #la vraie valeur est plus faible : elle prend en compte la tuyauterie, les pompes et les utilités
    # print(Liste_ecoelec)
    # print("L'économie électrique réalisée grâce aux échangeurs est de ", sum(Liste_ecoelec), " €") #idem
    # print(Liste_ecogaz)
    # print("L'économie de gaz réalisée grâce aux échangeurs est de ", sum(Liste_ecogaz), " €") #idem
    # print(Liste_ecofioul)
    # print("L'économie de fioul réalisée grâce aux échangeurs est de ", sum(Liste_ecofioul), " €") #idem
    # print(Liste_ecotot)
    # print("L'économie totale réalisée grâce aux échangeurs est de ", sum(Liste_ecotot), " €")
    # print(Liste_puissech)
    # print("La puissance totale échangée par les échangeurs est : ", sum(Liste_puissech), " kW") #OK ?
    # print("La puissance minimale échangée par un échangeur est : ", min(Liste_puissech), " kW") #OK
    # print("La puissance maximale échangée par un échangeur est : ", max(Liste_puissech), " kW") #OK
    # # print(Liste_energieech)
    # # print("L'énergie totale échangée par les échangeurs est : ", sum(Liste_energieech), " kWh") #OK

    # ##### Calcul des Valeurs Actuelles Nettes (VAN) pour chaque année et chaque échangeur #####
    # for ind in range (len(reseau.listeCouple)) :
    #     Liste_van[ind][0] = (-1) * Liste_capex[ind] #initialisation : à l'année 0 on a juste investi le CAPEX
    #     for j in range (1, (duree_vie+1)) :
    #         Liste_van[ind][j] = Liste_van[ind][j-1] + ((Liste_ecotot[ind] - Liste_opex[ind]) / ((1+taux_actualisation)**j)) #hérédité : chaque année on ajoute l'économie (économie moins OPEX) réalisée actulaisée

    # # print(id(Liste_van[-1]))
    # # print(Liste_van)

    # # for i in range (0, len(reseau.listeCouple)) :
    # #     print("La VAN de l'échangeur ", i+1, " au bout de 10 ans est : ", Liste_van[i][duree_vie], " €")


    # ##### Calcul des indices de profitabilité (IP) pour chaque année et pour chaque échangeur #####
    # for i in range (len(reseau.listeCouple)) :
    #     for j in range (0, (duree_vie+1)) :
    #         Liste_ip[i][j] = (Liste_capex[i] + Liste_van[i][j]) / Liste_capex[i]

    # # print(Liste_ip)

    # # for i in range (0, len(reseau.listeCouple)) :
    # #     print("L'IP de l'échangeur ", i+1, " au bout de 10 ans est : ", Liste_ip[i][duree_vie])


    # # ##### Est-ce que l'échangeur est rentable ? Si OPEX > économie : problème #####
    # # for i in range (len(reseau.listeCouple)) :
    # #     if (Liste_opex[i] > Liste_ecotot[i]) :
    # #         print("L'échangeur numéro ", i, " coûte plus qu'il ne rapporte !")
    # #         print("L'OPEX de cet échangeur vaut ", round(Liste_opex[i],0), "€")
    # #         print("L'économie réalisée grâce à cet échangeur vaut ", round(Liste_ecotot[i], 0), "€")

    # ##### Calcul du TRI pour chaque échangeur #####
    # for i in range (len(reseau.listeCouple)) :
    #     Liste_tri[i] = Liste_capex[i] / (Liste_ecotot[i] - Liste_opex[i])
    # # print("La liste des TRI (en années) des échangeurs est : ", Liste_tri)

    # listetotale = [] #contient les infos sur les échangeurs de la forme ((numfluxchaud, numfluxfroid, puissance, surface, TRI, VAN en fin de vie, IP en fin de vie))
    # for i in range(len(reseau.listeCouple)) :
    #     listetotale.append((Liste_numchaud[i], Liste_numfroid[i], round(Liste_puissech[i],3), round(Liste_surfech[i],3), round(Liste_tri[i],3), round(Liste_van[i][duree_vie],3), round(Liste_ip[i][duree_vie],3)))

    # listetotale = sorted(listetotale, key = itemgetter(6), reverse = False) #on trie la liste par IP croissant
    # # print("Liste de TOUS les échangeurs : ", listetotale)
    # print("Il y a en tout ", len(listetotale), " échangeurs")


    # indi = 0
    # for elt in listetotale :
    #     if elt[6] <= 1 :
    #         indi += 1
    # # print("Le nombre d'échangeurs NON RENTABLES (en fin de vie) est ", indi)
    # # print("Le nombre d'échangeurs RENTABLES (en fin de vie) est ", len(listetotale)-indi)

    # # print("L'indice du premier échangeur rentable (IP > 0) est ", indi)

    # listeech_nonrentable = []
    # listeech_rentable = []
    # for m in range(0, indi) :
    #     listeech_nonrentable.append(listetotale[m])
    # #La liste est déjà triée de l'échangeur le moins rentable au plus rentable (ici aucun n'est rentable)
    
    # for n in range(indi, len(listetotale)) :
    #     listeech_rentable.append(listetotale[n])
    # listeech_rentable = sorted(listeech_rentable, key = itemgetter(6), reverse = True)
    # #On trie la liste de l'échangeur le plus rentable au moins rentable (ici ils sont tous rentables)

    # print("Le nombre d'échangeurs NON RENTABLES (en fin de vie) est ", len(listeech_nonrentable))
    # print(listeech_nonrentable)
    # print("Le nombre d'échangeurs RENTABLES (en fin de vie) est ", len(listeech_rentable))
    # print(listeech_rentable)
    



###### Pour tester l'algo #####
#Test = AlgoFinal(0.05, 400, 400)

