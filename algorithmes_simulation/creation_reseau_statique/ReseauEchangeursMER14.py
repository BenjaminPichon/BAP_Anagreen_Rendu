# -*- coding: utf-8 -*-
"""

Created on mai 27  

@author: p-aToussaint
"""
import numpy as np
import math
import matplotlib.pyplot as plt
from operator import itemgetter, attrgetter
import copy

from creation_reseau_statique import MERContinue1,Division,Fct,reseauUp,reseauDown
from donnees import Donnees
from classes import Flux, reseau,kpi,ssFlux,utilite

def HEN(ensFlux, deltaTmin):
    #Si les donnees ne sont pas fournies, les charger depuis la classe Donnees
    if ensFlux is None or deltaTmin is None:
        ensFlux,ensFlux0,deltaTmin,inutileEnContinu=Donnees.donnees()

    deltaH,temp,EnergEch,MerDessus,MerDessous=MERContinue1.MERCont(ensFlux,deltaTmin)
    ensFlux0=copy.deepcopy(ensFlux)
    ensFlux1=copy.deepcopy(ensFlux)
    
    #Recherche de la température de pincement
    ind=deltaH.index(0)#renvoie l'indice où la puissance cumulée est nulle
    temp.reverse()#pour que deltaH et temp soit dans le même ordre (décroissant)
    Tpincement=temp[ind]
    print("\nLa température de pincement: " + str(Tpincement) + "°C")
    TpincementC=Tpincement+deltaTmin/2#Température de pincement fluide chaud
    TpincementF=Tpincement-deltaTmin/2#Température de pincement fluide froid
    print("La température chaude de pincement: " + str(TpincementC) + "°C")
    print("La température froide de pincement: " + str(TpincementF) + "°C")
    """
    Tpincement=temp[ind]
    print("\nLa température de pincement: " + str(Tpincement) + "°C")
    TpincementC=Tpincement+deltaTmin/2#Température de pincement fluide chaud
    TpincementF=Tpincement-deltaTmin/2#Température de pincement fluide froid
    """
    #Liste des flux au-dessus du pincement
    ensFluxC=[]#flux chauds présents au-dessus du pincement
    ensFluxF=[]#flux froids présents au-dessus du pincement
    chargeThTot=0
    for j in range(len(ensFlux0)):#Séparation des flux présents au-dessus du pincement dans deux listes différentes (chaud et froid)
    	if ensFlux0[j].type=="c":#vérifie si le fluide chaud est présent au-dessus du pincement
    		if ensFlux0[j].Te>TpincementC:
    			val=max(TpincementC,ensFlux0[j].Ts)
    			ensFlux0[j].chargeThA=ensFlux0[j].CP*abs(ensFlux0[j].Te-val)#calcul de la charge thermique du fluide : pour le design du réseau
    			ensFlux[j].chargeThA=ensFlux0[j].CP*abs(ensFlux0[j].Te-val)#calcul de la charge thermique du fluide : pour l'affichage du jeu de données
    			ensFlux1[j].chargeThA=ensFlux0[j].CP*abs(ensFlux0[j].Te-val)#calcul de la charge thermique du fluide : pour l'affichage du jeu de données
    			ensFluxC.append(ensFlux0[j])#pour la zone au-dessus
    			chargeThTot+=ensFlux[j].chargeThA
    	else:
    		if ensFlux0[j].Ts>TpincementF:#vérifie si le fluide froid est présent au-dessus du pincement
    			val=max(TpincementF,ensFlux0[j].Te)
    			ensFlux0[j].chargeThA=ensFlux0[j].CP*abs(ensFlux0[j].Ts-val)#calcul de la charge thermique du fluide
    			ensFlux[j].chargeThA=ensFlux0[j].CP*abs(ensFlux0[j].Ts-val)#calcul de la charge thermique du fluide
    			ensFlux1[j].chargeThA=ensFlux0[j].CP*abs(ensFlux0[j].Ts-val)#calcul de la charge thermique du fluide
    			ensFluxF.append(ensFlux0[j])#pour la zone au-dessus
    			chargeThTot+=ensFlux[j].chargeThA
    
    #Liste des flux en-dessous du pincement
    for i in range(len(ensFlux)):#Séparation des flux présents en-dessous du pincement dans deux listes différentes (chaud et froid)
    	if ensFlux[i].type=="c":#vérifie si le fluide chaud est présent en-dessous du pincement
    		if ensFlux[i].Ts<TpincementC:
    			val=min(TpincementC,ensFlux[i].Te)
    			ensFlux[i].chargeThE=ensFlux[i].CP*abs((ensFlux[i].Ts-val))#calcul de la charge thermique du fluide
    			ensFlux1[i].chargeThE=ensFlux[i].CP*abs((ensFlux[i].Ts-val))#calcul de la charge thermique du fluide
    			chargeThTot+=ensFlux[i].chargeThE
    	else:
    		if ensFlux[i].Te<TpincementF:#vérifie si le fluide froid est présent en-dessous du pincement
    			val=min(TpincementF,ensFlux[i].Ts)
    			ensFlux[i].chargeThE=ensFlux[i].CP*abs((val-ensFlux[i].Te))#calcul de la charge thermique du fluide
    			ensFlux1[i].chargeThE=ensFlux[i].CP*abs((val-ensFlux[i].Te))#calcul de la charge thermique du fluide
    			chargeThTot+=ensFlux[i].chargeThE
    
    
    Donnees.donnees1(ensFlux,deltaTmin)
    
    
    
    
    
    kpi1=kpi.kpi(MerDessus+MerDessous)
    ensFluxInit=copy.deepcopy(ensFlux)#ne sera pas modifiée et servira pour sauvegarder la liste des sousFlux de chaque flux (commun à la zone au-dessus et en-dessous du pincement)
    surconsoTot=0
    
    
    
    
    ###################################################      Au-dessus du pincement      #####################################################################
    
    
    
    
    
    #Réseau d'échangeurs au-dessus du pincement
    print("\nRéseau d'échangeurs au-dessus du pincement :")
    
    """
    #Classement des flux par ordre croissant : le but est que les fluides chauds les plus froids échangent avec les fluides froids les plus froids
    for j in range(len(ensFluxF)):
    	if ensFluxF[j].Te>TpincementF: #on classe les fluides froids par ordre croissant que si un des fluides à une T d'entrée supérieure à la température de pincement. Car sinon, tous les flux ont comme valeur min (au-dessus du pincement) la température du pincement
    		ensFluxF=sorted(ensFluxF,key=attrgetter('Te'))
    for i in range(len(ensFluxC)):
    	if ensFluxC[i].Ts>TpincementC:#on classe les fluides chauds par ordre croissant que si un des fluides à une T de sortie supérieure à la température de pincement. Car sinon, tous les flux ont comme valeur min (au-dessus le pincement) la température du pincement
    		ensFluxC=sorted(ensFluxC,key=attrgetter('Ts'))"""
    
    #Classement des flux par ordre croissant : le but est que les fluides chauds les plus froids échangent avec les fluides froids les plus froids
    trueFalseTab=[[True,False],[False,True],[True,True],[False,False]]
    surconsoFTab=[]#on utilisera cette liste pour sauvegarder les surconsommation par rapport aux MER de chaque réseau 
    for k in range(len(trueFalseTab)):
    	listeCouple=[]#ensemble des couples du réseau
    	listeSsFlux=[]#ensemble des sous-flux du réseau
    	listeUtilite=[]#ensemble des utilités du réseau
    	ensFluxF1=copy.deepcopy(sorted(ensFluxF,key=attrgetter('CP'),reverse=trueFalseTab[k][0]))#on utilise ensFluxF1/C1 pour ne pas modifier ensFluxC/F
    	ensFluxC1=copy.deepcopy(sorted(ensFluxC,key=attrgetter('CP'),reverse=trueFalseTab[k][1]))
    	surconsoF,Reseau1=reseauUp.reseauUp(ensFluxF1,ensFluxC1,TpincementF,TpincementC,deltaTmin,listeCouple,listeUtilite,listeSsFlux,deltaH,[],0)
    	surconsoFTab.append(surconsoF)
    
    
    #On garde finalement que le réseau pour lequel la surconsommation par rapport au MER est minimale
    listeCouple=[]#ensemble des couples du réseau
    listeSsFlux=[]#ensemble des sous-flux du réseau
    listeUtilite=[]#ensemble des utilités du réseau
    print("len(listeCouple) :"+str(len(listeCouple)))
    indMinSurconsoFTab=surconsoFTab.index(min(surconsoFTab))
    ensFluxF=sorted(ensFluxF,key=attrgetter('CP'),reverse=trueFalseTab[indMinSurconsoFTab][0])
    ensFluxC=sorted(ensFluxC,key=attrgetter('CP'),reverse=trueFalseTab[indMinSurconsoFTab][1])
    surconsoF,Reseau1=reseauUp.reseauUp(ensFluxF,ensFluxC,TpincementF,TpincementC,deltaTmin,listeCouple,listeUtilite,listeSsFlux,deltaH,[],0)
    surconsoTot+=surconsoF
    print("len(listeCouple) :"+str(len(listeCouple)))
    
    
    
    
    
    
    
    
    
    
    
    
    for i in range(len(ensFluxC)):#on ajoute à ensFluxInit la liste des sous-flux chaud de dessus
    	for k in range(len(ensFluxInit)):
    		if ensFluxInit[k].type=="c":
    			if ensFluxC[i].numero==ensFluxInit[k].numero:
    				ensFluxInit[k].listeSsFlux+=ensFluxC[i].listeSsFlux
    
    for j in range(len(ensFluxF)):#on ajoute à ensFluxInit la liste des sous-flux froid du dessus
    	for k in range(len(ensFluxInit)):
    		if ensFluxInit[k].type=="f":
    			if ensFluxF[j].numero==ensFluxInit[k].numero:
    				ensFluxInit[k].listeSsFlux+=ensFluxF[j].listeSsFlux
    
    
    
    
    
    
    #########################################################  En-dessous du pincement  ############################################################
    
    
    
    
    
    #Réseau d'échangeurs en-dessous du pincement
    print("\nRéseau d'échangeurs en-dessous du pincement :")
    
    #Liste des flux en-dessous du pincement
    ensFluxC=[]#flux chauds présents en-dessous du pincement
    ensFluxF=[]#flux froids présents en-dessous du pincement
    for i in range(len(ensFlux)):#Séparation des flux présents en-dessous du pincement dans deux listes différentes (chaud et froid)
    	if ensFlux[i].type=="c" and ensFlux[i].Ts<TpincementC:#vérifie si le fluide chaud est présent en-dessous du pincement
    		ensFluxC.append(ensFlux[i])
    	else:
    		if ensFlux[i].Te<TpincementF:#vérifie si le fluide froid est présent en-dessous du pincement
    			ensFluxF.append(ensFlux[i])
    
    """
    #Classement des flux selon la temp par ordre décroissant :le but est que les fluides chauds les plus chauds échangent avec les fluides froids les plus chauds. 
    for j in range(len(ensFluxF)):
    	if ensFluxF[j].Ts<TpincementF: #on classe les fluides froids par ordre croissant que si un des fluides à une T de sortie inférieure à la température de pincement. Car sinon, tous les flux ont comme valeur max (sous le pincement) la température du pincement
    		ensFluxF=sorted(ensFluxF,key=attrgetter('Ts'),reverse=True)
    for i in range(len(ensFluxC)):
    	if ensFluxC[i].Te<TpincementC:#on classe les fluides chauds par ordre croissant que si un des fluides à une T d'entrée inférieure à la température de pincement. Car sinon, tous les flux ont comme valeur max (sous le pincement) la température du pincement
    		ensFluxC=sorted(ensFluxC,key=attrgetter('Te'),reverse=True)"""
    
    
    #ensFluxF.reverse()
    #ensFluxC.reverse()
    
    
    
    
    #Classement des flux par ordre croissant : le but est que les fluides chauds les plus froids échangent avec les fluides froids les plus froids
    trueFalseTab1=[[True,False],[True,True],[False,False],[False,True]]
    surconsoCTab=[]#on utilisera cette liste pour sauvegarder les surconsommation par rapport aux MER de chaque réseau 
    for k in range(len(trueFalseTab1)):
    	listeCouple1=copy.deepcopy(listeCouple)#ensemble des couples du réseau ; on utilise listeCouple1 pour ne pas modifier listeCouple
    	listeSsFlux1=copy.deepcopy(listeSsFlux)#ensemble des sous-flux du réseau ; on utilise listeSsFlux1 pour ne pas modifier listeSsFlux
    	listeUtilite1=copy.deepcopy(listeUtilite)#ensemble des utilités du réseau ; on utilise listeUtilite1 pour ne pas modifier listeUtilite
    	ensFluxF1=copy.deepcopy(sorted(ensFluxF,key=attrgetter('CP'),reverse=trueFalseTab1[k][0]))#on utilise ensFluxF1/C1 pour ne pas modifier ensFluxC/F
    	ensFluxC1=copy.deepcopy(sorted(ensFluxC,key=attrgetter('CP'),reverse=trueFalseTab1[k][1]))
    	surconsoC,Reseau=reseauDown.reseauDown(ensFluxF1,ensFluxC1,TpincementF,TpincementC,deltaTmin,listeCouple1,listeUtilite1,listeSsFlux1,deltaH,kpi,[],0)
    	surconsoCTab.append(surconsoC)
    
    """for i in range (len(listeCouple)):
    	print(str(listeCouple[i].ssFluxF)+"/"+str(listeCouple[i].ssFluxC)+"/"+str(listeCouple[i].puissE))"""
    print(len(listeCouple))
    indMinSurconsoCTab=surconsoCTab.index(min(surconsoCTab))
    ensFluxF=sorted(ensFluxF,key=attrgetter('CP'),reverse=trueFalseTab1[indMinSurconsoCTab][0])#on utilise ensFluxF1/C1 pour ne pas modifier ensFluxC/F
    ensFluxC=sorted(ensFluxC,key=attrgetter('CP'),reverse=trueFalseTab1[indMinSurconsoCTab][1])
    surconsoC,Reseau=reseauDown.reseauDown(ensFluxF,ensFluxC,TpincementF,TpincementC,deltaTmin,listeCouple,listeUtilite,listeSsFlux,deltaH,kpi,[],0)
    surconsoTot+=surconsoC
    print(len(listeCouple))
    """for i in range (len(listeCouple)):
    	print(str(listeCouple[i].ssFluxF)+"/"+str(listeCouple[i].ssFluxC)+"/"+str(listeCouple[i].puissE))"""
    
    
    print("surconsoTot : "+str(surconsoTot))
    
    
    
    
    
    
    
    
    
    
    
    
    
    #Affichage du réseau final
    Donnees.donnees1(ensFlux1,deltaTmin)
    
    print("")
    
    print("Puissance de l'utilité chaude = "+str(round(deltaH[0],1))+" kW")
    print("Puissance de l'utilité froide = "+str(round(deltaH[int(len(deltaH)-1)],1))+" kW")
    print("Puissance échangée entre les flux = "+str(round(EnergEch,1))+" kW")
    
    print("")
    
    print("\nLa température de pincement: " + str(Tpincement) + "°C")
    print("La température chaude de pincement: " + str(TpincementC) + "°C")
    print("La température froide de pincement: " + str(TpincementF) + "°C")
    print("")
    
    
    
    print("\nRéseau d'échangeurs au-dessus du pincement : ("+str(trueFalseTab[indMinSurconsoFTab])+")")
    for i in range(len(Reseau1)):
    	print(Reseau1[i])
    print(surconsoFTab)
    
    print("")
    print("\nRéseau d'échangeurs en-dessous du pincement :("+str(trueFalseTab1[indMinSurconsoCTab])+")")
    for i in range(len(Reseau)):
    	print(Reseau[i])
    print(surconsoCTab)

    #Création de l'objet réseau
    
    print("kpi1.mer : "+str(kpi1.mer))
    #on supprime les utilités qui ne sont appliqués à des flux qui n'ont pas besoin d'être refroidi (attribut process = False)
    supUtilite=[]
    for k in range(len(listeUtilite)):
    	if listeUtilite[k].ssFlux.objFlux.process==False:#on ne peut pas modifier la valeur du MER car si il n'y a que des ssFlux.process=False, on divisera par 0 lorsqu'on calculera le prctMER
    		supUtilite.append(listeUtilite[k].ssFlux)
    
    for k in range(len(supUtilite)):
    	for p in range(len(listeUtilite)):
    		if supUtilite[k]==listeUtilite[p].ssFlux:
    			listeUtilite.remove(listeUtilite[p])
    			break
    
    
    
    
    kpi1.prctMer=surconsoTot/kpi1.mer#donne la puissance des utilités dépassant le MER en pourcentage
    if abs(kpi1.prctMer)<10**(-10):
    	kpi1.prctMer=0
    kpi1.nbUti=len(listeUtilite)
    kpi1.nbEch=len(listeCouple)
    
    reseauFinal=reseau.reseau(listeCouple,listeUtilite,kpi1,listeSsFlux,ensFluxInit, TpincementC, TpincementF)
    
    for i in range(len(ensFluxC)):#on ajoute à ensFluxInit la liste des sous-flux chaud du dessous
    	for k in range(len(ensFluxInit)):
    		if ensFluxInit[k].type=="c":
    			if ensFluxC[i].numero==ensFluxInit[k].numero:
    				ensFluxInit[k].listeSsFlux+=ensFluxC[i].listeSsFlux
    
    for j in range(len(ensFluxF)):#on ajoute à ensFluxInit la liste des sous-flux froid du dessous
    	for k in range(len(ensFluxInit)):
    		if ensFluxInit[k].type=="f":
    			if ensFluxF[j].numero==ensFluxInit[k].numero:
    				ensFluxInit[k].listeSsFlux+=ensFluxF[j].listeSsFlux
    
    for k in range(len(ensFluxInit)):#classement des sous-Flux de chaque flux par ordre, attribution de la valeur des tuples, puis ajout au réseau
    	
    	if ensFluxInit[k].type=="c":#classement
    		valReverse=True
    	else:
    		valReverse=False
    	ensFluxInit[k].listeSsFlux=sorted(ensFluxInit[k].listeSsFlux,key=attrgetter('Te'),reverse=valReverse)
    	print(len(ensFluxInit[k].listeSsFlux))
    	if len(ensFluxInit[k].listeSsFlux)!=0:
    		ensFluxInit[k].listeSsFlux[len(ensFluxInit[k].listeSsFlux)-1].refEch=False#permet de notifier qu'il s'agit du dernier sous-flux de chaque flux
    
    	valTuple=0#tuple
    	for l in range(len(ensFluxInit[k].listeSsFlux)):
    		ensFluxInit[k].listeSsFlux[l].refFlux=(ensFluxInit[k].numero,valTuple)
    		valTuple+=1
    
    	reseauFinal.listeSsFlux+=ensFluxInit[k].listeSsFlux#ajout dans le réseau
    
    for k in range(len(listeCouple)):#on remplace le sous-flux par sa refFlux
    	listeCouple[k].ssFluxF=listeCouple[k].ssFluxF.refFlux
    	listeCouple[k].ssFluxC=listeCouple[k].ssFluxC.refFlux
    
    for k in range(len(listeUtilite)):#on remplace le sous-flux par sa refFlux
    	listeUtilite[k].ssFlux=listeUtilite[k].ssFlux.refFlux
    
    print("len(listeUtilite) : "+str(len(listeUtilite)))
    reseauFinal.listeCouple=listeCouple#on met à jour le reseau final avec la nouvelle liste de couple
    reseauFinal.listeUtilite=listeUtilite#on met à jour le reseau final avec la nouvelle liste d'utilite
    
    
    numSsFluxSup=[]
    numSsFlux=reseauFinal.listeSsFlux[0].refFlux[0]
    for i in range(len(reseauFinal.listeSsFlux)):#on supprime les utilités froide des flux chauds dont le refroidissement n'est pas nécessaire au process
    	if reseauFinal.listeSsFlux[i].refFlux[0]!=numSsFlux:#cela voudra dire que le flux précédent était le dernier de la liste de sous-flux du flux précédent
    		if reseauFinal.listeSsFlux[i-1].typeFlux=="c":
    			if reseauFinal.listeSsFlux[i-1].objFlux.process==False:
    				numSsFluxSup.append(reseauFinal.listeSsFlux[i-1])
    				reseauFinal.listeSsFlux[i-2].refEch=False #comme on supprime le dernier flux, l'avant dernier flux est celui qui porte l'attribut False pour refEch
    		numSsFlux=reseauFinal.listeSsFlux[i].refFlux[0]
    
    for i in range(len(numSsFluxSup)):
    	for j in range(len(reseauFinal.listeSsFlux)):
    		if numSsFluxSup[i]==reseauFinal.listeSsFlux[j]:
    			reseauFinal.listeSsFlux.remove(reseauFinal.listeSsFlux[j])
    			break
    
    

    puissEch=0
    for i in range(len(reseauFinal.listeSsFlux)):
        print(str(reseauFinal.listeSsFlux[i].refFlux)+"/"+str(reseauFinal.listeSsFlux[i].objFlux.nom)+"/ Te :"+str(reseauFinal.listeSsFlux[i].Te)+"/ Ts :"+str(reseauFinal.listeSsFlux[i].Ts)+"/ "+str(reseauFinal.listeSsFlux[i].typeFlux)+"/ "+str(reseauFinal.listeSsFlux[i].estDivise)+"/ "+str(reseauFinal.listeSsFlux[i].utilite)+"/ échange encore ?"+str(reseauFinal.listeSsFlux[i].refEch))
