# -*- coding: utf-8 -*-
"""
Created on Wed May 15 16:51:46 2019

@author: abonicel
"""

class utilite:
    
    def __init__(self,ssFlux,puissE,typeUtil,Te=0,Ts=0,tDeb=0,tFin=0):
        self.ssFlux=ssFlux#référence au sous-flux 
        self.puissE=puissE #en kW
        self.typeUtil=typeUtil #"c" pour utilité de chauffage et "f" pour utilité de refroidissement
        self.tDeb=tDeb #marque le début de présence du ssFlux
        self.tFin=tFin #marque la fin de présence du ssFlux
        self.Te=Te #donne la température du flux en entrée de l'utilité
        self.Ts=Ts #donne la température du flux en entrée de l'utilité
