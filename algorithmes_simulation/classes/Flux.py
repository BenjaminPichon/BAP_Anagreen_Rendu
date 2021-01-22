# -*- coding: utf-8 -*-
"""
Created on mars 07 

@author: paToussaint
"""

# -*- coding: utf-8 -*-
#"""
#Éditeur de Spyder

class Flux:

	def __init__(self,type,Te,Ts,CP,rho=0,mu=0,lamb=0,press=0,debVol=0,nom="",process=True):
		self.type=type
		self.Te=Te
		self.Ts=Ts
		self.CP=CP
		self.nom=nom
		self.div=0 
		self.pinc="non"
		self.ech="non"
		self.b=1
		self.chargeThA=0
		self.chargeThA1=0
		self.chargeThE=0
		self.chargeThE1=0
		self.b1=0
		self.verif=0
		self.puissModif="non"
		self.plusEch="oui"
		self.Ts1=Ts
		self.test=[]
		self.echChargeTh="oui" #indique si le flux échange toute sa charge Th "oui" ou moins que sa chargeTh : "non"
		self.rho=rho
		self.mu=mu
		self.lamb=lamb
		self.press=press
		self.debVol=debVol
		self.xDeb=0 #en pixel
		self.yDeb=0 #en pixel
		self.xFin=0 #en pixel
		self.yFin=0 #en pixel
		self.listeSsFlux=[]
		self.process=process #(concerne uniquement les flux chauds) indique si le refroidissement du flux est nécessaire (True), si ce n'est pas le cas (False), alors il n'est pas nécessaire de la refroidir jusqu'à sa température de sortie avec une utilité


		
	


		