#    print("Liste couple : ")
    for i in range (len(listeCouple)):
    	print(str(reseauFinal.listeCouple[i].ssFluxF)+"/"+str(reseauFinal.listeCouple[i].ssFluxC)+"/"+str(reseauFinal.listeCouple[i].puissE))
    	puissEch+=reseauFinal.listeCouple[i].puissE
#    print("")
#    print("Liste Utilité : ")
    utiliteTotC=0
    utiliteTotF=0
    for i in range (len(listeUtilite)):
    	print(str(reseauFinal.listeUtilite[i].ssFlux)+"/"+str(reseauFinal.listeUtilite[i].puissE)+"/"+str(reseauFinal.listeUtilite[i].typeUtil))
    	if listeUtilite[i].typeUtil=="c":
    		utiliteTotC+=listeUtilite[i].puissE
    	else:
    		utiliteTotF+=listeUtilite[i].puissE

    ##### Recherche de l'erreur donnant le NAN #####
    # listeCouplebis = sorted(listeCouple, key = attrgetter('puissE'), reverse = True)
    # for cple in listeCouplebis :
    #     print(cple.TeC, cple.TsC, cple.TeF, cple.TsF)
    #     print("DTE : ", cple.TeC-cple.TsF, " - DTS : ", cple.TsC-cple.TeF)
    #     print("DTM : ", (cple.TsC-cple.TeF-cple.TeC+cple.TsF)/(np.log((cple.TsC-cple.TeF)/(cple.TeC-cple.TsF))))
    #     if math.isnan((cple.TsC-cple.TeF-cple.TeC+cple.TsF)/(np.log((cple.TsC-cple.TeF)/(cple.TeC-cple.TsF)))) :
    #         print(cple.ssFluxF[0], cple.ssFluxC[0])

    ##### Couples avec TeC < TeS ????? #####
    # listeCouplebis = sorted(listeCouple, key = attrgetter('puissE'), reverse = True)
    # compt = 0
    # for cple in listeCouplebis :
    #     compt += 1
    #     print("Températures chaudes : ", cple.TeC, cple.TsC)
    #     if (cple.TeC <= cple.TsC) :
    #         print("PROBLEME TEMPERATURES CHAUDES")
    #     print("Températures froides : ", cple.TeF, cple.TsF)
    #     if (cple.TeF >= cple.TsF) :
    #         print("PROBLEME TEMPERATURES FROIDES")
    # print(compt)

    ########################################################################################
    ##### LOI 80% ECHANGEUR : Recherche des flux qui échangent 80% de l'énergie totale #####
    ########################################################################################

    # print(listeCouple)
    # print("Longueur de listeCouple : ",len(listeCouple))
    # print(setCouple)
    # print("Longueur de setCouple : ",len(setCouple))

    listeCouplebis = sorted(listeCouple, key = attrgetter('puissE'), reverse = True)
    listeCouple_puiss = [couple.puissE for couple in listeCouplebis] #contient les puissances échangées de chaque couple
    #print(listeCouple_puiss)
    print(puissEch) #puissance totale échangée
    print(sum(listeCouple_puiss)) #doit être égale à la puissance totale échangée puissEch

    listeCouple_energprct = [(listeCouple_puiss[i] / puissEch) for i in range (len(listeCouple_puiss))] #contient le pourcentage d'énergie échangée par le couple sur la puissance échangée totale
    #print(listeCouple_energprct)
    print(sum(listeCouple_energprct)) #doit être égale à 1 = 100%
    print("---Le nombre de couples est de---", len(listeCouplebis))

    comptprct = 0
    comptnbrcouple = 0
    comptpuiss = 0
    fluxphyschaudmax = []
    fluxphysfroidmax = []
    for i in range (0, len(listeCouplebis)) :
        if comptprct < 0.8 :
            comptprct += listeCouple_energprct[i]
            comptnbrcouple += 1
            comptpuiss += listeCouplebis[i].puissE
            fluxphysfroidmax.append(listeCouplebis[i].ssFluxF[0]) #on ajoute les références des flux froids et chauds 
            fluxphyschaudmax.append(listeCouplebis[i].ssFluxC[0])

    print(fluxphyschaudmax)
    print(fluxphysfroidmax)
    fluxphyschaudmax = sorted(set(fluxphyschaudmax))
    fluxphysfroidmax = sorted(set(fluxphysfroidmax))
    print("Les références des flux chauds échangeant 80% de l'énergie totale sont : ", fluxphyschaudmax)
    print("Les références des flux froids échangeant 80% de l'énergie totale sont : ", fluxphysfroidmax)
    # fluxphyschaudmax = set(fluxphyschaudmax) #pour supprimer les doublons
    # fluxphysfroidmax = set(fluxphysfroidmax) #pour supprimer les doublons
    # print(fluxphyschaudmax)
    # print(fluxphysfroidmax)
    print(comptprct)
    print(comptnbrcouple)
    print(comptpuiss)

    print("Ces flux échangent ", round(comptprct*100, 2), "% de l'énergie totale")
    print("Soit ", round(comptpuiss, 2), "kW sur un total de ", round(puissEch, 2), "kW")



    ########################################################################################
    ##### LOI 80% FLUX : Recherche des flux qui échangent 80% de l'énergie totale ##########
    ########################################################################################

    # listeCouplebis = sorted(listeCouple, key = attrgetter('puissE'), reverse = True)
    # listeCouple_puiss = [couple.puissE for couple in listeCouplebis] #contient les puissances échangées de chaque couple
    # listefluxchaud = [] #contient les flux chauds pour tous les couples
    # listefluxfroid = [] #contient les flux froids pour tous les couples
    # prctfluxchaud = [0]*len(listefluxchaud) #contient les prct d'énergie échangée par les couples pour les flux chauds
    # prctfluxfroid = [0]*len(listefluxfroid) #contient les prct d'énergie échangée par les couples  pour les flux froids

    # for cple in listeCouplebis :
    #     listefluxchaud.append(cple.ssFluxC[0])
    #     listefluxfroid.append(cple.ssFluxF[0])
    #     prctfluxchaud.append((cple.puissE)/puissEch*100)
    #     prctfluxfroid.append((cple.puissE)/puissEch*100)
    
    # # print(prctfluxchaud, sum(prctfluxchaud))
    # # print(prctfluxfroid, sum(prctfluxfroid))

    # listefluxchaud2 = sorted(set(listefluxchaud)) #contient les num des flux chauds par ordre croissant
    # listefluxfroid2 = sorted(set(listefluxfroid)) #contient les num des flux froids par ordre croissant
    # prctfluxchaud2 = [0]*len(listefluxchaud2) #contient les prct associés aux flux chauds
    # prctfluxfroid2 = [0]*len(listefluxfroid2) #contient les prct associés aux flux froids

    # for i in range (0, len(listefluxchaud)) :
    #     numfluxchaud = listefluxchaud[i]
    #     prctfluxchaud2[numfluxchaud-1] += prctfluxchaud[i]

    # for j in range (0, len(listefluxfroid)) :
    #     numfluxfroid = listefluxfroid[j]
    #     prctfluxfroid2[numfluxfroid-1] += prctfluxfroid[j]

    # # print("Liste des flux chauds : ", listefluxchaud)
    # # print("Liste des flux froids : ", listefluxfroid)
    # print("Set des flux chauds trié: ", listefluxchaud2)
    # print("Set des flux froids trié: ", listefluxfroid2)
    # print("Prct pour chaque flux chaud : ", prctfluxchaud2)
    # print("Prct pour chaque flux froid : ", prctfluxfroid2)

    # # liste_fluxetprctchaud = [(0,0)]*len(prctfluxchaud2)
    # # liste_fluxetprctfroid = [(0,0)]*len(prctfluxfroid2)
    # # for i in range (0,len(prctfluxchaud2)) :
    # #     liste_fluxetprctchaud.append(((i+1), prctfluxchaud2[i]))
    # # for j in range (0, len(prctfluxfroid2)) :
    # #     liste_fluxetprctfroid.append((j+1), prctfluxfroid2[j])

    # ##### Etape intermédiaire pour associer les bons flux aux pourcentages triés par ordre décroissant #####
    # interchaud = []
    # interfroid = []
    # for i in range (0, len(listefluxchaud2)) :
    #     interchaud.append((listefluxchaud2[i], prctfluxchaud2[i]))

    # for j in range (0, len(listefluxfroid2)) :
    #     interfroid.append((listefluxfroid2[j], prctfluxfroid2[j]))
    # # print("INTERCHAUD : ", interchaud)
    # # print("INTERFROID : ", interfroid)
    # interchaud = sorted(interchaud, key = itemgetter(1), reverse = True)
    # interfroid = sorted(interfroid, key = itemgetter(1), reverse = True)
    # # print("INTERCHAUD TRIEE : ", interchaud)
    # # print("INTERFROID TRIEE : ", interfroid)

    # ##### Tri des listes de pourcentage et création des listes avec les pourcentages sommés #####
    # # tempchaud = sorted(prctfluxchaud2, reverse = True) #listes temporaires qui contiennent les valeurs des prct triées par ordre croissant
    # # tempfroid = sorted(prctfluxfroid2, reverse = True)

    # listesommeprctchaud = [0]*len(prctfluxchaud2) #listes qui contiennent les prct sommés triés par ordre croissant
    # listesommeprctfroid = [0]*len(prctfluxfroid2)
    # listesommeprctchaud[0] = interchaud[0][1]
    # listesommeprctfroid[0] = interfroid[0][1]

    # # print("LISTE TEMP CHAUD : ", tempchaud, sum(tempchaud))
    # # print("LISTE TEMP FROID : ", tempfroid, sum(tempfroid))
    # for i in range (1, len(prctfluxchaud2)) :
    #     listesommeprctchaud[i] = listesommeprctchaud[i-1] + interchaud[i][1]
    # for j in range (1, len(prctfluxfroid2)) :
    #     listesommeprctfroid[j] = listesommeprctfroid[j-1] + interfroid[j][1]
    # # print("LISTESOMMEPRCT CHAUD : ", listesommeprctchaud)
    # # print("LISTESOMMEPRCT FROID : ", listesommeprctfroid)


    # liste_fluxetprctchaud = []
    # liste_fluxetprctfroid = []
    # for i in range (0, len(listefluxchaud2)) :
    #     liste_fluxetprctchaud.append((interchaud[i][0], interchaud[i][1], listesommeprctchaud[i]))
    # for j in range (0, len(listefluxfroid2)) :
    #     liste_fluxetprctfroid.append((interfroid[j][0], interfroid[j][1], listesommeprctfroid[j]))

    # # print(liste_fluxetprctchaud)
    # # print(liste_fluxetprctfroid)
    # # liste_fluxetprctchaud = sorted(liste_fluxetprctchaud, key = itemgetter(1), reverse = True)
    # # liste_fluxetprctfroid = sorted(liste_fluxetprctfroid, key = itemgetter(1), reverse = True)
    # print("FLUX CHAUDS (num, prct, sommeprct) : ", liste_fluxetprctchaud)
    # print("FLUX FROIDS (num, prct, sommeprct) : ", liste_fluxetprctfroid)

    # # liste_fluxetprctchaud[0][2] = liste_fluxetprctchaud[0][1] #initialisation chaud
    # # liste_fluxetprctfroid[0][2] = liste_fluxetprctfroid[0][1] #initialisation froid
    # # for i in range (1, len(liste_fluxetprctchaud)) :
    # #     liste_fluxetprctchaud[i][2] = liste_fluxetprctchaud[i-1][2] + liste_fluxetprctchaud[i][1] #hérédité chaud
    # # for j in range (1, len(liste_fluxetprctfroid)) :
    # #     liste_fluxetprctfroid[i][2] = liste_fluxetprctfroid[i-1][2] + liste_fluxetprctfroid[i][1] #hérédité froid

    # # print(liste_fluxetprctchaud)
    # # print(liste_fluxetprctfroid)

    # ##############################################################################################
    # ##### LOI 80% ECHANGEUR : Recherche des échangeurs qui échangent 80% de l'énergie totale #####
    # ##############################################################################################

    # print("ListeCouple triée par puissance : ", listeCouplebis)
    # listetriparech = [0] #liste de la forme [(fluxchaud, fluxfroid, puissance)]
    # for cpletri in listeCouplebis :
    #     listetriparech.append((cpletri.ssFluxC[0], cpletri.ssFluxF[0], cpletri.puissE, cpletri.puissE/puissEch))
    # print(listetriparech)



    return reseauFinal
