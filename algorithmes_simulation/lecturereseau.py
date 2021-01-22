# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 10:24:42 2019

@author: abonicel
"""
import pickle
#import Flux
#import reseau,kpi,ssFlux
import AlgorithmeThermique
#import algo_complet as alg
#import couple
import random

with open('Reseau_Statique8flux_80echangeur', 'rb') as fichier:
    mon_depickler = pickle.Unpickler(fichier)
    reseau1 = mon_depickler.load()   
    
nss=len(reseau1.ensFlux)

n=len(reseau1.listeSsFlux)
for i in range(n):
    reseau1.listeSsFlux[i].objFlux.xDeb,reseau1.listeSsFlux[i].objFlux.yDeb,reseau1.listeSsFlux[i].objFlux.xFin,reseau1.listeSsFlux[i].objFlux.yFin=random.randint(0,400),random.randint(0,400),random.randint(0,400),random.randint(0,400)
#    print("xFin Flux",reseau1.listeSsFlux[i].objFlux.xFin,"yFin Flux",reseau1.listeSsFlux[i].objFlux.yFin)    

for j in range(n):
    reseau1.listeSsFlux[j].x=reseau1.listeSsFlux[j].objFlux.xDeb
    reseau1.listeSsFlux[j].y=reseau1.listeSsFlux[j].objFlux.yDeb
#    print("la ref du ssflux est",reseau1.listeSsFlux[j].refFlux,"| type flux",reseau1.listeSsFlux[j].typeFlux,"| Te",reseau1.listeSsFlux[j].Te,"°C | Ts",reseau1.listeSsFlux[j].Ts,"°C | divise",reseau1.listeSsFlux[j].estDivise,"| utilite",reseau1.listeSsFlux[j].utilite)

E_ech=0
for couple in reseau1.listeCouple:
    E_ech+=couple.puissE
#    print("le ssflux chaud",couple.ssFluxC,"| le ssflux froid",couple.ssFluxF,"| la puissance échangée",couple.puissE,"kW")

reseau1.KPI.enEch=E_ech*8760
    
#nu=len(reseau1.listeUtilite)
#for k in range(nu):
#    if reseau1.listeUtilite[k].ssFlux == (1,0) or reseau1.listeUtilite[k].ssFlux == (2,0) or reseau1.listeUtilite[k].ssFlux == (3,7) or reseau1.listeUtilite[k].ssFlux == (4,0) or reseau1.listeUtilite[k].ssFlux == (5,0) or  reseau1.listeUtilite[k].ssFlux == (6,6):
#        reseau1.listeUtilite[k].typeUtil="f"
#    elif reseau1.listeUtilite[k].ssFlux == (2,1) or reseau1.listeUtilite[k].ssFlux == (3,2) or reseau1.listeUtilite[k].ssFlux == (7,2):
#        reseau1.listeUtilite[k].typeUtil="c"
#
#print("\n")
##nc=len(reseau1.listeCouple)
#for j in range(n):
##    print("le type du flux est :",reseau1.listeSsFlux[j].typeFlux,"la ref",reseau1.listeSsFlux[j].refFlux,"utilite",reseau1.listeSsFlux[j].utilite)
##    print("la ref",reseau1.listeSsFlux[j].refFlux)
#    print("la ref du ssflux est",reseau1.listeSsFlux[j].refFlux,"| x",reseau1.listeSsFlux[j].x,"y",reseau1.listeSsFlux[j].y,"| xFinEch",reseau1.listeSsFlux[j].xFinEch,"yFinEch",reseau1.listeSsFlux[j].yFinEch,"| xFin",reseau1.listeSsFlux[j].xFin,"yFin",reseau1.listeSsFlux[j].yFin,"| division", reseau1.listeSsFlux[j].estDivise)
#    print("le flux chaud référencé :",reseau1.listeCouple[j].ssFluxC,"échange avec le flux froid référencé :",reseau1.listeCouple[j].ssFluxF)
print("\n")
#print("\n",reseau1.listeSsFlux[13].refFlux)
#Tce,Tcs=reseau1.listeSsFlux[13].Te,reseau1.listeSsFlux[13].Ts
#print("Tce ",Tce,"°C et Tcs ",Tcs,"°C")
#print("\n",reseau1.listeSsFlux[22].refFlux)
#Tfe,Tfs=reseau1.listeSsFlux[22].Te,reseau1.listeSsFlux[22].Ts
#print("Tfe ",Tfe,"°C et Tfs ",Tfs,"°C")
#print("le nombre de sous flux est :",len(reseau1.listeSsFlux))
#print("le nombre de flux est :",len(reseau1.ensFlux))
#print(reseau1.listeSsFlux[3].x)
#ssFluxFroid=alg.tri(alg.tmpfroid(reseau1.listeSsFlux))
#ssflux=alg.selection(ssFluxFroid,(3,1))
#print(ssflux.typeFlux)
#couple=alg.selection_couple(reseau1.listeCouple,ssflux)
#print(couple.ssFluxF)
#ssFluxChaud=alg.tri(alg.tmpchaud(reseau1.listeSsFlux))
##liste donnant seulement les sous flux froid
print("Le MER ",reseau1.KPI.mer,"kW | pourcentage MER",reseau1.KPI.prctMer,"| nombre utilités",reseau1.KPI.nbUti,"| nombre échangeur",reseau1.KPI.nbEch,"| énergie échangée",reseau1.KPI.enEch,"kWh")
#
#ssflux=alg.selection(ssFluxFroid,(3,1))
#print('la ref est :',ssflux.refFlux)
#print("L'algo est lancé")
AlgorithmeThermique.Algo(reseau1,0.1,400,400)
#print("\n")
#
for couple in reseau1.listeCouple:
    
    print("le ssflux chaud",couple.ssFluxC,"| le ssflux froid",couple.ssFluxF,"| la puissance échangée",couple.puissE,"kW")
    
print("\n")
#for j in range(n):
#    print("la ref du ssflux est",reseau1.listeSsFlux[j].refFlux,"| xFin Flux",reseau1.listeSsFlux[j].objFlux.xFin,"yFin Flux",reseau1.listeSsFlux[j].objFlux.yFin)    

#print("\n")
#
print("Le MER ",reseau1.KPI.mer,"kW | pourcentage MER",reseau1.KPI.prctMer,"| nombre utilités",reseau1.KPI.nbUti,"| nombre échangeur",reseau1.KPI.nbEch,"| CAPEX",reseau1.KPI.cap,"€ | OPEX",reseau1.KPI.op,"€ | co2",reseau1.KPI.co2,"kt eq | Economie elec",reseau1.KPI.ecoElec,"€ | Economie gaz",reseau1.KPI.ecoGaz,"€ | Economie fioul",reseau1.KPI.ecoFioul,"€ | énergie échangée",reseau1.KPI.enEch,"kWh")
#
##S_pip=0

for j in range(n):

    print("la ref du ssflux est",reseau1.listeSsFlux[j].refFlux,"| type flux",reseau1.listeSsFlux[j].typeFlux,"| Te",reseau1.listeSsFlux[j].Te,"°C | Ts",reseau1.listeSsFlux[j].Ts,"°C | longueur tuyauterie",reseau1.listeSsFlux[j].longTuy,"m")

#print("\nle cout total de la tuyauterie est de :",S_pip,"€\n")
#
#nc=len(reseau1.listeCouple)
#
#S_ech=0
#for j in range(nc):
#    S_ech+=reseau1.listeCouple[j].objEch.cout
#    print("la ref du chaud et du froid",reseau1.listeCouple[j].ssFluxC,reseau1.listeCouple[j].ssFluxF,"| le cout de l'échangeur est",reseau1.listeCouple[j].objEch.cout,"€ | la surface d'échange est de :",reseau1.listeCouple[j].objEch.surfEch,"m²")
#
#print("\nle cout total des échangeurs est de :",S_ech,"€\n")
#
##for j in range(nc):
##    print("le type d'échangeur est :",reseau1.listeCouple[j].objEch.typee,"| la perte de charge du fluide chaud",reseau1.listeCouple[j].objEch.perteChaud,"Pa","| la perte de charge du fluide froid",reseau1.listeCouple[j].objEch.perteFroid,"Pa")
#
##print("\n")
#S_pomp=0
#P_pompe_tot=0
#P_pompe=0
#for j in range(n):
##    if reseau1.listeSsFlux[j].utilite==False:
##    if reseau1.listeSsFlux[j].refFlux != (2,1):
##        S_pomp+=reseau1.listeSsFlux[j].objPomp.coutInves
##        P_pompe_tot+=reseau1.listeSsFlux[j].objPomp.puissance
#    P_pompe+=reseau1.listeSsFlux[j].objPomp.puissance
#    print("la ref du ssflux est",reseau1.listeSsFlux[j].refFlux,"| le type de ssflux est :",reseau1.listeSsFlux[j].typeFlux,"| la puissance de la pompe",reseau1.listeSsFlux[j].objPomp.puissance/1000,"kW | prix pompe",reseau1.listeSsFlux[j].objPomp.coutInves,"€")
#    else:
#        if reseau1.listeSsFlux[j].refEch==True:
##            S_pomp+=reseau1.listeSsFlux[j].objPomp.coutInves
#            print("la ref du ssflux est",reseau1.listeSsFlux[j].refFlux,"| le type de ssflux est :",reseau1.listeSsFlux[j].typeFlux,"| la puissance de la pompe",reseau1.listeSsFlux[j].objPomp.puissance/1000,"kW | prix pompe",reseau1.listeSsFlux[j].objPomp.coutInves,"€")

#print("\nle cout total des pompes est de :",S_pomp,"€\n")
#print("\nla puissance totale des pompes est :",P_pompe_tot/1000,"kW soit pour un fonctionnement annuel",P_pompe_tot/1000*8760,"kWh\n")
##for j in range(n):
##    if reseau1.listeSsFlux[j].utilite==False:
##        print("la ref du ssflux et son type",reseau1.listeSsFlux[j].refFlux,reseau1.listeSsFlux[j].typeFlux,"| le debit volumique",reseau1.listeSsFlux[j].debVol,"m3/s | la perte de charge dans la tuyauterie",reseau1.listeSsFlux[j].objPip.pertes,"Pa | diametre tuyauterie",reseau1.listeSsFlux[j].objPip.diamTuy,"m")
##    else:
##        if reseau1.listeSsFlux[j].refEch==True:
##            print("la ref du ssflux et son type",reseau1.listeSsFlux[j].refFlux,reseau1.listeSsFlux[j].typeFlux,"| le debit volumique",reseau1.listeSsFlux[j].debVol,"m3/s | la perte de charge dans la tuyauterie",reseau1.listeSsFlux[j].objPip.pertes,"Pa | diametre tuyauterie",reseau1.listeSsFlux[j].objPip.diamTuy,"m")
#
#print("\nl'investissement total est de :",S_pomp+S_ech+S_pip,"€")