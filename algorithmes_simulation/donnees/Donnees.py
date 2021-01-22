# -*- coding: utf-8 -*-
"""
Created on mai 13 

@author: p-aToussaint
"""

from classes import Flux
#import FluxDisc
import copy
#import xlrd
#import pandas as pd

def donnees():
	#Les exemples sont tirés du livre "Pinch Analysis and process integration" de Ian C.Kemp

	ensFlux=[] #contient l'ensemble (ens) des flux => servira pour le dessous du pincement
	ensFlux0=[] #contient l'ensemble (ens) des flux => servira pour le dessus du pincement
	durCycle=1 #valeur par défaut

	"""
	#tableau 2.2 ou fig 2.18  MER-HEN fct
	deltaTmin=25
	ensFlux.append(Flux.Flux("f",20,135,2))
	ensFlux.append(Flux.Flux("c",170,60,3))
	ensFlux.append(Flux.Flux("f",80,140,4))
	ensFlux.append(Flux.Flux("c",150,30,1.5))"""
	"""
	#tableau 2.4 MER fct - pas de HEN dans la littérature - MER au-dessus du pincement atteint
	deltaTmin=25
	ensFlux.append(Flux.Flux("c",200,50,3))
	ensFlux.append(Flux.Flux("c",240,100,1.5))
	ensFlux.append(Flux.Flux("c",120,119,300))
	ensFlux.append(Flux.Flux("f",30,200,4))
	ensFlux.append(Flux.Flux("f",50,250,2))"""
	"""
	#figure 4.18 (alternative network design) MER-HEN fct
	deltaTmin=25
	ensFlux.append(Flux.Flux("c",150,40,0.1))
	ensFlux.append(Flux.Flux("c",150,30,0.12))
	ensFlux.append(Flux.Flux("c",150,30,0.15))
	ensFlux.append(Flux.Flux("c",150,30,0.2))
	ensFlux.append(Flux.Flux("c",150,30,0.25))
	ensFlux.append(Flux.Flux("c",100,80,2))
	ensFlux.append(Flux.Flux("f",20,150,0.1))
	ensFlux.append(Flux.Flux("f",20,150,0.16))
	ensFlux.append(Flux.Flux("f",20,150,0.18))
	ensFlux.append(Flux.Flux("f",20,150,0.24))
	ensFlux.append(Flux.Flux("f",20,150,0.3))"""
	"""
	#figure 4.23 (cas threshold) MER fct - HEN ne fct pas
	deltaTmin=25
	ensFlux.append(Flux.Flux("f",20,135,2))
	ensFlux.append(Flux.Flux("c",170,60,3))
	ensFlux.append(Flux.Flux("f",80,140,2))
	ensFlux.append(Flux.Flux("c",150,30,1.5))"""
	"""
	#figure 4.21 (cas threshold) MER fct - HEN ne fct pas
	deltaTmin=5
	ensFlux.append(Flux.Flux("f",20,135,2))
	ensFlux.append(Flux.Flux("c",170,60,3))
	ensFlux.append(Flux.Flux("f",80,140,4))
	ensFlux.append(Flux.Flux("c",150,30,1.5))"""
	"""
	#tableau 4.31 MER fct - HEN fct
	deltaTmin=25
	ensFlux.append(Flux.Flux("c",159,77,2.285))
	ensFlux.append(Flux.Flux("c",267,80,0.204))
	ensFlux.append(Flux.Flux("c",343,90,0.538))
	ensFlux.append(Flux.Flux("f",16,117,0.933))
	ensFlux.append(Flux.Flux("f",118,265,1.961))"""
	"""
	#Midrex boite grise old
	deltaTmin=10
	ensFlux.append(Flux.Flux("c",150,20,6.947))
	ensFlux.append(Flux.Flux("c",150,20,6.947))
	ensFlux.append(Flux.Flux("c",238,112,1.069))
	ensFlux.append(Flux.Flux("c",45,20,6.947))
	ensFlux.append(Flux.Flux("c",45,20,6.947))
	ensFlux.append(Flux.Flux("c",1832,20,5.846))
	ensFlux.append(Flux.Flux("f",33,166,1.730))
	ensFlux.append(Flux.Flux("f",20,1668,1.157))
	ensFlux.append(Flux.Flux("f",20,1668,1.122))
	ensFlux.append(Flux.Flux("f",166,800,35.164))
	ensFlux.append(Flux.Flux("f",9,1072,15.419))
	ensFlux.append(Flux.Flux("f",101,650,20.366))
	ensFlux.append(Flux.Flux("f",20,650,0.192))
	ensFlux.append(Flux.Flux("f",20,650,0.045))
	ensFlux.append(Flux.Flux("f",20,1072,0.426))
	ensFlux.append(Flux.Flux("f",20,150,6.947))
	ensFlux.append(Flux.Flux("f",20,150,6.947))"""
	"""
	#Figure 9.39 MER fct pas
	deltaTmin=5.5
	ensFlux.append(Flux.Flux("c",108.4,10,3.34))
	ensFlux.append(Flux.Flux("c",86,86,30000))#pb avec ce flux car deltaT nul => MER pas correct
	ensFlux.append(Flux.Flux("c",86,10,1.1))
	ensFlux.append(Flux.Flux("c",60,13,2.98))
	ensFlux.append(Flux.Flux("c",55,13,4.5))
	ensFlux.append(Flux.Flux("c",41,13,5.31))
	ensFlux.append(Flux.Flux("f",10,70,3.05))
	ensFlux.append(Flux.Flux("f",37.8,100,3.98))"""
	"""
	#Midrex boite grise new
	deltaTmin=10
	ensFlux.append(Flux.Flux("c",150,20,23))
	ensFlux.append(Flux.Flux("c",150,20,23))
	ensFlux.append(Flux.Flux("c",238,112,1.069))
	ensFlux.append(Flux.Flux("c",45,20,1.261))
	ensFlux.append(Flux.Flux("c",45,20,1.261))
	ensFlux.append(Flux.Flux("c",1832,20,5.846))
	ensFlux.append(Flux.Flux("f",33,166,1.730))
	ensFlux.append(Flux.Flux("f",20,1668,1.157))
	ensFlux.append(Flux.Flux("f",20,1668,1.122))
	ensFlux.append(Flux.Flux("f",166,800,9.5))
	ensFlux.append(Flux.Flux("f",9,1072,15.419))
	ensFlux.append(Flux.Flux("f",101,650,4.7))
	ensFlux.append(Flux.Flux("f",20,650,0.192))
	ensFlux.append(Flux.Flux("f",20,650,0.045))
	ensFlux.append(Flux.Flux("f",20,1072,0.426))
	#ensFlux.append(Flux.Flux("f",20,150,6.947))
	#ensFlux.append(Flux.Flux("f",20,150,6.947))"""
	"""
	#Cokerie boite noire 
	deltaTmin=25
	ensFlux.append(Flux.Flux("c",200,20,77.8,"Fum2"))
	ensFlux.append(Flux.Flux("c",100,20,943.3,"Vap1"))
	ensFlux.append(Flux.Flux("c",65,12,636.7,"EaR1"))
	ensFlux.append(Flux.Flux("c",70,65,645.3,"Eau2"))
	ensFlux.append(Flux.Flux("c",800,500,105.4,"EaG1"))
	ensFlux.append(Flux.Flux("c",2000,20,12.1,"Torche COG"))
	ensFlux.append(Flux.Flux("c",72.5,36,23.7,"EaP1"))
	ensFlux.append(Flux.Flux("c",23,20.5,229.9,"EaRE1"))
	ensFlux.append(Flux.Flux("c",23,22,581,"EaIn2"))
	ensFlux.append(Flux.Flux("c",40,20,58.1,"EaC1"))
	ensFlux.append(Flux.Flux("c",81,38,4.4,"Bue1"))
	ensFlux.append(Flux.Flux("c",160,20,7.8,"Fum3"))
	ensFlux.append(Flux.Flux("f",20,200,3.9,"Pat1"))
	ensFlux.append(Flux.Flux("f",20,100,594.3,"Extérieur-Ga"))
	ensFlux.append(Flux.Flux("f",20,100,393.9,"Extérieur-Air"))
	ensFlux.append(Flux.Flux("f",23,45,58.1,"EaIn4"))
	ensFlux.append(Flux.Flux("f",20,90,13.7,"EaIn7"))"""
	"""
	#test
	deltaTmin=10
	ensFlux.append(Flux.Flux("c",420,20,6.947))
	ensFlux.append(Flux.Flux("c",150,20,0.5))
	ensFlux.append(Flux.Flux("c",238,10,1.069))
	ensFlux.append(Flux.Flux("c",45,20,2))
	ensFlux.append(Flux.Flux("c",45,20,4))
	ensFlux.append(Flux.Flux("c",1832,20,5.846))
	ensFlux.append(Flux.Flux("c",30,250,3))
	ensFlux.append(Flux.Flux("c",30,540,20))
	ensFlux.append(Flux.Flux("c",40,125,7))
	ensFlux.append(Flux.Flux("f",9,166,1.730))
	ensFlux.append(Flux.Flux("f",20,1668,1.157))
	ensFlux.append(Flux.Flux("f",20,1668,1.122))
	ensFlux.append(Flux.Flux("f",166,800,35.164))
	ensFlux.append(Flux.Flux("f",5,1072,25))
	ensFlux.append(Flux.Flux("f",101,650,20.366))
	ensFlux.append(Flux.Flux("f",20,650,0.192))
	ensFlux.append(Flux.Flux("f",20,650,0.045))
	ensFlux.append(Flux.Flux("f",20,1072,0.426))
	ensFlux.append(Flux.Flux("f",20,150,6.947))
	ensFlux.append(Flux.Flux("f",20,150,6.947))"""
	"""
	#Midrex Boite noire V1
	deltaTmin=25
	ensFlux.append(Flux.Flux("c",150,20,23.02,1000,2.8*10**(-4),0.604,1.013*10**5,5.5*10**(-3),"scrubTop"))
	ensFlux.append(Flux.Flux("c",150,20,23.02,1000,2.8*10**(-3),0.604,1.013*10**5,5.5*10**(-3),"scrubCool"))
	ensFlux.append(Flux.Flux("c",238,20,288.32,0.67,1.03*10**(-5),0.0127,1.013*10**5,1.4*10**(1),"cool"))
	ensFlux.append(Flux.Flux("c",45,20,1.261,1000,2.8*10**(-4),0.604,1.013*10**5,3.0*10**(-4),"compTop"))
	ensFlux.append(Flux.Flux("c",45,20,1.261,1000,2.8*10**(-4),0.604,1.013*10**5,3.0*10**(-4),"compCool"))
	ensFlux.append(Flux.Flux("c",1832,20,58.35,0.67,1.03*10**(-5),0.0127,1.5*10**5,1.35,"echap"))
	ensFlux.append(Flux.Flux("f",33,166,31.72,0.67,1.03*10**(-5),0.0127,1.013*10**5,1.56,"GN21"))
	ensFlux.append(Flux.Flux("f",10,1668,19.60,0.67,1.03*10**(-5),0.0127,1.013*10**5,9.62*10**(-1),"GN8"))
	ensFlux.append(Flux.Flux("f",20,1668,1.204,1.2,2.2*10**(-5),0.0234,1.013*10**5,9.96*10**(-1),"Air8"))
	ensFlux.append(Flux.Flux("f",101,834,21.644,0.67,1.03*10**(-5),0.0127,5*10**5,1.35,"Fuel"))
	ensFlux.append(Flux.Flux("f",20,834,3.38,0.67,1.03*10**(-5),0.0127,1.013*10**5,1.7*10**(-1),"GN13"))
	ensFlux.append(Flux.Flux("f",20,834,0.78,0.67,1.03*10**(-5),0.0127,1.013*10**5,3.8*10**(-2),"GNaux"))
	ensFlux.append(Flux.Flux("f",20,1072,0.46,1.2,2.2*10**(-5),0.0234,1.013*10**5,3.79*10**(-1),"AirAux"))"""
	"""
	#Midrex Boite noire V2
	deltaTmin=10
	ensFlux.append(Flux.Flux("c",150,20,400.9,1000,2.8*10**(-4),0.604,2*10**5,9.6*10**(-2),"scrubTop",True))
	ensFlux.append(Flux.Flux("c",150,20,50.9,1000,2.8*10**(-4),0.604,2*10**5,1.2*10**(-2),"scrubCool",True))
	ensFlux.append(Flux.Flux("c",238,20,14.6,0.67,1.03*10**(-5),0.0127,20*10**5,7.2*10**(-1),"cool",True))
	ensFlux.append(Flux.Flux("c",45,20,1.261,1000,2.8*10**(-4),0.604,2*10**5,3.0*10**(-4),"compTop",True))
	ensFlux.append(Flux.Flux("c",45,20,1.261,1000,2.8*10**(-4),0.604,2*10**5,3.0*10**(-4),"compCool",True))
	ensFlux.append(Flux.Flux("c",1832,20,58.35,0.67,1.03*10**(-5),0.0127,3*10**5,1.35,"echap",True))
	ensFlux.append(Flux.Flux("f",33,166,1.3,0.67,1.03*10**(-5),0.0127,25*10**5,6.3*10**(-2),"GN21"))
	ensFlux.append(Flux.Flux("f",10,1668,0.9,0.67,1.03*10**(-5),0.0127,23*10**5,4.2*10**(-2),"GN8"))
	ensFlux.append(Flux.Flux("f",20,1668,0.053,1.2,2.2*10**(-5),0.0234,23*10**5,4.4*10**(-2),"Air8"))
	ensFlux.append(Flux.Flux("f",101,834,21.64,0.67,1.03*10**(-5),0.0127,5*10**5,1.35,"Fuel"))
	ensFlux.append(Flux.Flux("f",-9.86,834,0.68,0.67,1.03*10**(-5),0.0127,5*10**5,3.4*10**(-2),"GN13"))
	ensFlux.append(Flux.Flux("f",-9.86,834,0.16,0.67,1.03*10**(-5),0.0127,5*10**5,7.8*10**(-3),"GNaux"))
	ensFlux.append(Flux.Flux("f",-6.16,1072,0.09,1.2,2.2*10**(-5),0.0234,5*10**5,7.7*10**(-2),"AirAux"))"""
	

	# #test discontinue flux type A
	# deltaTmin=10
	# durCycle=1 #donne la durée du cycle en h 
	# monExcel=xlrd.open_workbook(R'C:\Users\patoussaint\Documents\DataScience\tableau_fusion\donneesDiscontinues.xlsx')
	# ensFeuille=monExcel.sheet_names() # Récupération du nom de toutes les feuilles sous forme d'une liste
	# nbLigne=0
	# for i in range(len(ensFeuille)):
	# 	feuille=monExcel.sheet_by_name(str(ensFeuille[i]))
	# 	# print("Format de la feuille 1:")
	# 	# print("Nom: "+str(feuille_1.name))
	# 	# print("Nombre de colonnes: "+str(feuille_1.ncols))
	# 	nbLigne=feuille.nrows#Nombre de lignes
	# 	j=1
	# 	while j!=nbLigne:
	# 		ensFlux.append(FluxDisc.Flux(str(feuille.cell_value(rowx=j, colx=0)),feuille.cell_value(rowx=j, colx=1),feuille.cell_value(rowx=j, colx=2),feuille.cell_value(rowx=j, colx=3),feuille.cell_value(rowx=j, colx=4),feuille.cell_value(rowx=j, colx=5)))
	# 		j+=1
		


	# #test discontinue flux type B,C
	# deltaTmin=10
	# durCycle=1 #donne la durée du cycle en h
	# monExcel=xlrd.open_workbook(R'C:\Users\patoussaint\Documents\DataScience\tableau_fusion\donneesDiscontinues1.xlsx')
	# ensFeuille=monExcel.sheet_names() # Récupération du nom de toutes les feuilles sous forme d'une liste
	# nbLigne=0
	# for i in range(len(ensFeuille)):
	# 	feuille=monExcel.sheet_by_name(str(ensFeuille[i]))
	# 	# print("Format de la feuille 1:")
	# 	# print("Nom: "+str(feuille_1.name))
	# 	# print("Nombre de colonnes: "+str(feuille_1.ncols))
	# 	nbLigne=feuille.nrows#Nombre de lignes
	# 	j=1
	# 	while j!=nbLigne:
	# 		ensFlux.append(FluxDisc.Flux(str(feuille.cell_value(rowx=j, colx=7)),feuille.cell_value(rowx=j, colx=8),feuille.cell_value(rowx=j, colx=9),feuille.cell_value(rowx=j, colx=10),feuille.cell_value(rowx=j, colx=11),feuille.cell_value(rowx=j, colx=12)))
	# 		j+=1

	#test discontinue flux type B,C moyenné
	# deltaTmin=10
	# ensFlux.append(Flux.Flux("f",20,135,10))
	# ensFlux.append(Flux.Flux("f",80,140,8))
	# ensFlux.append(Flux.Flux("c",170,60,4))
	# ensFlux.append(Flux.Flux("c",150,30,3))



	"""
	#test discontinue1
	deltaTmin=10
	ensFlux.append(FluxDisc.Flux("f",20,135,10,0.5,0.7))
	ensFlux.append(FluxDisc.Flux("f",80,140,8,0,0.5))
	ensFlux.append(FluxDisc.Flux("c",170,60,4,0.25,1))
	ensFlux.append(FluxDisc.Flux("c",150,30,3,0.3,0.8))"""
	"""
	#Midrex Boite noire V2 -- PB avec echap A -> atteint pas sa Ts
	deltaTmin=10
	ensFlux.append(Flux.Flux("c",60,0,528.52,96,2.8*10**(-4),0.604,0.4*10**5,1.27*10**(-1),"scrubTop",True))
	ensFlux.append(Flux.Flux("c",60,0,71.76,996,2.8*10**(-4),0.604,1.8*10**5,1.72*10**(-2),"scrubCool",True))
	ensFlux.append(Flux.Flux("c",118,-21,23.64,1.07,1.03*10**(-5),0.0127,1.8*10**5,1.19*10**(1),"cool",True))
	ensFlux.append(Flux.Flux("c",45,0,1.26,998,2.8*10**(-4),0.604,2*10**5,3.02*10**(-4),"compTop",True))
	ensFlux.append(Flux.Flux("c",45,0,1.26,998,2.8*10**(-4),0.604,2*10**5,3.02*10**(-4),"compCool",True))
	ensFlux.append(Flux.Flux("c",427,-21,5.22,0.27,1.03*10**(-5),0.0127,0.4*10**5,8.26,"echap_A",True))
	ensFlux.append(Flux.Flux("c",427,-21,5.22,0.27,1.03*10**(-5),0.0127,0.4*10**5,8.26,"echap_B",True))
	ensFlux.append(Flux.Flux("f",-9,68,5.3,1.13,1.03*10**(-5),0.0127,1.8*10**5,2.51,"GN21_A"))
	ensFlux.append(Flux.Flux("f",-9,68,5.3,1.13,1.03*10**(-5),0.0127,1.8*10**5,2.51,"GN21_B"))
	ensFlux.append(Flux.Flux("f",-31,954,1.55,0.47,1.03*10**(-5),0.0127,1.8*10**5,1.78,"GN8"))
	ensFlux.append(Flux.Flux("f",-21,954,1.49,1.2,2.2*10**(-5),0.0234,1.8*10**5,1.78,"Air8"))
	ensFlux.append(Flux.Flux("f",34,477,1.66,0.67,1.03*10**(-5),0.0127,0.4*10**5,8.26,"Fuel_A"))
	ensFlux.append(Flux.Flux("f",34,477,1.66,0.67,1.03*10**(-5),0.0127,0.4*10**5,8.26,"Fuel_B"))
	ensFlux.append(Flux.Flux("f",-31,477,0.08,0.67,1.03*10**(-5),0.0127,0.4*10**5,2.69*10**(-1),"GN13_A"))
	ensFlux.append(Flux.Flux("f",-31,477,0.08,0.67,1.03*10**(-5),0.0127,0.4*10**5,2.69*10**(-1),"GN13_B"))
	ensFlux.append(Flux.Flux("f",-31,477,0.02,0.67,1.03*10**(-5),0.0127,0.4*10**5,5.87*10**(-2),"GNaux_A"))
	ensFlux.append(Flux.Flux("f",-31,477,0.02,0.67,1.03*10**(-5),0.0127,0.4*10**5,5.87*10**(-2),"GNaux_B"))
	ensFlux.append(Flux.Flux("f",-30,595,0.25,1.2,2.2*10**(-5),0.0234,0.4*10**5,5.86*10**(-1),"AirAux_A"))
	ensFlux.append(Flux.Flux("f",-30,595,0.25,1.2,2.2*10**(-5),0.0234,0.4*10**5,5.86*10**(-1),"AirAux_B"))"""
	"""
	#Midrex Boite noire V2 -- Valeur positive
	deltaTmin=10
	#ensFlux.append(Flux.Flux("c",60,0,528.52,96,2.8*10**(-4),0.604,0.4*10**5,1.27*10**(-1),"scrubTop",True))
	#ensFlux.append(Flux.Flux("c",120,0,71.76,996,2.8*10**(-4),0.604,1.8*10**5,1.72*10**(-2),"scrubCool",True))
	ensFlux.append(Flux.Flux("c",118,21,23.64,1.07,1.03*10**(-5),0.0127,1.8*10**5,1.19*10**(1),"cool",True))
	ensFlux.append(Flux.Flux("c",45,0,1.26,998,2.8*10**(-4),0.604,2*10**5,3.02*10**(-4),"compTop",True))
	ensFlux.append(Flux.Flux("c",45,0,1.26,998,2.8*10**(-4),0.604,2*10**5,3.02*10**(-4),"compCool",True))
	ensFlux.append(Flux.Flux("c",427,21,5.22,0.27,1.03*10**(-5),0.0127,0.4*10**5,8.26,"echap_A",True))
	ensFlux.append(Flux.Flux("c",427,21,5.22,0.27,1.03*10**(-5),0.0127,0.4*10**5,8.26,"echap_B",True))
	ensFlux.append(Flux.Flux("f",9,68,5.3,1.13,1.03*10**(-5),0.0127,1.8*10**5,2.51,"GN21_A"))
	ensFlux.append(Flux.Flux("f",9,68,5.3,1.13,1.03*10**(-5),0.0127,1.8*10**5,2.51,"GN21_B"))
	ensFlux.append(Flux.Flux("f",31,954,1.55,0.47,1.03*10**(-5),0.0127,1.8*10**5,1.78,"GN8"))
	ensFlux.append(Flux.Flux("f",21,954,1.49,1.2,2.2*10**(-5),0.0234,1.8*10**5,1.78,"Air8"))
	ensFlux.append(Flux.Flux("f",34,477,1.66,0.67,1.03*10**(-5),0.0127,0.4*10**5,8.26,"Fuel_A"))
	ensFlux.append(Flux.Flux("f",34,477,1.66,0.67,1.03*10**(-5),0.0127,0.4*10**5,8.26,"Fuel_B"))
	ensFlux.append(Flux.Flux("f",31,477,0.08,0.67,1.03*10**(-5),0.0127,0.4*10**5,2.69*10**(-1),"GN13_A"))
	ensFlux.append(Flux.Flux("f",31,477,0.08,0.67,1.03*10**(-5),0.0127,0.4*10**5,2.69*10**(-1),"GN13_B"))
	ensFlux.append(Flux.Flux("f",31,477,0.02,0.67,1.03*10**(-5),0.0127,0.4*10**5,5.87*10**(-2),"GNaux_A"))
	ensFlux.append(Flux.Flux("f",31,477,0.02,0.67,1.03*10**(-5),0.0127,0.4*10**5,5.87*10**(-2),"GNaux_B"))
	ensFlux.append(Flux.Flux("f",30,595,0.25,1.2,2.2*10**(-5),0.0234,0.4*10**5,5.86*10**(-1),"AirAux_A"))
	ensFlux.append(Flux.Flux("f",30,595,0.25,1.2,2.2*10**(-5),0.0234,0.4*10**5,5.86*10**(-1),"AirAux_B"))"""
	"""
	#Midrex Boite noire V2 
	deltaTmin=10
	ensFlux.append(Flux.Flux("c",60,0,528.52,96,2.8*10**(-4),0.604,0.4*10**5,1.27*10**(-1),"scrubTop",True))
	ensFlux.append(Flux.Flux("c",120,0,71.76,996,2.8*10**(-4),0.604,1.8*10**5,1.72*10**(-2),"scrubCool",True))
	ensFlux.append(Flux.Flux("c",118,-21,23.64,1.07,1.03*10**(-5),0.0127,1.8*10**5,1.19*10**(1),"cool",False))
	ensFlux.append(Flux.Flux("c",45,0,1.26,998,2.8*10**(-4),0.604,2*10**5,3.02*10**(-4),"compTop",False))
	ensFlux.append(Flux.Flux("c",45,0,1.26,998,2.8*10**(-4),0.604,2*10**5,3.02*10**(-4),"compCool",False))
	ensFlux.append(Flux.Flux("c",427,-21,5.22,0.27,1.03*10**(-5),0.0127,0.4*10**5,8.26,"echap_A",False))
	ensFlux.append(Flux.Flux("c",427,-21,5.22,0.27,1.03*10**(-5),0.0127,0.4*10**5,8.26,"echap_B",False))
	ensFlux.append(Flux.Flux("f",-9,68,5.3,1.13,1.03*10**(-5),0.0127,1.8*10**5,2.51,"GN21_A"))
	ensFlux.append(Flux.Flux("f",-9,68,5.3,1.13,1.03*10**(-5),0.0127,1.8*10**5,2.51,"GN21_B"))
	ensFlux.append(Flux.Flux("f",-31,954,1.55,0.47,1.03*10**(-5),0.0127,1.8*10**5,1.78,"GN8"))
	ensFlux.append(Flux.Flux("f",-21,954,1.49,1.2,2.2*10**(-5),0.0234,1.8*10**5,1.78,"Air8"))
	ensFlux.append(Flux.Flux("f",34,477,1.66,0.67,1.03*10**(-5),0.0127,0.4*10**5,8.26,"Fuel_A"))
	ensFlux.append(Flux.Flux("f",34,477,1.66,0.67,1.03*10**(-5),0.0127,0.4*10**5,8.26,"Fuel_B"))
	ensFlux.append(Flux.Flux("f",-31,477,0.08,0.67,1.03*10**(-5),0.0127,0.4*10**5,2.69*10**(-1),"GN13_A"))
	ensFlux.append(Flux.Flux("f",-31,477,0.08,0.67,1.03*10**(-5),0.0127,0.4*10**5,2.69*10**(-1),"GN13_B"))
	ensFlux.append(Flux.Flux("f",-31,477,0.02,0.67,1.03*10**(-5),0.0127,0.4*10**5,5.87*10**(-2),"GNaux_A"))
	ensFlux.append(Flux.Flux("f",-31,477,0.02,0.67,1.03*10**(-5),0.0127,0.4*10**5,5.87*10**(-2),"GNaux_B"))
	ensFlux.append(Flux.Flux("f",-30,595,0.25,1.2,2.2*10**(-5),0.0234,0.4*10**5,5.86*10**(-1),"AirAux_A"))
	ensFlux.append(Flux.Flux("f",-30,595,0.25,1.2,2.2*10**(-5),0.0234,0.4*10**5,5.86*10**(-1),"AirAux_B"))"""
	
	# Midrex Boite noire V3 
	deltaTmin=10
	# ensFlux.append(Flux.Flux("c",60,0,564.81,996,2.8*10**(-4),0.604,0.4*10**5,1.36*10**(-1),"scrubTop",True))
	# ensFlux.append(Flux.Flux("c",120,0,56.81,983,2.8*10**(-4),0.604,1.8*10**5,1.84*10**(-2),"scrubCool",True))
	ensFlux.append(Flux.Flux("c",118,-21,6.31,0.24,1.03*10**(-5),0.0127,0.4*10**5,1.19*10**(1),"cool",True))
	ensFlux.append(Flux.Flux("c",45,0,1.26,998,2.8*10**(-4),0.604,2*10**5,3.02*10**(-4),"compTop",True))
	ensFlux.append(Flux.Flux("c",45,0,1.26,998,2.8*10**(-4),0.604,2*10**5,3.02*10**(-4),"compCool",True))
	ensFlux.append(Flux.Flux("c",427,-21,3.5,0.27,1.03*10**(-5),0.0127,0.4*10**5,8.26,"echap_A",True))
	ensFlux.append(Flux.Flux("c",427,-21,3.5,0.27,1.03*10**(-5),0.0127,0.4*10**5,8.26,"echap_B",True))
	ensFlux.append(Flux.Flux("f",-9,68,6.36,1.13,1.03*10**(-5),0.0127,1.8*10**5,2.51,"GN21_A"))#
	ensFlux.append(Flux.Flux("f",-9,68,6.36,1.13,1.03*10**(-5),0.0127,1.8*10**5,2.51,"GN21_B"))#
	ensFlux.append(Flux.Flux("f",-31,954,1.86,0.47,1.03*10**(-5),0.0127,1.8*10**5,1.78,"GN8"))
	ensFlux.append(Flux.Flux("f",-21,954,1.49,0.83,2.2*10**(-5),0.0234,1.8*10**5,1.78,"Air8"))
	ensFlux.append(Flux.Flux("f",34,477,2.3,0.17,1.03*10**(-5),0.0127,0.4*10**5,8.26,"Fuel_A"))
	ensFlux.append(Flux.Flux("f",34,477,2.3,0.17,1.03*10**(-5),0.0127,0.4*10**5,8.26,"Fuel_B"))
	ensFlux.append(Flux.Flux("f",-31,477,0.09,0.15,1.03*10**(-5),0.0127,0.4*10**5,2.69*10**(-1),"GN13_A"))
	ensFlux.append(Flux.Flux("f",-31,477,0.09,0.15,1.03*10**(-5),0.0127,0.4*10**5,2.69*10**(-1),"GN13_B"))
	ensFlux.append(Flux.Flux("f",-31,477,0.02,0.15,1.03*10**(-5),0.0127,0.4*10**5,5.87*10**(-2),"GNaux_A"))
	ensFlux.append(Flux.Flux("f",-31,477,0.02,0.15,1.03*10**(-5),0.0127,0.4*10**5,5.87*10**(-2),"GNaux_B"))
	ensFlux.append(Flux.Flux("f",-30,595,0.15,0.25,2.2*10**(-5),0.0234,0.4*10**5,5.86*10**(-1),"AirAux_A"))
	ensFlux.append(Flux.Flux("f",-30,595,0.15,0.25,2.2*10**(-5),0.0234,0.4*10**5,5.86*10**(-1),"AirAux_B"))

	########################################################################################
	#################### Réseau spécial avec un seul intervalle de temps ###################
	########################################################################################

	# deltaTmin = 10
	# ensFlux.append(Flux.Flux("c", 390.6, -22.8, 3.04, 0.27, 1.03*10**(-5), 0.0127, 0.4*10**5, 7.2, "EchapA"))
	# ensFlux.append(Flux.Flux("c", 390.6, -22.8, 3.04, 0.27, 1.03*10**(-5), 0.0127, 0.4*10**5, 7.2, "EchapB"))
	# ensFlux.append(Flux.Flux("f", -9.4, 67.8, 5.32, 1.13, 1.03*10**(-5), 0.0127, 1.8*10**5, 2.1, "GN21_A"))
	# ensFlux.append(Flux.Flux("f", -9.4, 67.8, 5.32, 1.13, 1.03*10**(-5), 0.0127, 1.8*10**5, 2.1, "GN21_B"))
	# ensFlux.append(Flux.Flux("f", 37.2, 462.2, 2.00, 0.165, 1.03*10**(-5), 0.0127, 0.4*10**5, 7.2, "FuelA"))
	# ensFlux.append(Flux.Flux("f", 37.2, 462.2, 2.00, 0.165, 1.03*10**(-5), 0.0127, 0.4*10**5, 7.2, "FuelB"))

	# deltaTmin = 10
	# ensFlux.append(Flux.Flux("c", 330, 160, 15.20, 1.3, 1.85*10**(-5), 0.024, 0.4*10**5, 8.7, "Fumees recup GALVA"))
	# ensFlux.append(Flux.Flux("c", 403, 157, 13.47, 1.3, 1.85*10**(-5), 0.024, 0.4*10**5, 7.7, "Fumees recup RCM"))
	# ensFlux.append(Flux.Flux("f", 132, 143, 193.81, 921, 1.89*10**(-4), 0.6, 7*10**5, 4.94*10**(-2), "ES recup GALVA"))
	# ensFlux.append(Flux.Flux("f", 129, 143, 165.5, 921, 1.89*10**(-4), 0.6, 7*10**5, 4.22*10**(-2), "ES recup RCM"))



	




	ensFlux0=copy.deepcopy(ensFlux)

	#numérotation des flux
	nbFluxC=0
	nbFluxF=0
	for i in range(len(ensFlux)):
		if ensFlux[i].type=="c":
			nbFluxC+=1
			ensFlux[i].numero=nbFluxC
			ensFlux0[i].numero=nbFluxC
			if ensFlux[i].nom=="":
				ensFlux[i].nom=nbFluxC
				ensFlux0[i].nom=nbFluxC
				
		else:
			nbFluxF+=1
			ensFlux[i].numero=nbFluxF
			ensFlux0[i].numero=nbFluxF
			if ensFlux[i].nom=="":
				ensFlux[i].nom=nbFluxF
				ensFlux0[i].nom=nbFluxF

	return(ensFlux,ensFlux0,deltaTmin,durCycle)

	
			
def donnees1(ensFlux,deltaTmin):
	#Affichage jeu de données
	print("\nJeu de données (températures non décalées) : (DeltaTmin = " +str(deltaTmin)+"°C)")
	for i in range(len(ensFlux)):
		print("[Flux: "+ ensFlux[i].type +" "+ str(ensFlux[i].nom)+ "    |    Te: "+ str(ensFlux[i].Te)
		+ "°C    |    Ts: "+ str(ensFlux[i].Ts)+ "°C    |    CP: "+ str(ensFlux[i].CP)+"kW/K    |    ChargThA/B: " 
		+ str(round(ensFlux[i].chargeThA,1))+"/"+str(round(ensFlux[i].chargeThE,1))+" kW]")

