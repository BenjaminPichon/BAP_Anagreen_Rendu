# -*- coding: utf-8 -*-
"""
Created on mars 11 

@author: p-aToussaint
"""

# -*- coding: utf-8 -*-
#"""

#Les exemples sont tirés du livre "Pinch Analysis and process integration" de Ian C.Kemp

import matplotlib.pyplot as plt

from classes import Flux

def MERCont(ensFlux,deltaTmin):
    for i in range(len(ensFlux)):#transforme le jeu de données de string à float (car opérations sur les températures)
        ensFlux[i].Te=float(ensFlux[i].Te)
        ensFlux[i].Ts=float(ensFlux[i].Ts)
        ensFlux[i].CP=float(ensFlux[i].CP)

    for i in range(len(ensFlux)):#donne les températures décalées (utile pour la GCC)
        if ensFlux[i].type=="c":
            ensFlux[i].Te-=deltaTmin/2
            ensFlux[i].Ts-=deltaTmin/2
        else:
            ensFlux[i].Te+=deltaTmin/2
            ensFlux[i].Ts+=deltaTmin/2

    #Récupération des températures de chaque flux dans une liste 
    temp = []
    for i in range(len(ensFlux)):
        temp.append(ensFlux[i].Te)
        temp.append(ensFlux[i].Ts)
    temp=list(set(temp)) #supprimer les doublons
    temp.sort() #trier par ordre croissant

    #Définition des intervalles de températures grâce à la liste de température des flux
    interTemp=[]
    for i in range(len(temp)-1):
        interTemp.append(temp[i+1]-temp[i])

    #Calcul de la différence des capacités thermiques des fluides chauds et froids pour chaque intervalle
    capa=[0]*(len(temp)-1) #création d'une liste composée de 1 et de la taille de la liste "temp" 
    for j in range(len(temp)-1):#pour chaque intervalle de température on regarde quel flux est compris dedans
        for i in range(len(ensFlux)):
            if ensFlux[i].type == "f": #on sépare le cas f et c car quand Te=temp[j], s'il s'agit d'un fluide f alors il est contenu dans l'intervalle puisque sa tempéture augmente, mais le fluide c n'est pas dedans car sa température diminue
                if (ensFlux[i].Te == temp[j]) or (ensFlux[i].Ts == temp[j+1]) or (ensFlux[i].Te < temp[j] and ensFlux[i].Ts > temp[j+1]):#Soit le fluide marque le début, soit la fin d'un intervalle, soit l'intervalle est compris dans sa gamme de température
                    capa[j]-=ensFlux[i].CP
            else:
                if (ensFlux[i].Ts == temp[j]) or (ensFlux[i].Te == temp[j+1]) or (ensFlux[i].Te > temp[j+1] and ensFlux[i].Ts < temp[j]):
                    capa[j]+=ensFlux[i].CP

    #Calcul deltaHi
    deltaHi=[1]*(len(temp)-1)
    for i in range(len(temp)-1):
        deltaHi[i]=float(capa[i])*float(interTemp[i])
    deltaHi.reverse()

    #Cascade d'énergie sans apport de chaleur
    deltaH=[]
    deltaH.append(0)
    for i in range(len(temp)-1):
        deltaH.append(deltaH[i]+deltaHi[i])
    print("Cascade d'énergie sans ajout de chaleur : ", end="") #end = "" évite le retour à la ligne
    print(deltaH)
        
    #Cascade d'énergie avec apport de chaleur
    minDeltaH=min(deltaH)
    for i in range(len(temp)):
        deltaH[i]-=minDeltaH
    print("Cascade d'énergie avec ajout de chaleur : ", end="")
    print(deltaH)

    #Calcul de l'énergie échangée entre les flux
    chargeThF=0
    for i in range(len(ensFlux)):
        if ensFlux[i].type =="f":
            chargeThF+=ensFlux[i].CP*abs((ensFlux[i].Te-ensFlux[i].Ts))
    EnergEch=chargeThF-deltaH[0]#on soustrait l'énergie demandé par les fluides froids à la puissance de l'utilité chaude


    #Affichage résultats
    print("Puissance de l'utilité chaude = "+str(round(deltaH[0],1))+" kW")
    print("Puissance de l'utilité froide = "+str(round(deltaH[int(len(deltaH)-1)],1))+" kW")
    print("Puissance échangée entre les flux = "+str(round(EnergEch,1))+" kW")

    #Tracé de la grande courbe composite
    """
    for i in range(6):	
        deltaH[i]=float(deltaH[i])
    temp.reverse()
    plt.title("Grande Courbe Composite")
    plt.plot(deltaH,temp)
    plt.xlabel("Puissance(kW)")
    plt.ylabel("Température(°C)")
    plt.show()
    temp.reverse()"""

    for i in range(len(ensFlux)):#retour aux températures non-décalées
        if ensFlux[i].type=="c":
            ensFlux[i].Te+=deltaTmin/2
            ensFlux[i].Ts+=deltaTmin/2
        else:
            ensFlux[i].Te-=deltaTmin/2
            ensFlux[i].Ts-=deltaTmin/2

    return(deltaH,temp,EnergEch,deltaH[0],deltaH[int(len(deltaH)-1)])
    




