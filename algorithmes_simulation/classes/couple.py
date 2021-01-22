# -*- coding: utf-8 -*-
"""
Created on Wed May 15 16:58:33 2019

@author: abonicel
"""

class couple:
    
    def __init__(self,ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC,energE=0,puissMax=0,tDeb=0,tFin=0):
        self.ssFluxF=ssFluxF #référence au sous-flux froid
        self.ssFluxC=ssFluxC #référence au sous-flux chaud
        self.puissE=puissE #puissance échangée en kW
        self.objEch=0
        self.classement=0 #donne la liste des possibilités d'échangeurs pour le couple
        self.energE=energE #énergie échangée en kWh
        self.puissMax=puissMax #puissMax pour un couple donné (pour le dimensionnement des échangeurs)
        self.tDeb=tDeb #marque le début de présence du ssFlux
        self.tFin=tFin #marque la fin de présence du ssFlux
        self.TeC=TeC
        self.TsC=TsC
        self.TeF=TeF
        self.TsF=TsF
                
        # La VAN et l'IP sont calculés avec : durée de vie n de 10 ans, taux d'actualisation i de 1%
        # Pour changer ces valeurs : Predimensionnement.py
        # Le cout_tot correspond au cout de l'échangeur + celui de la tuyauterie qui lui est associée
        # Le CAPEX et l'OPEX sont calculés à partir de ce couttot

        self.couttot = 0 #cout de l'échangeur + tuyauterie associée
        self.lontuy = 0 #longueur de la tuyauterie associée
        self.capexech = 0 #capex de l'échangeur + tuyauterie
        self.opexech = 0 #opex de l'échangeur + tuyauterie
        self.co2ech = 0 #co2 sauvé par l'échangeur
        self.ecototech = 0 #économie réalisée par l'échangeur
        self.triech = 0 #TRI de échangeur + tuyauterie
        self.vanech = 0 #VAN de échangeur + tuyauterie
        self.ipech = 0 #IP de échangeur + tuyauterie