# -*- coding: utf-8 -*-
"""
Created on Wed May 15 16:51:46 2019

@author: abonicel
"""
import math

class ssFlux:
    
    def __init__(self,Te,Ts,CP,debVol,rho,mu,lamb,press,objFlux,typeFlux,estDivise,utilite,energE=0,tDeb=0,tFin=0):
        self.typeFlux=typeFlux #chaud ou froid
        self.Te=Te #en °C
        self.Ts=Ts #en °C
        self.CP=CP #en W/°C
        self.debVol=debVol #en m3/s
        self.rho=rho #en kg/m3
        self.mu=mu #en Pa.s
        self.lamb=lamb #en W/m/K
        self.x=objFlux.xDeb #en pixel
        self.y=objFlux.yDeb #en pixel
#        self.x=1 #pour test
#        self.y=1 #pour test
        self.xFin=0 #en pixel
        self.yFin=0 #en pixel
        self.xFinEch=0 #en pixel donne la position de l'échangeur
        self.yFinEch=0 #en pixel donne la position de l'échangeur
        self.longTuy=0 #en m
        self.nbCoude=0 #sans unité
        self.press=press #en Pa
        self.objPip= None
        self.objPomp= None
        self.objFlux=objFlux
        self.refEch=True #True s'il échange encore après False sinon
        self.refFlux=(0,0) #tuple avec première valeur la reférence au flux et la seconde au sous flux
        self.estDivise=estDivise #True s'il est divisé False sinon
        self.utilite=utilite #True s'il s'agit d'un échange avec une utilité False sinon
        self.tDeb=tDeb #marque le début de présence du ssFlux
        self.tFin=tFin #marque la fin de présence du ssFlux
        self.energE=energE #permet de mettre à jour les tuples des couples en discontinu (non nécessaire en continu et pour les utilités)

    def pas_egal(self,other):
        return self.refFlux!=other.refFlux and self.typeFlux!=other.typeFlux
    
    def hasNaN(self):
        for attr in self.__dict__:
            if attr in(int, float):
                if math.isnan(attr):
                    print("NaN pour "+attr)