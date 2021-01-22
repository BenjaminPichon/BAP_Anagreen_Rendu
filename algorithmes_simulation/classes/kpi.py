# -*- coding: utf-8 -*-
"""
Created on Wed May 15 16:51:46 2019

@author: abonicel
"""

class kpi:
    
    def __init__(self,mer):
        self.mer=mer # donne le mer total en kW
        self.prctMer=0 # donne la puissance des utilités dépassant le MER en pourcentage
        self.nbUti=0 # donne le nombre d'utilités du réseau
        self.nbEch=0 # donne le nombre d 'échangeurs du réseau
        self.cap=0 # donne le capex
        self.op=0 # donne l'opex
        self.co2=0 # donne l'équivalent C02 sauvé
        self.ecoElec=0 # donne en € l'économie d'énergie
        self.ecoGaz=0 # donne en € l'économie d'énergie
        self.ecoFioul=0 # donne en € l'économie d'énergie
        self.ecoElecCycle=0 # donne en € l'économie d'énergie
        self.ecoGazCycle=0 # donne en € l'économie d'énergie
        self.ecoFioulCycle=0 # donne en € l'économie d'énergie
        self.enEch=0 # énergie échange sur une année kWh
        self.puissEch = 0 # puissance échangée kW
        self.coutEch = 0 # cout total investissement des echangeurs
        self.coutPompe = 0 # cout investissement des pompes
        self.coutfoncpompe = 0 # cout fonctionnement total annuel des pompes
        self.coutfoncuti = 0 # cout fonctionnement total annuel des utilites
        self.nbpompe = 0 # nombre total de pompe
        self.puissancepompe = 0 # puissance totale des pompes W
        self.energiepompe = 0 # énergie des pompes en kWh
        self.surfaceminech = 0 # surface min des echangeurs m²
        self.surfacemaxech = 0 # surface max des echangeurs m²
        self.puissanceminech = 0 # puissance min echangeur kW
        self.puissancemaxech = 0 # puissance max echangeur kW
        self.TRI = 0 # temps de retour sur investissement en année
        self.puissanceutilitechaude = 0 # puissance utilité chaude en kW
        self.puissanceutilitefroide = 0 # puissance utilité froide en kW
        self.energieutilitechaude = 0 # energie utilité chaude en kWh
        self.energieutilitefroide = 0 # energie utilité froide en kWh
        self.ecoTot = 0 # économie d'énerie totale en €
        self.van = 0 #VAN au bout de la durée de vie et avec le taux d'actualisation choisi
        self.ip = 0 #IP au bout de la durée de vie et avec le taux d'actualisation choisi