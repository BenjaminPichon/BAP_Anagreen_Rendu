# -*- coding: utf-8 -*-
"""
Created on april 29 

@author: p-aToussaint
"""
import matplotlib.pyplot as plt
from operator import itemgetter, attrgetter
import copy

from creation_reseau_statique import Division,Fct
from classes import Flux,ssFlux,couple,reseau


def testDiv(ensFlux,i):
    if ensFlux[i].div>0:
        return True
    else:
        return False

def echA(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,p,m,CPbrF,ech,CP,bclDiv,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple):#Pour flux chaud divisé. Calcul la puissance de l'échange et vérifie la condition des deltaTmin
    ########## Liste des échangeurs que l'on souhaite avoir ##########
    #La liste est une liste de tuples de la forme (numfluxchaud, numfluxfroid)
    # Liste_echangeur = [(5,5), (4,3), (4,4), (5,6), (1,1), (1,2)]
    # print("Liste des échangeurs que l'on souhaite : ", Liste_echangeur)
    # print("On souhaite donc ", len(Liste_echangeur), " échangeurs")
    # possibilite = (ensFluxC[p].numero, ensFluxF[m].numero)
    # if possibilite in Liste_echangeur :
    print(ensFluxC[p].Ts1)
    print(ensFluxC[p].Ts)
    print(TpincementC)
    TsC=max(TpincementC,ensFluxC[p].Ts,ensFluxC[p].Ts1)#le but est que les fluides froids atteignent la température de pincementF. Et que le refroidissement des fluides chauds se fasse à la température la plus faible. 
    TeF=max(TpincementF,ensFluxF[m].Te)
    TeC=TsC+puissE/ensFluxC[p].CP
    TsF=TeF+puissE/CPbrF
    # print("TpincementF :"+str(TpincementF))
    # print("ensFluxF[m].Te : "+str(ensFluxF[m].Te))
    print("TeC : " +str(TeC))
    print("TsC : " +str(TsC))
    print("TeF : " +str(TeF))
    print("TsF : " +str(TsF))
    if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
        if bclDiv!="oui":
            print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrF : "+str(CPbrF))
            Reseau1.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrF : "+str(round(CPbrF,3)))
            ssFluxC=ssFlux.ssFlux(TeC,TsC,ensFluxC[p].CP*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
            ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
            ensFluxC[p].listeSsFlux.append(ssFluxC)
            ensFluxF[m].listeSsFlux.append(ssFluxF)
            listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
        ech+=1
        ensFluxC[p].chargeThA-=puissE
        ensFluxF[m].chargeThA-=puissE
        ensFluxC[p].pinc="oui"
        ensFluxC[p].Ts=TeC
        #print(ensFluxC[p].div)
        if ensFluxF[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
            #print("TE===TSC")
            ensFluxF[m].Te=TsF
        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
            ensFluxF[m].ech="oui"
            if bclDiv!="oui" and ensFluxF[m].div!=0.5:
                CP[m]=CP[m]*2
            if bclDiv!="oui" and ensFluxF[m].div==0.5:
                ensFluxF[m].test=[]
                ensFluxF[m].verif=0
                ensFluxF[m].ech="non"
                if ensFluxF[m].chargeThA!=0:    
                    CP[m]=ensFluxF[m].CP
            if ensFluxF[m].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                ensFluxF[m].div-=0.5
                ensFluxF[m].Te=TsF
            else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                ensFluxF[m].div-=0.5
    else:#prend en compte que l'échange peut-être inférieure à la charge Th d'un des flux (car sinon la condition deltaTmin n'est pas respectée)
        print("else")
        if ensFluxF[m].Te<ensFluxC[p].Te:
            if TeC<=TeF+deltaTmin:
                print("PB : TeC<=TeF+deltaTmin")
                #on ne va donc plus chercher à amener le fluide chaud à la température de pincement mais on va partir de sa température d'entrée 
                print("ensFluxC[p].Te : "+str(ensFluxC[p].Te))
                print("ensFluxF[m].Te : "+str(ensFluxF[m].Te))
                TeC=ensFluxC[p].Te
                TsC=ensFluxF[m].Te+deltaTmin
                puissE=min(ensFluxF[m].chargeThA,(TeC-TsC)*ensFluxC[p].CP)
                if puissE==ensFluxF[m].chargeThA:#cela voudra dire qu'imposer une TsF à deltaTmin de l'entrée du fluide chaud implique que le fluide chaud ne peut pas fournir la chaleur demandé par le fluide froid. Ainsi, si le fluide chaud ne peut pas fournir plus, on recalcule quelle T va atteindre le fluide froid avec cette puissance
                    TsC=TeC-puissE/ensFluxC[p].CP
                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                    if bclDiv!="oui":
                        print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrF : "+str(CPbrF))
                        Reseau1.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrF : "+str(round(CPbrF,3)))
                        ssFluxC=ssFlux.ssFlux(TeC,TsC,ensFluxC[p].CP*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                        ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                        ensFluxC[p].listeSsFlux.append(ssFluxC)
                        ensFluxF[m].listeSsFlux.append(ssFluxF)
                        listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))                   
                    ensFluxF[m].chargeThA-=puissE
                    ensFluxC[p].chargeThA-=puissE
                    ensFluxC[p].pinc="oui"
                    ensFluxC[p].Te=TsC
                    ech+=1
                    #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                    if ensFluxF[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                        ensFluxF[m].Te=TsF
                    else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                        ensFluxF[m].ech="oui"
                        if bclDiv!="oui" and ensFluxF[m].div!=0.5:
                            CP[m]=CP[m]*2
                        if bclDiv!="oui" and ensFluxC[p].div==0.5:
                            ensFluxF[m].test=[]
                            ensFluxF[m].verif=0
                            ensFluxF[m].ech="non"
                            if ensFluxF[m].chargeThA!=0:    
                                CP[m]=ensFluxF[m].CP
                        if ensFluxF[m].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                            ensFluxF[m].div-=0.5
                            ensFluxF[m].Te=TsF
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            ensFluxF[m].div-=0.5
                return(ech,CP)
            if TeC<(TsF+deltaTmin):#hypothèse : "la chargeTh minimale est celle du fluide froid". On va réduire la température de sortie du flux froid. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                print("echA-stop1")
                
                TeC=ensFluxC[p].Te#car sinon TeF est égal à la valeur calculé dans la 1ère boucle
                if ensFluxF[m].verif==0:#car si verif!=0, alors on va modifier la Ts du flux chaud alors que celle-ci doit être fixe puisque la fin des branches d'un flux divisé doivent avoir la même température
                    TsF=min(ensFluxF[m].Ts,TeC-deltaTmin)
                puissE=(TsF-TeF)*CPbrF
                TsC=max(ensFluxC[p].Ts,TeC-puissE/ensFluxC[p].CP)
                
                
                
                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                    #print("stop")
                    if bclDiv!="oui":
                        print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrF : "+str(CPbrF))
                        Reseau1.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrF : "+str(round(CPbrF,3)))
                        ssFluxC=ssFlux.ssFlux(TeC,TsC,ensFluxC[p].CP*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                        ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                        ensFluxC[p].listeSsFlux.append(ssFluxC)
                        ensFluxF[m].listeSsFlux.append(ssFluxF)
                        listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))                
                    ensFluxC[p].chargeThA-=puissE
                    ensFluxF[m].chargeThA-=puissE
                    ensFluxC[p].pinc="oui"
                    ensFluxC[p].Te=TsC
                    #print(ensFluxF[m].Te)
                    ech+=1
                    #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                    if ensFluxF[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                        ensFluxF[m].Te=TsF
                    else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                        ensFluxF[m].ech="oui"
                        if bclDiv!="oui" and ensFluxF[m].div!=0.5:
                            CP[m]=CP[m]*2
                        if bclDiv!="oui" and ensFluxF[m].div==0.5:
                            ensFluxF[m].test=[]
                            ensFluxF[m].verif=0
                            ensFluxF[m].ech="non"
                            if ensFluxF[m].chargeThA!=0:    
                                CP[m]=ensFluxF[m].CP
                        if ensFluxF[m].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                            ensFluxF[m].div-=0.5
                            ensFluxF[m].Te=TsF
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            ensFluxF[m].div-=0.5
            if TsC<(TeF+deltaTmin):# TsC<(TeF+deltaTmin) / hypothèse : la chargeTh minimale est celle du fluide froid / on va augmenter la température de sortie du fluide chaud. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                print("echA-stop2")
                TsC=TeF+deltaTmin
                #if TeC<ensFluxC[p].Te:
                TeC=ensFluxC[p].Te
                if ensFluxF[m].verif!=0:#car si toute les branches du flux n'ont pas fini d'être satisfaite alors on doit se baser sur son b
                    puissE=min(puissE,(TeC-TsC)*ensFluxC[p].CP)
                else:
                    print("verif=0")
                    print(TeC)
                    print(TsC)
                    print(ensFluxC[p].CP)
                    print((TeC-TsC)*ensFluxC[p].CP)
                    print(ensFluxF[m].chargeThA)
                    puissE=min(ensFluxF[m].chargeThA,(TeC-TsC)*ensFluxC[p].CP)
                TsF=TeF+puissE/CPbrF
                if puissE==ensFluxF[m].chargeThA:#cela voudra dire qu'imposer une TsF à deltaTmin de l'entrée du fluide chaud implique que le fluide chaud ne peut pas fournir la chaleur demandé par le fluide froid. Ainsi, si le fluide chaud ne peut pas fournir plus, on recalcule quelle T va atteindre le fluide froid avec cette puissance
                    print("puissE==ensFluxF[m].chargeThA")
                    #TeC=min(ensFluxC[p].Te,TsF+deltaTmin) #Midrex boite noire V3
                    TsC=TeC-puissE/ensFluxC[p].CP
                print("TeC : " +str(TeC))
                print("TsC : " +str(TsC))
                print("TeF : " +str(TeF))
                print("TsF : " +str(TsF))
                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                    if bclDiv!="oui":
                        print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrF : "+str(CPbrF))
                        Reseau1.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrF : "+str(round(CPbrF,3)))
                        ssFluxC=ssFlux.ssFlux(TeC,TsC,ensFluxC[p].CP*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                        ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                        ensFluxC[p].listeSsFlux.append(ssFluxC)
                        ensFluxF[m].listeSsFlux.append(ssFluxF)
                        listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
                    print("échange")
                    ensFluxC[p].chargeThA-=puissE
                    ensFluxF[m].chargeThA-=puissE
                    ensFluxC[p].pinc="oui"
                    ensFluxC[p].Te=TsC
                    ech+=1
                    #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                    if ensFluxF[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                        ensFluxF[m].Te=TsF
                    else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                        ensFluxF[m].ech="oui"
                        if bclDiv!="oui" and ensFluxF[m].div!=0.5:
                            CP[m]=CP[m]*2
                        if bclDiv!="oui" and ensFluxF[m].div==0.5:
                            ensFluxF[m].test=[]
                            ensFluxF[m].verif=0
                            ensFluxF[m].ech="non"
                            if ensFluxF[m].chargeThA!=0:    
                                CP[m]=ensFluxF[m].CP
                        if ensFluxF[m].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                            ensFluxF[m].div-=0.5
                            ensFluxF[m].Te=TsF
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            ensFluxF[m].div-=0.5
    return(ech,CP)
    # else : 
    #     return(ech,CP)





def echA1(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,p,m,CPbrF,CPbrC,ech,bclDiv,CP,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple):#Pour flux chaud et froid divisé. Calcul la puissance de l'échange et vérifie la condition des deltaTmin
        ########## Liste des échangeurs que l'on souhaite avoir ##########
    #La liste est une liste de tuples de la forme (numfluxchaud, numfluxfroid)
    # Liste_echangeur = [(5,5), (4,3), (4,4), (5,6), (1,1), (1,2)]
    # print("Liste des échangeurs que l'on souhaite : ", Liste_echangeur)
    # print("On souhaite donc ", len(Liste_echangeur), " échangeurs")
    # possibilite = (ensFluxC[p].numero, ensFluxF[m].numero)
    # if possibilite in Liste_echangeur :
    TeF=max(TpincementF,ensFluxF[m].Te)
    TsF=TeF+puissE/CPbrF     
    if ensFluxC[p].echChargeTh=="non":#si on échange pas toute la charge Th alors le flux chaud démare de sa Te pour atteindre une certaine température de sortie
        TeC=ensFluxC[p].Te
        TsC=TeC-puissE/CPbrC
    else:#si on échange toute la charge Th du flux chaud, on l'amène à sa température de sortie
        TsC=max(TpincementC,ensFluxC[p].Ts)#le but est que les fluides froids atteignent la température de pincementF. Et que le refroidissement des fluides chauds se fasse à la température la plus faible. 
        TeC=TsC+puissE/CPbrC
    print(puissE)
    print(CPbrC)
    print(CPbrF)
    print(TeC)
    print(TsC)
    print(TeF)
    print(TsF)
    if round(CPbrC,10)<=round(CPbrF,10) or ensFluxC[p].Ts>TpincementC:
        if round(TeC,10)>=round((TsF+deltaTmin),10) and round(TsC,10)>=round(TeF+deltaTmin,10):#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
            ensFluxC[p].chargeThA-=puissE
            ensFluxF[m].chargeThA-=puissE
            if bclDiv!="oui":
                print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC)+" - CPbrF : "+str(CPbrF))
                Reseau1.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3))+" - CPbrF : "+str(round(CPbrF,3)))
                ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                ensFluxC[p].listeSsFlux.append(ssFluxC)
                ensFluxF[m].listeSsFlux.append(ssFluxF)
                listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
            ech+=1
            if ensFluxF[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                ensFluxF[m].Te=TsF
            else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                ensFluxF[m].ech="oui"
                if bclDiv!="oui" and ensFluxF[m].div!=0.5:
                    CP[m]=CP[m]*2
                if bclDiv!="oui" and ensFluxF[m].div==0.5:
                    ensFluxF[m].test=[]
                    ensFluxF[m].verif=0
                    ensFluxF[m].ech="non"
                    if ensFluxF[m].chargeThA!=0:
                        CP[m]=ensFluxF[m].CP
                if ensFluxF[m].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                    ensFluxF[m].Te=TsF
                    ensFluxF[m].verif=0
                if bclDiv!="oui":
                    ensFluxF[m].div-=0.5########vérifier que cela est correct car on met à 0 ensFluxC.div si son div =1 
            if ensFluxC[p].div==0:
                if TeC==ensFluxC[p].Te: #car dans certain cas (divA1) on sera obliger d'avoir TeC=ensFluxC[p].Te et Ts > max(ensFluxC[p].Ts,TpincementC)
                    ensFluxC[p].Te=TsC
                else:
                    ensFluxC[p].Ts=TeC
            else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                ensFluxC[p].ech="oui"
                if ensFluxC[p].div==0.5:
                    ensFluxC[p].div-=0.5
                    if TeC==ensFluxC[p].Te: #car dans certain cas (divA1) on sera obliger d'avoir TeC=ensFluxC[p].Te et Ts > max(ensFluxC[p].Ts,TpincementC)
                        ensFluxC[p].Te=TsC
                    else:
                        ensFluxC[p].Ts=TeC
                    ensFluxC[p].pinc="oui"
                else:
                    ensFluxC[p].div-=0.5
        else:#prend en compte que l'échange peut-être inférieure à la charge Th d'un des flux (car sinon la condition deltaTmin n'est pas respectée)
            #print("else-echE1")
            if ensFluxF[m].Te<ensFluxC[p].Te:
                if TeC<=TeF+deltaTmin:
                    #print("PB : TeC<TeF+deltaTmin")
                    TeC=ensFluxC[p].Te
                    TsC=ensFluxF[m].Te+deltaTmin
                    puissE=(TeC-TsC)*ensFluxC[p].CP

                    if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                        if bclDiv!="oui":
                            print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC)+" - CPbrF : "+str(CPbrF))
                            Reseau1.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3))+" - CPbrF : "+str(round(CPbrF,3)))
                            ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                            ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                            ensFluxC[p].listeSsFlux.append(ssFluxC)
                            ensFluxF[m].listeSsFlux.append(ssFluxF)
                            listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
                        ensFluxC[p].chargeThA-=puissE
                        ensFluxF[m].chargeThA-=puissE
                        ensFluxC[p].pinc="oui"
                        ech+=1
                        #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                        if ensFluxF[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                            ensFluxF[m].Te=TsF
                        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                            ensFluxF[m].ech="oui"
                            if bclDiv!="oui" and ensFluxF[m].div!=0.5:
                                CP[m]=CP[m]*2
                            if bclDiv!="oui" and ensFluxF[m].div==0.5:
                                ensFluxF[m].test=[]
                                ensFluxF[m].verif=0
                                ensFluxF[m].ech="non"
                                if ensFluxF[m].chargeThA!=0:
                                    CP[m]=ensFluxF[m].CP
                            if bclDiv!="oui":#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                ensFluxF[m].div-=0.5
                            if ensFluxF[m].div==0.5:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                ensFluxF[m].Te=TsF
                        if ensFluxC[p].div==0:
                            ensFluxC[p].Te=TsC
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            ensFluxC[p].ech="oui"
                            if ensFluxC[p].div==0.5:
                                ensFluxC[p].div-=0.5
                                ensFluxC[p].Te=TsC
                            else:
                                ensFluxC[p].div-=0.5
                    return(ech,CP)  
                if TeC<(TsF+deltaTmin):#hypothèse : "la chargeTh minimale est celle du fluide froid". On va réduire la température de sortie du flux froid. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                    TeC=ensFluxC[p].Te#car sinon TeF est égal à la valeur calculé dans la 1ère boucle
                    if ensFluxF[m].verif==0:#car si verif!=0, alors on va modifier la Ts du flux chaud alors que celle-ci doit être fixe puisque la fin des branches d'un flux divisé doivent avoir la même température
                        TsF=min(ensFluxF[m].Ts,TeC-deltaTmin)
                    puissE=(TsF-TeF)*CPbrF
                    TsC=max(ensFluxC[p].Ts,TeC-puissE/CPbrC)
                    
                    if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                        if bclDiv!="oui":
                            print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC)+" - CPbrF : "+str(CPbrF))
                            Reseau1.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3))+" - CPbrF : "+str(round(CPbrF,3)))
                            ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                            ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                            ensFluxC[p].listeSsFlux.append(ssFluxC)
                            ensFluxF[m].listeSsFlux.append(ssFluxF)
                            listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
                        ensFluxC[p].chargeThA-=puissE
                        ensFluxF[m].chargeThA-=puissE
                        ensFluxC[p].pinc="oui"
                        ech+=1
                        #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                        if ensFluxF[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                            ensFluxF[m].Te=TsF
                        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                            ensFluxF[m].ech="oui"
                            if bclDiv!="oui" and ensFluxF[m].div!=0.5:
                                CP[m]=CP[m]*2
                            if bclDiv!="oui" and ensFluxF[m].div==0.5:
                                ensFluxF[m].test=[]
                                ensFluxF[m].verif=0
                                ensFluxF[m].ech="non"
                                if ensFluxF[m].chargeThA!=0:
                                    CP[m]=ensFluxF[m].CP
                            if bclDiv!="oui":#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                ensFluxF[m].div-=0.5
                            if ensFluxF[m].div==0.5:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                ensFluxF[m].Te=TsF
                        if ensFluxC[p].div==0:
                            ensFluxC[p].Te=TsC
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            ensFluxC[p].ech="oui"
                            if ensFluxC[p].div==0.5:
                                ensFluxC[p].div-=0.5
                                ensFluxC[p].Te=TsC
                            else:
                                ensFluxC[p].div-=0.5
                if TsC<(TeF+deltaTmin):# TsC<(TeF+deltaTmin) / hypothèse : la chargeTh minimale est celle du fluide froid / on va augmenter la température de sortie du fluide chaud. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                    if ensFluxC[p].echChargeTh=="non":
                        TsC=ensFluxC[p].tempMax
                    else:
                        TsC=max(ensFluxC[p].Ts,TeF+deltaTmin)
                    #if TeC<ensFluxC[p].Te:
                    TeC=ensFluxC[p].Te
                    puissE=min(ensFluxF[m].chargeThA,(TeC-TsC)*CPbrC)
                    TsF=TeF+puissE/CPbrF
                    if puissE==ensFluxF[m].chargeThA and puissE!=(TeC-TsC)*CPbrC:#cela voudra dire qu'imposer une TsF à deltaTmin de l'entrée du fluide chaud implique que le fluide chaud ne peut pas fournir la chaleur demandé par le fluide froid. Ainsi, si le fluide chaud ne peut pas fournir plus, on recalcule quelle T va atteindre le fluide froid avec cette puissance
                        if TeC<TsF+deltaTmin:
                            TeC=min(ensFluxC[p].Te,TsF+deltaTmin)
                        TsC=TeC-puissE/ensFluxC[p].CP
                    
                    if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                        if bclDiv!="oui":
                            print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC)+" - CPbrF : "+str(CPbrF))
                            Reseau1.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3))+" - CPbrF : "+str(round(CPbrF,3)))
                            ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                            ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                            ensFluxC[p].listeSsFlux.append(ssFluxC)
                            ensFluxF[m].listeSsFlux.append(ssFluxF)
                            listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
                        ensFluxC[p].chargeThA-=puissE
                        ensFluxF[m].chargeThA-=puissE
                        ensFluxC[p].pinc="oui"
                        ech+=1
                        #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                        if ensFluxF[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                            ensFluxF[m].Te=TsF
                        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                            ensFluxF[m].ech="oui"
                            if bclDiv!="oui" and ensFluxF[m].div!=0.5:
                                CP[m]=CP[m]*2
                            if bclDiv!="oui" and ensFluxF[m].div==0.5:
                                ensFluxF[m].test=[]
                                ensFluxF[m].verif=0
                                ensFluxF[m].ech="non"
                                if ensFluxF[m].chargeThA!=0:
                                    CP[m]=ensFluxF[m].CP
                            if bclDiv!="oui":#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                ensFluxF[m].div-=0.5
                            if ensFluxF[m].div==0.5:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                ensFluxF[m].Te=TsF
                        if ensFluxC[p].div==0:
                            ensFluxC[p].Te=TsC
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            ensFluxC[p].ech="oui"
                            if ensFluxC[p].div==0.5:
                                ensFluxC[p].div-=0.5
                                ensFluxC[p].Te=TsC
                            else:
                                ensFluxC[p].div-=0.5


    return(ech,CP)
    # else :
    #     return (ech,CP)

def echA2(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,p,m,CPbrF,CPbrC,ech,CP,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple):#égale à echE1 mais pas de condition sur les CP
    TsC=max(TpincementC,ensFluxC[p].Ts)#Le but est que les fluides chauds atteignent la température de pincementC. 
    TeF=max(TpincementF,ensFluxF[m].Te)
    TeC=TsC+puissE/CPbrC
    TsF=TeF+puissE/CPbrF
    if TeC>=(TsF+deltaTmin) and TsC>=TeF+deltaTmin:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
        ensFluxC[p].chargeThA-=puissE
        ensFluxF[m].chargeThA-=puissE
        print("Couple ech2 c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC)+" - CPbrF : "+str(CPbrF))
        Reseau1.append("Couple ech2 c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3))+" - CPbrF : "+str(round(CPbrF,3)))
        ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
        ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
        ensFluxC[p].listeSsFlux.append(ssFluxC)
        ensFluxF[m].listeSsFlux.append(ssFluxF)
        listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
        ech+=1
        if ensFluxF[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
            ensFluxF[m].Te=TsF
        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
            ensFluxF[m].ech="oui"
            CP[m]=CP[m]*2
            if ensFluxF[m].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                ensFluxF[m].div-=0.5
                ensFluxF[m].Te=TsF
            else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                ensFluxF[m].div-=0.5
        if ensFluxC[p].div==0:
            ensFluxC[p].Te=TsC
        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
            ensFluxC[p].ech="oui"
            if ensFluxC[p].div==0.5:
                ensFluxC[p].div-=0.5
                ensFluxC[p].Te=TsF
                ensFluxC[p].pinc="oui"
            else:
                ensFluxC[p].div-=0.5
    return(CP)



def echE(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,p,m,CPbrC,ech,CP,bclDiv,Reseau,ensFluxCinit,ensFluxFinit,listeCouple):#Pour flux chaud divisé. Calcul la puissance de l'échange et vérifie la condition des deltaTmin
    TeC=min(TpincementC,ensFluxC[p].Te)#le but est que les fluides froids atteignent la température de pincementF. Et que le refroidissement des fluides chauds se fasse à la température la plus faible. 
    TsF=min(TpincementF,ensFluxF[m].Ts,ensFluxF[m].Ts1)
    TsC=TeC-puissE/CPbrC
    TeF=TsF-puissE/ensFluxF[m].CP
    if ensFluxF[m].numero==11 or ensFluxF[m].numero==8 or ensFluxF[m].numero==7:
        print(ensFluxF[m].Ts)
        print(puissE)
        print(CPbrC)
        print(TeC)
        print(TsC)
        print(TeF)
        print(TsF)
    if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
        if bclDiv!="oui":
            print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC))
            Reseau.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3)))
            ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
            ssFluxF=ssFlux.ssFlux(TeF,TsF,ensFluxF[m].CP*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
            ensFluxC[p].listeSsFlux.append(ssFluxC)
            ensFluxF[m].listeSsFlux.append(ssFluxF)
            listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
        ech+=1
        ensFluxC[p].chargeThE-=puissE
        ensFluxF[m].chargeThE-=puissE
        ensFluxF[m].pinc="oui"
        ensFluxF[m].Ts=TeF
        #print(ensFluxC[p].div)
        if ensFluxC[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
            #print("TE===TSC")
            ensFluxC[p].Te=TsC
        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
            ensFluxC[p].ech="oui"
            if bclDiv!="oui" and ensFluxC[p].div!=0.5:
                CP[p]=CP[p]*2
            if bclDiv!="oui" and ensFluxC[p].div==0.5:
                ensFluxC[p].test=[]
                ensFluxC[p].verif=0
                ensFluxC[p].ech="non"
                if ensFluxC[p].chargeThE!=0:    
                    CP[p]=ensFluxC[p].CP
            if ensFluxC[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                ensFluxC[p].div-=0.5
                ensFluxC[p].Te=TsC
            else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                ensFluxC[p].div-=0.5
    else:#prend en compte que l'échange peut-être inférieure à la charge Th d'un des flux (car sinon la condition deltaTmin n'est pas respectée)
        print("else")
        if ensFluxF[m].Te<ensFluxC[p].Te:
            if TeC<=TeF+deltaTmin:
                print("PB : TeC<TeF+deltaTmin")
                #on ne va donc plus chercher à amener le fluide froid à la température de pincement mais on va partir de sa température d'entrée 
                TeF=ensFluxF[m].Te
                TsF=ensFluxC[p].Te-deltaTmin
                puissE=min(ensFluxC[p].chargeThE,(TsF-TeF)*ensFluxF[m].CP)
                if puissE==ensFluxC[p].chargeThE:#cela voudra dire qu'imposer une TsF à deltaTmin de l'entrée du fluide chaud implique que le fluide chaud ne peut pas fournir la chaleur demandé par le fluide froid. Ainsi, si le fluide chaud ne peut pas fournir plus, on recalcule quelle T va atteindre le fluide froid avec cette puissance
                    TsF=TeF+puissE/ensFluxF[m].CP
                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                    if bclDiv!="oui":
                        print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC))
                        Reseau.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3)))
                        ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                        ssFluxF=ssFlux.ssFlux(TeF,TsF,ensFluxF[m].CP*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                        ensFluxC[p].listeSsFlux.append(ssFluxC)
                        ensFluxF[m].listeSsFlux.append(ssFluxF)
                        listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
                    ensFluxC[p].chargeThE-=puissE
                    ensFluxF[m].chargeThE-=puissE
                    ensFluxF[m].pinc="oui"
                    ensFluxF[m].Te=TsF
                    ech+=1
                    #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                    if ensFluxC[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                        ensFluxC[p].Te=TsC
                    else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                        ensFluxC[p].ech="oui"
                        if bclDiv!="oui" and ensFluxC[p].div!=0.5:
                            CP[p]=CP[p]*2
                        if bclDiv!="oui" and ensFluxC[p].div==0.5:
                            ensFluxC[p].test=[]
                            ensFluxC[p].verif=0
                            ensFluxC[p].ech="non"
                            if ensFluxC[p].chargeThE!=0:    
                                CP[p]=ensFluxC[p].CP
                        if ensFluxC[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                            ensFluxC[p].div-=0.5
                            ensFluxC[p].Te=TsC
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            ensFluxC[p].div-=0.5
                return(ech,CP)
            if TeC<(TsF+deltaTmin):#hypothèse : "la chargeTh minimale est celle du fluide froid". On va réduire la température de sortie du flux froid. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                print("echE-stop1")
                TsF=min(ensFluxF[m].Ts,TeC-deltaTmin)
                #if TeF<ensFluxF[m].Te:
                TeF=ensFluxF[m].Te
                if ensFluxC[p].verif!=0:#car si toute les branches du flux n'ont pas fini d'être satisfaite alors on doit se baser sur son b
                    puissE=min(puissE,(TsF-TeF)*ensFluxF[m].CP)
                else:
                    puissE=min(ensFluxC[p].chargeThE,(TsF-TeF)*ensFluxF[m].CP)
                TsC=TeC-puissE/CPbrC
                if puissE==ensFluxC[p].chargeThE:#cela voudra dire qu'imposer une TsF à deltaTmin de l'entrée du fluide chaud implique que le fluide chaud ne peut pas fournir la chaleur demandé par le fluide froid. Ainsi, si le fluide chaud ne peut pas fournir plus, on recalcule quelle T va atteindre le fluide froid avec cette puissance
                    TeF=max(ensFluxF[m].Te,TsC-deltaTmin)
                    TsF=TeF+puissE/ensFluxF[m].CP
                
                #if ensFluxF[m].numero==10:
                print(puissE)
                print(TeC)
                print(TsC)
                print(TeF)
                print(TsF)
                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                    #print("stop")
                    if bclDiv!="oui":
                        print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC))
                        Reseau.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3)))
                        ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                        ssFluxF=ssFlux.ssFlux(TeF,TsF,ensFluxF[m].CP*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                        ensFluxC[p].listeSsFlux.append(ssFluxC)
                        ensFluxF[m].listeSsFlux.append(ssFluxF)
                        listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
                    ensFluxC[p].chargeThE-=puissE
                    ensFluxF[m].chargeThE-=puissE
                    ensFluxF[m].pinc="oui"
                    ensFluxF[m].Te=TsF
                    #print(ensFluxF[m].Te)
                    ech+=1
                    #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                    if ensFluxC[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                        ensFluxC[p].Te=TsC
                    else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                        ensFluxC[p].ech="oui"
                        if bclDiv!="oui" and ensFluxC[p].div!=0.5:
                            CP[p]=CP[p]*2
                        if bclDiv!="oui" and ensFluxC[p].div==0.5:
                            ensFluxC[p].test=[]
                            ensFluxC[p].verif=0
                            ensFluxC[p].ech="non"
                            if ensFluxC[p].chargeThE!=0:    
                                CP[p]=ensFluxC[p].CP
                        if ensFluxC[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                            ensFluxC[p].div-=0.5
                            ensFluxC[p].Te=TsC
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            ensFluxC[p].div-=0.5
            if TsC<(TeF+deltaTmin):# / hypothèse : la chargeTh minimale est celle du fluide froid / on va augmenter la température de sortie du fluide chaud. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                print("echE-stop2")
                TeF=ensFluxF[m].Te#car sinon TeF est égal à la valeur calculé dans la 1ère boucle
                if ensFluxC[p].verif==0:#car si verif!=0, alors on va modifier la Ts du flux chaud alors que celle-ci doit être fixe puisque la fin des branches d'un flux divisé doivent avoir la même température
                    TsC=max(ensFluxC[p].Ts,TeF+deltaTmin)
                puissE=(TeC-TsC)*CPbrC
                TsF=min(ensFluxF[m].Ts,TeF+puissE/ensFluxF[m].CP)
                print("TsC<TeF+deltaTmin")
                print(ensFluxC[p].numero)
                print(CPbrC)
                print(ensFluxF[m].CP)
                print(puissE)
                print(TeC)
                print(TsC)
                print(TeF)
                print(TsF)
                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                    if bclDiv!="oui":
                        print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC))
                        Reseau.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3)))
                        ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                        ssFluxF=ssFlux.ssFlux(TeF,TsF,ensFluxF[m].CP*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                        ensFluxC[p].listeSsFlux.append(ssFluxC)
                        ensFluxF[m].listeSsFlux.append(ssFluxF)
                        listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
                    print("échange")
                    ensFluxC[p].chargeThE-=puissE
                    ensFluxF[m].chargeThE-=puissE
                    ensFluxF[m].pinc="oui"
                    ensFluxF[m].Te=TsF
                    ech+=1
                    #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                    if ensFluxC[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                        ensFluxC[p].Te=TsC
                    else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                        ensFluxC[p].ech="oui"
                        if bclDiv!="oui" and ensFluxC[p].div!=0.5:
                            CP[p]=CP[p]*2
                        if bclDiv!="oui" and ensFluxC[p].div==0.5:
                            ensFluxC[p].test=[]
                            ensFluxC[p].verif=0
                            ensFluxC[p].ech="non"
                            if ensFluxC[p].chargeThE!=0:    
                                CP[p]=ensFluxC[p].CP
                        if ensFluxC[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                            ensFluxC[p].div-=0.5
                            ensFluxC[p].Te=TsC
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            ensFluxC[p].div-=0.5
    return(ech,CP)





def echE1(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,p,m,CPbrF,CPbrC,ech,bclDiv,CP,Reseau,ensFluxCinit,ensFluxFinit,listeCouple):#Pour flux chaud et froid divisé. Calcul la puissance de l'échange et vérifie la condition des deltaTmin
    TeC=min(TpincementC,ensFluxC[p].Te)#le but est que les fluides froids atteignent la température de pincementF. Et que le refroidissement des fluides chauds se fasse à la température la plus faible. 
    TsC=TeC-puissE/CPbrC
    if ensFluxF[m].echChargeTh=="non":
        TeF=ensFluxF[m].Te
        TsF=TeF+puissE/CPbrF
    else: 
        TsF=min(TpincementF,ensFluxF[m].Ts)
        TeF=TsF-puissE/CPbrF
    if ensFluxF[m].numero==11:
        print(puissE)
        print(CPbrC)
        print(CPbrF)
        print(TeC)
        print(TsC)
        print(TeF)
        print(TsF)
    if CPbrF<=CPbrC or ensFluxF[m].Ts<TpincementF:
        if TeC>=(TsF+deltaTmin) and TsC>=TeF+deltaTmin:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
            ensFluxC[p].chargeThE-=puissE
            ensFluxF[m].chargeThE-=puissE
            if bclDiv!="oui":
                print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC)+" - CPbrF : "+str(CPbrF))
                Reseau.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3))+" - CPbrF : "+str(round(CPbrF,3)))
                ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                ensFluxC[p].listeSsFlux.append(ssFluxC)
                ensFluxF[m].listeSsFlux.append(ssFluxF)
                listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
            ech+=1
            if ensFluxC[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                ensFluxC[p].Te=TsC
            else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                ensFluxC[p].ech="oui"
                if bclDiv!="oui" and ensFluxC[p].div!=0.5:
                    CP[p]=CP[p]*2
                if bclDiv!="oui" and ensFluxC[p].div==0.5:
                    ensFluxC[p].test=[]
                    ensFluxC[p].verif=0
                    ensFluxC[p].ech="non"
                    if ensFluxC[p].chargeThE!=0:
                        CP[p]=ensFluxC[p].CP
                if ensFluxC[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                    ensFluxC[p].Te=TsC
                    ensFluxC[p].verif=0
                if bclDiv!="oui":
                    ensFluxC[p].div-=0.5########vérifier que cela est correct car on met à 0 ensFluxC.div si son div =1 
            if ensFluxF[m].div==0:
                ensFluxF[m].Ts=TeF
            else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                ensFluxF[m].ech="oui"
                if ensFluxF[m].div==0.5:
                    ensFluxF[m].div-=0.5
                    ensFluxF[m].Ts=TeF
                    ensFluxF[m].pinc="oui"
                else:
                    ensFluxF[m].div-=0.5
        else:#prend en compte que l'échange peut-être inférieure à la charge Th d'un des flux (car sinon la condition deltaTmin n'est pas respectée)
            #print("else-echE1")
            if ensFluxF[m].Te<ensFluxC[p].Te:
                if TeC<=TeF+deltaTmin:
                    #print("PB : TeC<TeF+deltaTmin")
                    TeF=ensFluxF[m].Te
                    TsF=ensFluxC[p].Te-deltaTmin
                    puissE=(TsF-TeF)*ensFluxF[m].CP
                    if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                        if bclDiv!="oui":
                            print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC)+" - CPbrF : "+str(CPbrF))
                            Reseau.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3))+" - CPbrF : "+str(round(CPbrF,3)))
                            ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                            ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                            ensFluxC[p].listeSsFlux.append(ssFluxC)
                            ensFluxF[m].listeSsFlux.append(ssFluxF)
                            listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
                        ensFluxC[p].chargeThE-=puissE
                        ensFluxF[m].chargeThE-=puissE
                        ensFluxF[m].pinc="oui"
                        ech+=1
                        #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                        if ensFluxC[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                            ensFluxC[p].Te=TsC
                        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                            ensFluxC[p].ech="oui"
                            if bclDiv!="oui" and ensFluxC[p].div!=0.5:
                                CP[p]=CP[p]*2
                            if bclDiv!="oui" and ensFluxC[p].div==0.5:
                                ensFluxC[p].test=[]
                                ensFluxC[p].verif=0
                                ensFluxC[p].ech="non"
                                if ensFluxC[p].chargeThE!=0:
                                    CP[p]=ensFluxC[p].CP
                            if bclDiv!="oui":#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                ensFluxC[p].div-=0.5
                            if ensFluxC[p].div==0.5:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                ensFluxC[p].Te=TsC
                        if ensFluxF[m].div==0:
                            ensFluxF[m].Te=TsF
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            ensFluxF[m].ech="oui"
                            if ensFluxF[m].div==0.5:
                                ensFluxF[m].div-=0.5
                                ensFluxF[m].Te=TsF
                            else:
                                ensFluxF[m].div-=0.5
                    return(ech,CP)  
                if TeC<(TsF+deltaTmin):#hypothèse : "la chargeTh minimale est celle du fluide froid". On va réduire la température de sortie du flux froid. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                    if ensFluxF[m].echChargeTh=="non":
                        TsF=ensFluxF[m].tempMin
                    else:
                        TsF=min(ensFluxF[m].Ts,TeC-deltaTmin)
                    #if TeF<ensFluxF[m].Te:
                    TeF=ensFluxF[m].Te
                    puissE=min(ensFluxC[p].chargeThE,(TsF-TeF)*CPbrF)
                    TsC=TeC-puissE/CPbrC
                    print("(TsF-TeF)*CPbrF : "+str((TsF-TeF)*CPbrF))
                    if puissE==ensFluxC[p].chargeThE and puissE!=(TsF-TeF)*CPbrF:#cela voudra dire qu'imposer une TsF à deltaTmin de l'entrée du fluide chaud implique que le fluide chaud ne peut pas fournir la chaleur demandé par le fluide froid. Ainsi, si le fluide chaud ne peut pas fournir plus, on recalcule quelle T va atteindre le fluide froid avec cette puissance                      
                        if TeF>TsC-deltaTmin:
                            TeF=max(ensFluxF[m].Te,TsC-deltaTmin)
                        TsF=TeF+puissE/CPbrF
                    if ensFluxF[m].numero==11:
                        print("TeC<(TsF+deltaTmin)")
                        print(puissE)
                        print(TeC)
                        print(TsC)
                        print(TeF)
                        print(TsF)
                    if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                        if bclDiv!="oui":
                            print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC)+" - CPbrF : "+str(CPbrF))
                            Reseau.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3))+" - CPbrF : "+str(round(CPbrF,3)))
                            ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                            ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                            ensFluxC[p].listeSsFlux.append(ssFluxC)
                            ensFluxF[m].listeSsFlux.append(ssFluxF)
                            listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
                        ensFluxC[p].chargeThE-=puissE
                        ensFluxF[m].chargeThE-=puissE
                        ensFluxF[m].pinc="oui"
                        ech+=1
                        #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                        if ensFluxC[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                            ensFluxC[p].Te=TsC
                        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                            ensFluxC[p].ech="oui"
                            if bclDiv!="oui" and ensFluxC[p].div!=0.5:
                                CP[p]=CP[p]*2
                            if bclDiv!="oui" and ensFluxC[p].div==0.5:
                                ensFluxC[p].test=[]
                                ensFluxC[p].verif=0
                                ensFluxC[p].ech="non"
                                if ensFluxC[p].chargeThE!=0:
                                    CP[p]=ensFluxC[p].CP
                            if bclDiv!="oui":
                                ensFluxC[p].div-=0.5########vérifier que cela est correct car on met à 0 ensFluxC.div si son div =1 
                            if ensFluxC[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                #ensFluxC[p].div-=0.5
                                ensFluxC[p].Te=TsC
                            #else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                #ensFluxC[p].div-=0.5
                        if ensFluxF[m].div==0:
                            ensFluxF[m].Te=TsF
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            ensFluxF[m].ech="oui"
                            if ensFluxF[m].div==0.5:
                                ensFluxF[m].div-=0.5
                                ensFluxF[m].Te=TsF
                            else:
                                ensFluxF[m].div-=0.5
                if TsC<(TeF+deltaTmin):# / hypothèse : la chargeTh minimale est celle du fluide froid / on va augmenter la température de sortie du fluide chaud. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                    TeF=ensFluxF[m].Te#car sinon TeF est égal à la valeur calculé dans la 1ère boucle
                    if ensFluxC[p].verif==0:#car si verif!=0, alors on va modifier la Ts du flux chaud alors que celle-ci doit être fixe puisque la fin des branches d'un flux divisé doivent avoir la même température
                        TsC=max(ensFluxC[p].Ts,TeF+deltaTmin)
                    puissE=(TeC-TsC)*CPbrC
                    TsF=min(ensFluxF[m].Ts,TeF+puissE/CPbrF)
                    if ensFluxF[m].numero==11:
                        print("TsC<TeF+deltaTmin-echE1")
                        print(ensFluxC[p].numero)
                        print(CPbrC)
                        print(CPbrF)
                        print(puissE)
                        print(TeC)
                        print(TsC)
                        print(TeF)
                        print(TsF)
                    if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                        if bclDiv!="oui":
                            print("Couple c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC)+" - CPbrF : "+str(CPbrF))
                            Reseau.append("Couple c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3))+" - CPbrF : "+str(round(CPbrF,3)))
                            ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
                            ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
                            ensFluxC[p].listeSsFlux.append(ssFluxC)
                            ensFluxF[m].listeSsFlux.append(ssFluxF)
                            listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
                        #print("échange")
                        ensFluxC[p].chargeThE-=puissE
                        ensFluxF[m].chargeThE-=puissE
                        ensFluxF[m].pinc="oui"
                        ech+=1
                        #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                        if ensFluxC[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                            ensFluxC[p].Te=TsC
                        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                            ensFluxC[p].ech="oui"
                            if bclDiv!="oui" and ensFluxC[p].div!=0.5:
                                CP[p]=CP[p]*2
                            if bclDiv!="oui" and ensFluxC[p].div==0.5:
                                ensFluxC[p].test=[]
                                ensFluxC[p].verif=0
                                ensFluxC[p].ech="non"
                                if ensFluxC[p].chargeThE!=0:    
                                    CP[p]=ensFluxC[p].CP
                            if bclDiv!="oui":
                                ensFluxC[p].div-=0.5########vérifier que cela est correct car on met à 0 ensFluxC.div si son div =1 
                            if ensFluxC[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                #ensFluxC[p].div-=0.5
                                ensFluxC[p].Te=TsC
                            #else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                #ensFluxC[p].div-=0.5
                            if ensFluxF[m].div==0:
                                ensFluxF[m].Te=TsF
                            else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                ensFluxF[m].ech="oui"
                                if ensFluxF[m].div==0.5:
                                    ensFluxF[m].div-=0.5
                                    ensFluxF[m].Te=TsF
                                else:
                                    ensFluxF[m].div-=0.5


    return(ech,CP)

def echE2(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,p,m,CPbrF,CPbrC,ech,CP,Reseau,ensFluxCinit,ensFluxFinit,listeCouple):#égale à echE1 mais pas de condition sur les CP
    TeC=min(TpincementC,ensFluxC[p].Te)#le but est que les fluides froids atteignent la température de pincementF. Et que le refroidissement des fluides chauds se fasse à la température la plus faible. 
    TsF=min(TpincementF,ensFluxF[m].Ts)
    TsC=TeC-puissE/CPbrC
    TeF=TsF-puissE/CPbrF
    """print(puissE)
    print(TeC)
    print(TsC)
    print(TeF)
    print(TsF)"""
    if TeC>=(TsF+deltaTmin) and TsC>=TeF+deltaTmin:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
        ensFluxC[p].chargeThE-=puissE
        ensFluxF[m].chargeThE-=puissE
        print("Couple ech2 c"+str(ensFluxC[p].numero)+"/f"+str(ensFluxF[m].numero)+": "+str(round(puissE,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1))+" - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1))+" - CPbrC : "+str(CPbrC)+" - CPbrF : "+str(CPbrF))
        Reseau.append("Couple ech2 c"+str(ensFluxC[p].nom)+"/f"+str(ensFluxF[m].nom)+": "+str(round(puissE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3))+" - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3))+" - CPbrC : "+str(round(CPbrC,3))+" - CPbrF : "+str(round(CPbrF,3)))
        ssFluxC=ssFlux.ssFlux(TeC,TsC,CPbrC*1000,ensFluxC[p].debVol,ensFluxC[p].rho,ensFluxC[p].mu,ensFluxC[p].lamb,ensFluxC[p].press,ensFluxCinit[p],ensFluxC[p].type,Fct.testDiv(ensFluxC,p),False,puissE)
        ssFluxF=ssFlux.ssFlux(TeF,TsF,CPbrF*1000,ensFluxF[m].debVol,ensFluxF[m].rho,ensFluxF[m].mu,ensFluxF[m].lamb,ensFluxF[m].press,ensFluxFinit[m],ensFluxF[m].type,Fct.testDiv(ensFluxF,m),False,puissE)
        ensFluxC[p].listeSsFlux.append(ssFluxC)
        ensFluxF[m].listeSsFlux.append(ssFluxF)
        listeCouple.append(couple.couple(ssFluxF,ssFluxC,puissE,TeF,TsF,TeC,TsC))
        ech+=1
        if ensFluxC[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
            ensFluxC[p].Te=TsC
        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
            ensFluxC[p].ech="oui"
            CP[p]=CP[p]*2
            if ensFluxC[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                ensFluxC[p].div-=0.5
                ensFluxC[p].Te=TsC
            else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                ensFluxC[p].div-=0.5
        if ensFluxF[m].div==0:
            ensFluxF[m].Te=TsF
        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
            ensFluxF[m].ech="oui"
            if ensFluxF[m].div==0.5:
                ensFluxF[m].div-=0.5
                ensFluxF[m].Te=TsF
                ensFluxF[m].pinc="oui"
            else:
                ensFluxF[m].div-=0.5
    return(CP)



def newTeSimuDown(ensFluxC2,ensFluxF2,ensFluxC,ensFluxF,i,j,test,TpincementC,TpincementF,deltaTmin,compt):
    ensFluxC3=[]#permet de ne pas modifier les valeurs de ensFluxC2/F2
    ensFluxC3=copy.deepcopy(ensFluxC2)
    ensFluxF3=[]#permet de ne pas modifier les valeurs de ensFluxC2/F2
    ensFluxF3=copy.deepcopy(ensFluxF2)
    """print(len(ensFluxC3))
    print(len(ensFluxF3))
    print(test)"""
    print("entrée dans newTeSimuDown")
    for m in range(len(ensFluxF3)):
        #print("ensFluxF3[m].chargeThE :"+str(ensFluxF3[m].chargeThE))
        for p in range(len(ensFluxC3)):
            #print("ensFluxC3[p].chargeThE :"+str(ensFluxC3[p].chargeThE))
            if compt==0:
                return()
            """print("stop1")
            print(m)
            print(j)
            print(p)
            print(i)
            print("ensFluxF3[m].chargeThE : "+str(ensFluxF3[m].chargeThE))
            print("ensFluxC3[p].chargeThE : "+str(ensFluxC3[p].chargeThE))"""
            if m>j and p<i and ensFluxF3[m].chargeThE!=0 and ensFluxC3[p].chargeThE!=0 :#and ensFluxF3[m].numero in test ; il n'est pas nécessaire de simuler les échanges avec le flux i, on s'intéresse qu'au échange qui le précède
                #print("stop2")
                puissE1=min(ensFluxC3[p].chargeThE,ensFluxF3[m].chargeThE)
                if ensFluxF3[m].div==0:
                    CPbrF=ensFluxF3[m].CP
                else:
                    CPbrF=puissE1*ensFluxF3[m].CP/ensFluxF3[m].b
                if ensFluxC3[p].div==0:
                    CPbrC=ensFluxC3[p].CP
                else:#si il s'agit d'un flux placé avant déjà divisé, alors son b aura été calculé
                    if puissE1==ensFluxC3[p].b:#car sinon la valeur de CPbrC est légèrement différent du CP
                        CPbrC=ensFluxC3[p].CP
                    else:
                        CPbrC=puissE1*ensFluxC3[p].CP/ensFluxC3[p].b
                TeC=min(TpincementC,ensFluxC3[p].Te)#le but est que les fluides froids atteignent la température de pincementF. Et que le refroidissement des fluides chauds se fasse à la température la plus faible. 
                TsF=min(TpincementF,ensFluxF3[m].Ts)
                TsC=TeC-puissE1/CPbrC
                TeF=TsF-puissE1/CPbrF
                #print(ensFluxF[j].numero)
                #print(ensFluxC[i].numero)
                """if ensFluxF[j].numero==7 and (ensFluxF[m].numero==7 or ensFluxF[m].numero==8 or ensFluxF[m].numero==11):
                    print("/oui")
                    print(ensFluxF3[m].numero)
                    print(ensFluxC3[p].numero)
                    print(ensFluxC3[p].div)
                    print(ensFluxC3[p].CP)
                    print(ensFluxC3[p].b)
                    print(puissE1)
                    print("TeC : "+str(TeC))
                    print("TsC : "+str(TsC))
                    print("TeF : "+str(TeF))
                    print("TsF : "+str(TsF))
                    print(CPbrF)
                    print(CPbrC)"""
                if TeC>=(TsF+deltaTmin) and TsC>=TeF+deltaTmin  and (CPbrF<=round(CPbrC,3) or ensFluxF3[m].Ts<TpincementF):#on n'a pas besoin de simuler les échanges ayant lieu avec les fluides froids positionnés après le fluide froid en question car ils n'auront pas d'impact sur les échanges du fluide froid en question.:
                    print("1echange possible")
                    if (ensFluxC[p].verif!=0 or ensFluxC3[p].chargeThE1!=0) and p==i:
                        ensFluxC3[p].chargeThE1-=puissE1
                    ensFluxF3[m].chargeThE-=puissE1
                    if ensFluxC3[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                        ensFluxC3[p].Te=TsC
                    else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                        if ensFluxC3[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                            ensFluxC3[p].div-=0.5
                            ensFluxC3[p].Te=TsC
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            ensFluxC3[p].div-=0.5
                    if ensFluxF3[m].div==0:
                        ensFluxF3[m].Ts=TeF
                    else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                        if ensFluxF3[m].div==0.5:
                            ensFluxF3[m].div-=0.5
                            ensFluxF3[m].Ts=TeF
                            ensFluxF3[m].pinc="oui"
                        else:
                            ensFluxF3[m].div-=0.5
    
                else:#prend en compte que l'échange peut-être inférieure à la charge Th d'un des flux (car sinon la condition deltaTmin n'est pas respectée)
                    #print("else")
                    #print("verif flux chaud :" +str(ensFluxC3[p].verif))
                    if ensFluxF3[m].Te<ensFluxC3[p].Te:#and ensFluxC3[p].verif==0 #on vérifie que verif est nul car sinon cela signifie que les températures du flux chauds ont déjà été modifiés pour s'adapter un flux. Si on les modifie à nouveau, les températures ne seront plus adaptées pour le premier flux.
                        #print("stop")
                        """print(ensFluxF2[m].numero)
                        print(ensFluxC2[p].numero)
                        print(ensFluxC2[p].chargeThE1)"""
                        if TeC<=TeF+deltaTmin:
                            TeC=TeC#inutile (permet juste de ne pas afficher print("PB ..."))
                            #print("PB : TeC<TeF+deltaTmin")
                            #on ne va donc plus chercher à amener le fluide froid à la température de pincement mais on va partir de sa température d'entrée 
                            """TeF=ensFluxF[m].Te
                            TsF=ensFluxC[p].Te-deltaTmin
                            puissE=(TsF-TeF)*ensFluxF[m].CP
                            if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                                #print("échange0")
                                ensFluxC2[p].chargeThE1-=puissE
                                ensFluxF2[m].chargeThE-=puissE
                                ensFluxC2[p].puissE3=puissE
                                if p==i:#si le flux respecte les règles on le retire de la liste sup
                                    sup.remove(ensFluxF2[m].numero)
                                    compt-=0.5
                                    #print(ensFluxC2[p].chargeThE1)
                                if ensFluxC2[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                                    ensFluxC2[p].Te=TsC
                                else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                                    if ensFluxC2[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                        ensFluxC2[p].div-=0.5
                                        ensFluxC2[p].Te=TsC
                                    else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                        ensFluxC2[p].div-=0.5
                                #ensFluxF2[m].Ts=TeF  on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                                if ensFluxF2[m].div!=0:
                                    if ensFluxF2[m].div==0.5:
                                        ensFluxF2[m].div-=0.5
                                        #ensFluxF2[m].Ts=TeF
                                        ensFluxF2[m].pinc="oui"
                                    else:
                                        ensFluxF2[m].div-=0.5"""


                        else:
                            #print("EEELLLLLSSEE")
                            """print("b1 : "+str(ensFluxC2[p].b))
                            print("ensFluxC2[i].b : "+str(ensFluxC2[i].b))
                            print("puissMaxEch : "+str(maxPuissEch))
                            print("maxListeTeF : "+str(maxListeTeF))
                            print("ensFluxC[i].Te : "+str(ensFluxC[i].Te))
                            print("ensFluxC[i].CP : "+str(ensFluxC[i].CP))"""
                            if TsC<(TeF+deltaTmin):# / hypothèse : la chargeTh minimale est celle du fluide chaud / on va augmenter la température de sortie du fluide chaud. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                                TeF=ensFluxF3[m].Te#car sinon TeF est égal à la valeur calculé dans la 1ère boucle
                                TsC=max(ensFluxC3[p].Ts,TeF+deltaTmin)
                                puissE=(TeC-TsC)*CPbrC
                                TsF=min(ensFluxF3[m].Ts,TeF+puissE/ensFluxF3[m].CP)
                                if ensFluxF[j].numero==3 and ensFluxC3[p].numero==4:
                                    """print(puissE)
                                    print(TeC)
                                    print(TsC)
                                    print(TeF)
                                    print(TsF)
                                    print(CPbrC)"""
                                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF and (CPbrF<=round(CPbrC,3) or ensFluxF3[m].Ts<TpincementF):#on n'a pas besoin de simuler les échanges ayant lieu avec les fluides froids positionnés après le fluide froid en question car ils n'auront pas d'impact sur les échanges du fluide froid en question.:
                                    print("échange1")
                                    ensFluxC3[p].chargeThE-=puissE
                                    ensFluxF3[m].chargeThE-=puissE
                                    ensFluxF2[m].chargeThE-=puissE
                                    ensFluxC3[p].puissE3=puissE
                                    if ensFluxC3[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                                        ensFluxC3[p].Te=TsC
                                    else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                                        if ensFluxC3[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                            ensFluxC3[p].div-=0.5
                                            ensFluxC3[p].Te=TsC
                                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                            ensFluxC3[p].div-=0.5
                                    #ensFluxF2[m].Ts=TeF  on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                                    if ensFluxF3[m].div!=0:
                                        if ensFluxF3[m].div==0.5:
                                            ensFluxF3[m].div-=0.5
                                            ensFluxF3[m].Te=TsF
                                            ensFluxF[m].newTe=TsF
                                            ensFluxF[m].newTeNum=ensFluxC3[p].numero
                                            ensFluxF3[m].pinc="oui"
                                        else:
                                            ensFluxF3[m].div-=0.5 
                                    else:
                                        ensFluxF3[m].Te=TsF
                                        ensFluxF[m].newTe=TsF
                                        ensFluxF[m].newTeNum=ensFluxC3[p].numero
                            if TeC<(TsF+deltaTmin): #hypothèse : "la chargeTh minimale est celle du fluide froid". On va réduire la température de sortie du flux froid. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                                TsF=min(ensFluxF3[m].Ts,TeC-deltaTmin)
                                #if TeF<ensFluxF3[m].Te:
                                TeF=ensFluxF3[m].Te
                                puissE=min(ensFluxC3[p].chargeThE,(TsF-TeF)*CPbrF)
                                TsC=TeC-puissE/CPbrC
                                #print("(TsF-TeF)*CPbrF : "+str((TsF-TeF)*CPbrF))
                                if puissE==ensFluxC3[p].chargeThE and puissE!=(TsF-TeF)*CPbrF:#cela voudra dire qu'imposer une TsF à deltaTmin de l'entrée du fluide chaud implique que le fluide chaud ne peut pas fournir la chaleur demandé par le fluide froid. Ainsi, si le fluide chaud ne peut pas fournir plus, on recalcule quelle T va atteindre le fluide froid avec cette puissance                      
                                    if TeF>TsC-deltaTmin:
                                        TeF=max(ensFluxF3[m].Te,TsC-deltaTmin)
                                    TsF=TeF+puissE/CPbrF
                                """print("//")
                                print(ensFluxC3[p].numero)
                                print(ensFluxF3[m].numero)
                                print(ensFluxC3[p].b)
                                print(CPbrC)
                                print(puissE)
                                print(TeC)
                                print(TsC)
                                print(TeF)
                                print(TsF)"""
                                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF and (CPbrF<=round(CPbrC,3) or ensFluxF3[m].Ts<TpincementF):#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                                    print("échange2")
                                    ensFluxC3[p].chargeThE-=puissE
                                    ensFluxF3[m].chargeThE-=puissE
                                    ensFluxF2[m].chargeThE-=puissE
                                    ensFluxC3[p].puissE3=puissE
                                    if ensFluxC3[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                                        ensFluxC3[p].Te=TsC
                                    else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                                        if ensFluxC3[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                            ensFluxC3[p].div-=0.5
                                            ensFluxC3[p].Te=TsC
                                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                            ensFluxC3[p].div-=0.5
                                    #ensFluxF2[m].Ts=TeF  on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                                    if ensFluxF3[m].div!=0:
                                        if ensFluxF3[m].div==0.5:
                                            ensFluxF3[m].div-=0.5
                                            ensFluxF3[m].Te=TsF
                                            ensFluxF[m].newTe=TsF
                                            ensFluxF[m].newTeNum=ensFluxC3[p].numero
                                            #print("ensFluxF[m].newTe=TsF"+str(ensFluxF[m].newTe))
                                            ensFluxF3[m].pinc="oui"
                                        else:
                                            ensFluxF3[m].div-=0.5
                                    else:
                                        ensFluxF3[m].Te=TsF
                                        ensFluxF[m].newTe=TsF
                                        #print("ensFluxF[m].newTe=TsF" + str(ensFluxF[m].newTe))
                                        ensFluxF[m].newTeNum=ensFluxC3[p].numero
    return()


def newTeSimuUp(ensFluxC2,ensFluxF2,ensFluxC,ensFluxF,i,j,test,TpincementC,TpincementF,deltaTmin,compt):
    ensFluxC3=[]#permet de ne pas modifier les valeurs de ensFluxC2/F2
    ensFluxC3=copy.deepcopy(ensFluxC2)
    ensFluxF3=[]#permet de ne pas modifier les valeurs de ensFluxC2/F2
    ensFluxF3=copy.deepcopy(ensFluxF2)
    """print(len(ensFluxC3))
    print(len(ensFluxF3))
    print(test)"""
    for p in range(len(ensFluxC3)):
        #print("ensFluxF3[m].chargeThE :"+str(ensFluxF3[m].chargeThE))
        for m in range(len(ensFluxF3)):
            #print("ensFluxC3[p].chargeThE :"+str(ensFluxC3[p].chargeThE))
            if compt==0:
                return()
            """print("stop1")
            print(m)
            print(j)
            print(p)
            print(i)"""
            if p>i and m<j and ensFluxF3[m].chargeThE!=0 and ensFluxC3[p].chargeThE!=0 :#and ensFluxF3[m].numero in test ; il n'est pas nécessaire de simuler les échanges avec le flux i, on s'intéresse qu'au échange qui le précède
                #print("stop2")
                puissE1=min(ensFluxC3[p].chargeThE,ensFluxF3[m].chargeThE)
                if ensFluxC3[p].div==0:
                    CPbrC=ensFluxC3[p].CP
                else:
                    CPbrC=puissE1*ensFluxC3[p].CP/ensFluxC3[p].b
                if ensFluxF3[m].div==0:
                    CPbrF=ensFluxF3[m].CP
                else:#si il s'agit d'un flux placé avant déjà divisé, alors son b aura été calculé
                    if puissE1==ensFluxF3[m].b:#car sinon la valeur de CPbrC est légèrement différent du CP
                        CPbrF=ensFluxF3[p].CP
                    else:
                        CPbrF=puissE1*ensFluxF3[m].CP/ensFluxF3[m].b
                TeF=max(TpincementF,ensFluxF[m].Te)
                TsF=TeF+puissE/CPbrF   
                TsC=max(TpincementC,ensFluxC[p].Ts)#le but est que les fluides froids atteignent la température de pincementF. Et que le refroidissement des fluides chauds se fasse à la température la plus faible. 
                TeC=TsC+puissE/CPbrC 
                print("/oui")
                print(ensFluxF3[m].numero)
                print(ensFluxC3[p].numero)
                print(ensFluxC3[p].div)
                print(ensFluxC3[p].CP)
                print(ensFluxC3[p].b)
                print(puissE1)
                print("TeC : "+str(TeC))
                print("TsC : "+str(TsC))
                print("TeF : "+str(TeF))
                print("TsF : "+str(TsF))
                print(CPbrF)
                print(CPbrC)
                if TeC>=(TsF+deltaTmin) and TsC>=TeF+deltaTmin  and (CPbrC<=round(CPbrF,3) or ensFluxC3[p].Ts>TpincementC):#on n'a pas besoin de simuler les échanges ayant lieu avec les fluides froids positionnés après le fluide froid en question car ils n'auront pas d'impact sur les échanges du fluide froid en question.:
                    print("1echange possible")
                    if (ensFluxF[m].verif!=0 or ensFluxF3[m].chargeThA1!=0) and m==j:
                        ensFluxF3[m].chargeThA1-=puissE1
                    ensFluxC3[p].chargeThA-=puissE1
                    if ensFluxF3[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                        ensFluxF3[m].Te=TsF
                    else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                        if ensFluxF3[m].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                            ensFluxF3[m].div-=0.5
                            ensFluxF3[m].Te=TsF
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            ensFluxF3[m].div-=0.5
                    if ensFluxC3[p].div==0:
                        ensFluxC3[p].Ts=TeC
                    else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                        if ensFluxC3[p].div==0.5:
                            ensFluxC3[p].div-=0.5
                            ensFluxC3[p].Ts=TeC
                            ensFluxC3[p].pinc="oui"
                        else:
                            ensFluxC3[p].div-=0.5
    
                else:#prend en compte que l'échange peut-être inférieure à la charge Th d'un des flux (car sinon la condition deltaTmin n'est pas respectée)
                    #print("else")
                    #print("verif flux chaud :" +str(ensFluxC3[p].verif))
                    if ensFluxF3[m].Te<ensFluxC3[p].Te:#and ensFluxC3[p].verif==0 #on vérifie que verif est nul car sinon cela signifie que les températures du flux chauds ont déjà été modifiés pour s'adapter un flux. Si on les modifie à nouveau, les températures ne seront plus adaptées pour le premier flux.
                        #print("stop")
                        """print(ensFluxF2[m].numero)
                        print(ensFluxC2[p].numero)
                        print(ensFluxC2[p].chargeThE1)"""
                        if TeC<=TeF+deltaTmin:
                            TeC=TeC#inutile (permet juste de ne pas afficher print("PB ..."))
                            #print("PB : TeC<TeF+deltaTmin")
                            #on ne va donc plus chercher à amener le fluide froid à la température de pincement mais on va partir de sa température d'entrée 
                            """TeF=ensFluxF[m].Te
                            TsF=ensFluxC[p].Te-deltaTmin
                            puissE=(TsF-TeF)*ensFluxF[m].CP
                            if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                                #print("échange0")
                                ensFluxC2[p].chargeThE1-=puissE
                                ensFluxF2[m].chargeThE-=puissE
                                ensFluxC2[p].puissE3=puissE
                                if p==i:#si le flux respecte les règles on le retire de la liste sup
                                    sup.remove(ensFluxF2[m].numero)
                                    compt-=0.5
                                    #print(ensFluxC2[p].chargeThE1)
                                if ensFluxC2[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                                    ensFluxC2[p].Te=TsC
                                else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                                    if ensFluxC2[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                        ensFluxC2[p].div-=0.5
                                        ensFluxC2[p].Te=TsC
                                    else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                        ensFluxC2[p].div-=0.5
                                #ensFluxF2[m].Ts=TeF  on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                                if ensFluxF2[m].div!=0:
                                    if ensFluxF2[m].div==0.5:
                                        ensFluxF2[m].div-=0.5
                                        #ensFluxF2[m].Ts=TeF
                                        ensFluxF2[m].pinc="oui"
                                    else:
                                        ensFluxF2[m].div-=0.5"""


                        else:
                            #print("EEELLLLLSSEE")
                            """print("b1 : "+str(ensFluxC2[p].b))
                            print("ensFluxC2[i].b : "+str(ensFluxC2[i].b))
                            print("puissMaxEch : "+str(maxPuissEch))
                            print("maxListeTeF : "+str(maxListeTeF))
                            print("ensFluxC[i].Te : "+str(ensFluxC[i].Te))
                            print("ensFluxC[i].CP : "+str(ensFluxC[i].CP))"""
                            if TsC<(TeF+deltaTmin):# / hypothèse : la chargeTh minimale est celle du fluide chaud / on va augmenter la température de sortie du fluide chaud. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                                TsC=TeF+deltaTmin
                                #if TeC<ensFluxC3[p].Te:
                                TeC=ensFluxC3[p].Te
                                puissE=min(ensFluxF3[m].chargeThA,(TeC-TsC)*CPbrC)
                                TsF=TeF+puissE/CPbrF
                                if puissE==ensFluxF3[m].chargeThA and puissE!=(TeC-TsC)*CPbrC:#cela voudra dire qu'imposer une TsF à deltaTmin de l'entrée du fluide chaud implique que le fluide chaud ne peut pas fournir la chaleur demandé par le fluide froid. Ainsi, si le fluide chaud ne peut pas fournir plus, on recalcule quelle T va atteindre le fluide froid avec cette puissance
                                    if TeC<TsF+deltaTmin:
                                        TeC=min(ensFluxC3[p].Te,TsF+deltaTmin)
                                    TsC=TeC-puissE/ensFluxC3[p].CP
                                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF and (CPbrC<=round(CPbrF,3) or ensFluxC3[p].Ts>TpincementC):#on n'a pas besoin de simuler les échanges ayant lieu avec les fluides froids positionnés après le fluide froid en question car ils n'auront pas d'impact sur les échanges du fluide froid en question.:
                                    print("échange1")
                                    ensFluxC3[p].chargeThE-=puissE
                                    ensFluxF3[m].chargeThE-=puissE
                                    ensFluxF3[m].puissE3=puissE
                                    if ensFluxF3[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                                        ensFluxF3[m].Te=TsF
                                    else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                                        if ensFluxF3[m].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                            ensFluxF3[m].div-=0.5
                                            ensFluxF3[m].Te=TsF
                                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                            ensFluxF3[m].div-=0.5
                                    #ensFluxF2[m].Ts=TeF  on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                                    if ensFluxC3[p].div!=0:
                                        if ensFluxC3[p].div==0.5:
                                            ensFluxC3[p].div-=0.5
                                            ensFluxC3[p].Te=TsC
                                            ensFluxC[p].newTe=TsC
                                            ensFluxC[p].newTeNum=ensFluxF3[m].numero
                                            ensFluxC3[p].pinc="oui"
                                        else:
                                            ensFluxC3[p].div-=0.5 
                                    else:
                                        ensFluxC3[p].Te=TsC
                                        ensFluxC[p].newTe=TsC
                                        ensFluxC[p].newTeNum=ensFluxF3[m].numero
                            if TeC<(TsF+deltaTmin): #hypothèse : "la chargeTh minimale est celle du fluide froid". On va réduire la température de sortie du flux froid. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)                               
                                TeC=ensFluxC3[p].Te#car sinon TeF est égal à la valeur calculé dans la 1ère boucle
                                if ensFluxF3[m].verif==0:#car si verif!=0, alors on va modifier la Ts du flux chaud alors que celle-ci doit être fixe puisque la fin des branches d'un flux divisé doivent avoir la même température
                                    TsF=min(ensFluxF3[m].Ts,TeC-deltaTmin)
                                puissE=(TsF-TeF)*CPbrF
                                TsC=max(ensFluxC3[p].Ts,TeC-puissE/ensFluxC3[p].CP)

                                print("//")
                                print(ensFluxC3[p].numero)
                                print(ensFluxF3[m].numero)
                                print(ensFluxC3[p].b)
                                print(CPbrC)
                                print(puissE)
                                print(TeC)
                                print(TsC)
                                print(TeF)
                                print(TsF)
                                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF and (CPbrC<=round(CPbrF,3) or ensFluxC3[p].Ts>TpincementC):#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                                    print("échange2")
                                    ensFluxC3[p].chargeThE-=puissE
                                    ensFluxF3[m].chargeThE-=puissE
                                    ensFluxF3[m].puissE3=puissE
                                    if ensFluxF3[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                                        ensFluxF3[m].Te=TsF
                                    else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                                        if ensFluxF3[m].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                            ensFluxF3[m].div-=0.5
                                            ensFluxF3[m].Te=TsF
                                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                            ensFluxF3[m].div-=0.5
                                    #ensFluxF2[m].Ts=TeF  on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                                    if ensFluxC3[p].div!=0:
                                        if ensFluxC3[p].div==0.5:
                                            ensFluxC3[p].div-=0.5
                                            ensFluxC3[p].Te=TsC
                                            ensFluxC[p].newTe=TsC
                                            ensFluxC[p].newTeNum=ensFluxF3[m].numero
                                            ensFluxC3[p].pinc="oui"
                                        else:
                                            ensFluxC3[p].div-=0.5 
                                    else:
                                        ensFluxC3[p].Te=TsC
                                        ensFluxC[p].newTe=TsC
                                        ensFluxC[p].newTeNum=ensFluxF3[m].numero
    return()







def Reseau1(ensFluxF,ensFluxC,CP,TpincementF,TpincementC,deltaTmin,longF,longC):
    print("") 
    print("Réseau 1") 
    Reseau=[]
    puissE=0#puissance de l'échange de chaleurlisteCouple=[]#ensemble des couples du réseau
    ensFluxCinit=[]
    ensFluxFinit=[]
    listeCouple=[]
    for j in range(len(ensFluxF)):#détermination des couples et de leurs puissances
        print("----------------")
        div=[]
        for i in range(len(ensFluxC)):
            div.append(ensFluxC[i].div)
        print(div)
        print(CP)
        ech=0#indique si le fluide a échangé de la chaleur
        imp=0#indique si le fluide ne peut pas échanger avec les flux chauds car sa Te est supérieur à toute les Te des flux chauds
        for i in range(len(ensFluxC)):
            #print(ensFluxC[i].div)
            annul="non"
            #print("num flux c"+str(ensFluxC[i].numero)+"-f"+str(ensFluxF[j].numero)+"/div: "+str(ensFluxC[i].div)+"/chargeThE: "+str(ensFluxC[i].chargeThE))
            if ensFluxF[j].CP<=ensFluxC[i].CP or ensFluxF[j].Ts<TpincementF and ensFluxF[j].pinc!="oui":#Calcul puissance échangée
                if ensFluxF[j].chargeThE!=0 and ensFluxC[i].chargeThE!=0:#on vérifie que les deux fluides ne sont pas déjà satisfait énergétiquement
                    puissE=min(ensFluxC[i].chargeThE,ensFluxF[j].chargeThE)
                    if ensFluxC[i].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                        #print("div=0")
                        CPbrC=ensFluxC[i].CP
                    else:#nous devons d'abord déterminer avec quel flux le flud divisé froid va échanger pour connaitre quel sera le dénominateur de CPbrF
                        if ensFluxC[i].ech=="non":
                            #print("div avant :" +str(ensFluxC[i].div))
                            print("entrée divE")
                            ensFluxC[i].b,annul,annuldiv,m,test,CP1=Division.divE(ensFluxC,ensFluxF,i,j,TpincementC,TpincementF,deltaTmin,ech,CP,"",Reseau,ensFluxCinit,ensFluxFinit,listeCouple)#on connait maitenant le dénominateur de CPbrF
                            print("sortie divE")
                            CP=CP1
                            print(ensFluxC[i].b)
                            print(CP)
                            #print("div après :" +str(ensFluxC[i].div))
                            if ensFluxC[i].puissModif=="oui":#lorsque la puissance échangée a été modifié dans la fct divE car on a échangé moins que la charge thermique minimale des deux flux
                                puissE=ensFluxC[i].b
                            if annul=="non":
                                if ensFluxC[i].div>0:#car sinon cela veut dire qu'on a annulé toutes ses branches
                                    CP[i]=0#permet de ne pas diviser un flux tant que toutes ses branches n'ont pas fini d'avoir échangé (sinon problème au niveau des .div)
                            #print(ensFluxC[i].numero)
                            if annuldiv=="oui":
                                #print(CP)
                                CPdiv=CP[i]
                                CP[i]=0#on ne va pas diviser le flux actuel alors qu'on cherche à annuler sa division
                                CPcompt=0
                                div=[]
                                CPdiv1=[]
                                CPdiv1=copy.deepcopy(CP)
                                for h in range(len(ensFluxC)):#on sauvegarde la valeur des div avant division
                                    div.append(ensFluxC[h].div)
                                while ensFluxC[i].div!=0:
                                    verif=0
                                    for h in range(len(CP)):
                                        verif+=CP[h]
                                    if verif==0:#si verif=0 alors tous les flux sont déjà satisfaits
                                        print("1Tous les flux sont satisfaits. Division d'un flux chaud impossible")
                                        #print(CP)
                                        for h in range(len(ensFluxC)):
                                            ensFluxC[h].div=div[h]
                                        CP=CPdiv1
                                        #print(CP)
                                        break#permet de stopper la boucle while annul!="non"
                                    #print(verif)
                                    if ensFluxC[i].div==1:
                                        ensFluxC[i].div=0
                                    else:
                                        ensFluxC[i].div-=0.5
                                    CPcompt+=1
                                    print("On annule la division du flux c"+str(ensFluxC[i].numero))#car une des branches des flux échanges toutes sa chaleur
                                    longC-=1
                                    #division d'un nouveau flux pour toujours respecter la règle des flux
                                    ind=CP.index(max(CP))
                                    print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
                                    CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                                    if ensFluxC[ind].div==0:
                                        ensFluxC[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                                    else:
                                        ensFluxC[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                                    longC+=1
                                CP[i]=CPdiv*2*CPcompt#on lui réattribue sa valeur moins les branches retirées (annulées)
                                #print(CP)
                                CPbrC=ensFluxC[i].CP
                            else:
                                print("stop")
                                print(puissE)
                                print(ensFluxC[i].CP)
                                print(ensFluxC[i].b)
                                CPbrC=puissE*ensFluxC[i].CP/ensFluxC[i].b
                                print(CPbrC)
                        else:
                            CPbrC=puissE*ensFluxC[i].CP/ensFluxC[i].b
                        if ensFluxC[i].verif!=0:
                            #print("verif")
                            #print(verif)
                            puiss=min((ensFluxC[i].b-ensFluxC[i].b1),ensFluxF[j].chargeThE)
                            ensFluxC[i].b1+=puiss
                            CPbrC=puiss*ensFluxC[i].CP/ensFluxC[i].b
                        if ensFluxF[j].numero==5: 
                            """print(CPbrC)
                            print(puiss)
                            print(ensFluxC[i].CP)
                            print(ensFluxC[i].numero)
                            print(ensFluxF[j].numero)
                            print(ensFluxC[i].div)
                            print(ensFluxC[i].test)"""

                    """print("boucle1-affich:")
                    print(ensFluxF[j].numero)
                    print(ensFluxC[i].numero)
                    print(ensFluxC[i].div)
                    print(annul)
                    print(ensFluxC[i].test)"""
                    if annul!="oui" and ((ensFluxC[i].div!=0 and ensFluxF[j].numero in ensFluxC[i].test) or ensFluxC[i].div==0):
                        print("entrée pour échange")
                        #print(CP)
                        bclDiv="non"
                        print(CP)
                        print(CPbrC)
                        ech,CP=Fct.echE(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,i,j,CPbrC,ech,CP,bclDiv,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)
                        print(CP)
                        #print("div flux chaud" +str(ensFluxC[i].div))
                    if ensFluxC[i].chargeThE==0 and len(CP)!=0:#car si aucun flux chaud n'a été divisé, CP[i] n'existera pas
                        CP[i]=0#cela permet de ne pas diviser à nouveau un flux chaud
            if ensFluxF[j].Te>ensFluxC[i].Te or ensFluxC[i].chargeThE==0:
                imp+=1
        if (ech==0 or ensFluxF[j].chargeThE!=0) and imp<len(ensFluxC)-1 and ensFluxF[j].Ts>TpincementF:#Si le fluide n'a pas pu échanger avec aucun flux mais que sa Te lui permet d'échanger de la chaleur, alors son CP est trop grand : on va le diviser. On vérifie aussi qu'il atteint la T de pincement car sinon il n'a pas besoin de respecter la règle du CP
            CPbrF=0#CP de chaque branche du flux froid divisé
            CPbrC=0#CP de chaque branche du flux chaud divisé
            annul="oui"
            div=[]
            CPdiv1=[]
            CPdiv1=copy.deepcopy(CP)
            ensFluxF[j].b2=0
            chargeThEfr=copy.deepcopy(ensFluxF[j].chargeThE)
            for h in range(len(ensFluxC)):#on sauvegarde la valeur des div avant division
                div.append(ensFluxC[h].div)
            while annul!="non":
                ensFluxF[j].b2+=1
                verif=0
                for h in range(len(CP)):
                    verif+=CP[h]
                if verif<0.01:#Car sinon on aura une boucle infini car les flux chauds seront divisés jusqu'à ce que la boucle while soit satisfaite
                    print("2Tous les flux sont satisfaits. Division d'un flux chaud impossible")
                    for h in range(len(ensFluxC)):#comme l'échange n'est pas possible malgré les division, on annule les divisions en rétablissant les div
                        ensFluxC[h].div=div[h]
                    CP=CPdiv1
                    verif=0#car on teste la valeur de verif par la suite par rapport à 0. On considère dans ce cas que verif=0
                    break#permet de stopper la boucle while annul!="non"
                if ensFluxF[j].numero!=10 and ensFluxF[j].numero!=11 and ensFluxF[j].numero!=7 and ensFluxF[j].numero!=8 and ensFluxF[j].numero!=9 and ensFluxF[j].numero!=3:
                    print("Le fluide froid f"+str(ensFluxF[j].numero)+" doit être divisé en deux.")
                if ensFluxF[j].div==0:
                    ensFluxF[j].div+=1
                else:
                    ensFluxF[j].div+=0.5
                longF+=1
                while longF>longC:#on vérifie à nouveau la condition sur le nombre de flux et indique à l'utilisateur que le flux doit être divisé en deux. On divise le fluide chaud qui a le plus grand CP pour que la condition sur les CP soit conservé. Jsuqu'à ce que le nombre de flux froids soit inférieur au nombre de flux chauds.
                    ind=CP.index(max(CP))
                    if ensFluxF[j].numero!=10 and ensFluxF[j].numero!=11 and ensFluxF[j].numero!=7 and ensFluxF[j].numero!=8 and ensFluxF[j].numero!=9 and ensFluxF[j].numero!=3:
                        print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
                    CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                    if ensFluxC[ind].div==0:
                        ensFluxC[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                    else:
                        ensFluxC[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                    longC+=1
                condCharge=0
                for i in range (len(ensFluxC)):
                    if ensFluxC[i].chargeThE==0:
                        condCharge+=1
                #if condCharge==len(ensFluxC):
                """print(len(ensFluxC))
                print(condCharge)"""
                if ensFluxF[j].numero==5:
                    print("************")
                    #print(div)
                    #print(CP)
                ensFluxF[j].b,annul=Division.divE1(ensFluxC,ensFluxF,j,TpincementC,TpincementF,deltaTmin,CP,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)#le but est de simuler les prochains échanges avec le flux froid divisé pour connaître la valeur de son b. 
            ensFluxF[j].chargeThE=chargeThEfr
            div=[]
            for h in range(len(ensFluxC)):#on sauvegarde la valeur des div avant division
                div.append(ensFluxC[h].div)
            print(ensFluxF[j].b)
            
            if verif!=0:
                print("Echange possible avec flux froid divisé : f"+str(ensFluxF[j].numero))
                print("")
                #CP=CPdiv1
                #print(CP)
                #print(div)
                for k in range(len(ensFluxC)):
                    annul1="non"
                    ensFluxC[k].verif=0
                    #print(ensFluxC[k].chargeThE)
                    #print(ensFluxF[j].chargeThE)
                    if ensFluxC[k].chargeThE!=0 and ensFluxF[j].chargeThE!=0 and ensFluxF[j].pinc!="oui":#si les fluides ne sont pas satisfait et le fluide froid possède encore des branches non utilisées (on considère un échange par branche)
                        puissE=min(ensFluxC[k].chargeThE,ensFluxF[j].chargeThE)
                        if ensFluxC[k].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                            CPbrC=ensFluxC[k].CP
                        else:#sinon on pondère le CP avec la puissance du flux complémentaire
                            if ensFluxC[k].ech=="non":
                                if ensFluxF[j].numero==5:
                                    print("1-entréedivE")
                                    #print(ensFluxF[j].b)
                                #vérifier que retourner m et test est vraiment utile !?
                                ensFluxC[k].b,annul1,annuldiv,m,test,CP=Division.divE(ensFluxC,ensFluxF,k,j,TpincementC,TpincementF,deltaTmin,ech,CP,"echE1",Reseau,ensFluxCinit,ensFluxFinit,listeCouple)#le but est de simuler les prochains échanges avec le flux chaud divisé pour connaître la valeur de son b
                                if ensFluxF[j].numero==5:
                                    print("1-sortie divE")
                                CPdiv=CP[k]#on ne va pas diviser le flux actuel alors qu'on cherche à annuler sa division
                                CPdiv1=[]
                                CPdiv1=copy.deepcopy(CP)
                                if annul=="non":
                                    if ensFluxC[k].div>0:
                                        CP[k]=0#permet de ne pas diviser un flux dont toutes ses branches n'ont pas fini d'avoir échangé (sinon problème au niveau des .div)
                                if annuldiv=="oui":
                                    CP[k]=0
                                    CPcompt=0
                                    div=[]
                                    for h in range(len(ensFluxC)):#on sauvegarde la valeur des div avant division
                                        div.append(ensFluxC[h].div)
                                    while ensFluxC[k].div!=0:
                                        for h in range(len(CP)):
                                            verif+=CP[h]
                                        if verif==0:#si verif=0 alors tous les flux sont déjà satisfaits
                                            print("3Tous les flux sont satisfaits. Division d'un flux chaud impossible")
                                            for h in range(len(ensFluxC)):
                                                ensFluxC[h].div=div[h]
                                            CP=CPdiv1
                                            break#permet de stopper la boucle while annul!="non"
                                        CPcompt+=1
                                        if ensFluxC[k].div==1:
                                            ensFluxC[k].div=0
                                        else:
                                            ensFluxC[k].div-=0.5
                                        print("On annule la division du flux c"+str(ensFluxC[k].numero))#car une des branches des flux échange toute sa chaleur
                                        #print(ensFluxC[k].div)
                                        #division d'un nouveau flux pour toujours respecter la règle des flux
                                        ind=CP.index(max(CP))
                                        print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
                                        CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                                        if ensFluxC[ind].div==0:
                                            ensFluxC[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                                        else:
                                            ensFluxC[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                                    CP[k]=CPdiv*2*CPcompt#on lui réattribue sa valeur moins les branches retirées (annulées)
                                    CPbrC=ensFluxC[k].CP
                                else:
                                    CPbrC=puissE*ensFluxC[k].CP/ensFluxC[k].b
                            else:
                                CPbrC=puissE*ensFluxC[k].CP/ensFluxC[k].b
                            if ensFluxC[k].verif!=0:
                                print("verif")
                                puissE=min((ensFluxC[k].b-ensFluxC[k].b1),ensFluxF[j].chargeThE)
                                ensFluxC[k].b1+=puissE

                        if ensFluxF[j].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                            CPbrF=ensFluxF[j].CP
                        else:#sinon on pondère le CP avec la puissance du flux complémentaire
                            """if ensFluxF[j].ech=="non":
                                ensFluxF[j].b,annul=Division.divE1(ensFluxC,ensFluxF,j,TpincementC,TpincementF,deltaTmin)#le but est de simuler les prochains échanges avec le flux froid divisé pour connaître la valeur de son b. 
                            """
                            """print(ensFluxF[j].b)
                            print(ensFluxF[j].CP)
                            print(ensFluxF[j].div)
                            print(puissE)"""
                            CPbrF=puissE*ensFluxF[j].CP/ensFluxF[j].b
                        if ensFluxF[j].numero==5:
                            """print(ensFluxF[j].numero)
                            print(ensFluxC[k].numero)
                            print(CPbrC)
                            print(CPbrF)
                            print(ensFluxC[k].div)
                            print(puissE)
                            print(ensFluxC[k].test)"""
                        if annul1=="non" and ((ensFluxC[k].div!=0 and ensFluxF[j].numero in ensFluxC[k].test) or ensFluxC[k].div==0):#si un des deux flux ne peut pas échanger, alors on ne fait pas l'échange. Le test permet de vérifier que le b du flux chaud divisé a été calculé pour échanger avec ce flux froid (sinon erreur). Si le flux n'est pas divisé cela n'a pas besoin d'être vérifié
                            bclDiv="non"
                            #print(CP)
                            ech,CP=Fct.echE1(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,k,j,CPbrF,CPbrC,ech,bclDiv,CP,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)
                            #print(CP)
                            #print("div" +str(ensFluxC[k].div))
                        if ensFluxC[k].chargeThE==0:
                            CP[k]=0#cela permet de ne pas diviser à nouveau un flux chaud
    print("")
    print("")
    print("")
    return(longF,longC,Reseau)





def Reseau2(ensFluxF,ensFluxC,CP,TpincementF,TpincementC,deltaTmin,longF,longC,Reseau):
    print("") 
    print("Réseau 2") 
    puissE=0#puissance de l'échange de chaleur
    ensFluxCinit=[]
    ensFluxFinit=[]
    listeCouple=[]
    for j in range(len(ensFluxF)):#détermination des couples et de leurs puissances
        div=[]
        for i in range(len(ensFluxC)):
            div.append(ensFluxC[i].div)
        ech=0#indique si le fluide a échangé de la chaleur
        imp=0#indique si le fluide ne peut pas échanger avec les flux chauds car sa Te est supérieur à toute les Te des flux chauds
        for i in range(len(ensFluxC)):
            #print(ensFluxC[i].div)
            annul="non"
            print("num flux c"+str(ensFluxC[i].numero)+"-f"+str(ensFluxF[j].numero)+"/div: "+str(ensFluxC[i].div)+"/chargeThE: "+str(ensFluxC[i].chargeThE))
            if ensFluxF[j].CP<=ensFluxC[i].CP or ensFluxF[j].Ts<TpincementF:#Calcul puissance échangée
                if ensFluxF[j].chargeThE!=0 and ensFluxC[i].chargeThE!=0:#on vérifie que les deux fluides ne sont pas déjà satisfait énergétiquement
                    puissE=min(ensFluxC[i].chargeThE,ensFluxF[j].chargeThE)
                    if ensFluxC[i].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                        #print("div=0")
                        CPbrC=ensFluxC[i].CP
                    else:#nous devons d'abord déterminer avec quel flux le flud divisé froid va échanger pour connaitre quel sera le dénominateur de CPbrF
                        if ensFluxC[i].ech=="non":
                            #print("div avant :" +str(ensFluxC[i].div))
                            #print("entrée divE")
                            ensFluxC[i].b,annul,annuldiv,m,test,CP1=Division.divE(ensFluxC,ensFluxF,i,j,TpincementC,TpincementF,deltaTmin,ech,CP,"",Reseau,ensFluxCinit,ensFluxFinit,listeCouple)#on connait maitenant le dénominateur de CPbrF
                            #print("sortie divE")
                            CP=CP1
                            #print(ensFluxC[i].b)
                            #print(CP)
                            #print("div après :" +str(ensFluxC[i].div))
                            if ensFluxC[i].puissModif=="oui":#lorsque la puissance échangée a été modifié dans la fct divE car on a échangé moins que la charge thermique minimale des deux flux
                                puissE=ensFluxC[i].b
                            if annul=="non":
                                if ensFluxC[i].div>0:#car sinon cela veut dire qu'on a annulé toutes ses branches
                                    CP[i]=0#permet de ne pas diviser un flux tant que toutes ses branches n'ont pas fini d'avoir échangé (sinon problème au niveau des .div)
                            #print(ensFluxC[i].numero)
                            if annuldiv=="oui":
                                #print(CP)
                                CPdiv=CP[i]
                                CP[i]=0#on ne va pas diviser le flux actuel alors qu'on cherche à annuler sa division
                                CPcompt=0
                                div=[]
                                CPdiv1=[]
                                CPdiv1=copy.deepcopy(CP)
                                for h in range(len(ensFluxC)):#on sauvegarde la valeur des div avant division
                                    div.append(ensFluxC[h].div)
                                while ensFluxC[i].div!=0:
                                    verif=0
                                    for h in range(len(CP)):
                                        verif+=CP[h]
                                    if verif==0:#si verif=0 alors tous les flux sont déjà satisfaits
                                        print("1Tous les flux sont satisfaits. Division d'un flux chaud impossible")
                                        #print(CP)
                                        for h in range(len(ensFluxC)):
                                            ensFluxC[h].div=div[h]
                                        CP=CPdiv1
                                        #print(CP)
                                        break#permet de stopper la boucle while annul!="non"
                                    #print(verif)
                                    if ensFluxC[i].div==1:
                                        ensFluxC[i].div=0
                                    else:
                                        ensFluxC[i].div-=0.5
                                    CPcompt+=1
                                    print("On annule la division du flux c"+str(ensFluxC[i].numero))#car une des branches des flux échanges toutes sa chaleur
                                    longC-=1
                                    #division d'un nouveau flux pour toujours respecter la règle des flux
                                    ind=CP.index(max(CP))
                                    print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
                                    CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                                    if ensFluxC[ind].div==0:
                                        ensFluxC[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                                    else:
                                        ensFluxC[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                                    longC+=1
                                CP[i]=CPdiv*2*CPcompt#on lui réattribue sa valeur moins les branches retirées (annulées)
                                #print(CP)
                                CPbrC=ensFluxC[i].CP
                            else:
                                """print("stop")
                                print(puissE)
                                print(ensFluxC[i].CP)
                                print(ensFluxC[i].b)"""
                                CPbrC=puissE*ensFluxC[i].CP/ensFluxC[i].b
                                #print(CPbrC)
                        else:
                            CPbrC=puissE*ensFluxC[i].CP/ensFluxC[i].b
                        if ensFluxC[i].verif!=0:
                            #print("verif")
                            #print(verif)
                            puiss=min((ensFluxC[i].b-ensFluxC[i].b1),ensFluxF[j].chargeThE)
                            ensFluxC[i].b1+=puiss
                            CPbrC=puiss*ensFluxC[i].CP/ensFluxC[i].b
                        if ensFluxF[j].numero==5: 
                            """print(CPbrC)
                            print(puiss)
                            print(ensFluxC[i].CP)
                            print(ensFluxC[i].numero)
                            print(ensFluxF[j].numero)
                            print(ensFluxC[i].div)
                            print(ensFluxC[i].test)"""

                    """print("boucle1-affich:")
                    print(ensFluxF[j].numero)
                    print(ensFluxC[i].numero)
                    print(ensFluxC[i].div)
                    print(annul)
                    print(ensFluxC[i].test)"""
                    if annul!="oui" and ((ensFluxC[i].div!=0 and ensFluxF[j].numero in ensFluxC[i].test) or ensFluxC[i].div==0):
                        #print("entrée pour échange")
                        #print(CP)
                        bclDiv="non"
                        #print(CP)
                        #print(CPbrC)
                        ech,CP=Fct.echE(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,i,j,CPbrC,ech,CP,bclDiv,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)
                        #print(CP)
                        #print("div flux chaud" +str(ensFluxC[i].div))
                    if ensFluxC[i].chargeThE==0 and len(CP)!=0:#car si aucun flux chaud n'a été divisé, CP[i] n'existera pas
                        CP[i]=0#cela permet de ne pas diviser à nouveau un flux chaud
            if ensFluxF[j].Te>ensFluxC[i].Te or ensFluxC[i].chargeThE==0:
                imp+=1
        if (ech==0 or ensFluxF[j].chargeThE!=0) and imp<len(ensFluxC)-1 and ensFluxF[j].Ts>TpincementF:#Si le fluide n'a pas pu échanger avec aucun flux mais que sa Te lui permet d'échanger de la chaleur, alors son CP est trop grand : on va le diviser. On vérifie aussi qu'il atteint la T de pincement car sinon il n'a pas besoin de respecter la règle du CP
            CPbrF=0#CP de chaque branche du flux froid divisé
            CPbrC=0#CP de chaque branche du flux chaud divisé
            annul="oui"
            div=[]
            CPdiv1=[]
            CPdiv1=copy.deepcopy(CP)
            ensFluxF[j].b2=0
            chargeThEfr=copy.deepcopy(ensFluxF[j].chargeThE)
            for h in range(len(ensFluxC)):#on sauvegarde la valeur des div avant division
                div.append(ensFluxC[h].div)
            while annul!="non":
                ensFluxF[j].b2+=1
                verif=0
                for h in range(len(CP)):
                    verif+=CP[h]
                if verif<0.01:#Car sinon on aura une boucle infini car les flux chauds seront divisés jusqu'à ce que la boucle while soit satisfaite
                    print("2Tous les flux sont satisfaits. Division d'un flux chaud impossible")
                    for h in range(len(ensFluxC)):#comme l'échange n'est pas possible malgré les division, on annule les divisions en rétablissant les div
                        ensFluxC[h].div=div[h]
                    CP=CPdiv1
                    verif=0#car on teste la valeur de verif par la suite par rapport à 0. On considère dans ce cas que verif=0
                    break#permet de stopper la boucle while annul!="non"
                if ensFluxF[j].numero!=10 and ensFluxF[j].numero!=11 and ensFluxF[j].numero!=7 and ensFluxF[j].numero!=8 and ensFluxF[j].numero!=9 and ensFluxF[j].numero!=3:
                    print("Le fluide froid f"+str(ensFluxF[j].numero)+" doit être divisé en deux.")
                if ensFluxF[j].div==0:
                    ensFluxF[j].div+=1
                else:
                    ensFluxF[j].div+=0.5
                longF+=1
                while longF>longC:#on vérifie à nouveau la condition sur le nombre de flux et indique à l'utilisateur que le flux doit être divisé en deux. On divise le fluide chaud qui a le plus grand CP pour que la condition sur les CP soit conservé. Jsuqu'à ce que le nombre de flux froids soit inférieur au nombre de flux chauds.
                    ind=CP.index(max(CP))
                    if ensFluxF[j].numero!=10 and ensFluxF[j].numero!=11 and ensFluxF[j].numero!=7 and ensFluxF[j].numero!=8 and ensFluxF[j].numero!=9 and ensFluxF[j].numero!=3:
                        print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
                    CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                    if ensFluxC[ind].div==0:
                        ensFluxC[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                    else:
                        ensFluxC[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                    longC+=1
                condCharge=0
                for i in range (len(ensFluxC)):
                    if ensFluxC[i].chargeThE==0:
                        condCharge+=1
                #if condCharge==len(ensFluxC):
                """print(len(ensFluxC))
                print(condCharge)"""
                ensFluxF[j].b,annul=Division.divE1(ensFluxC,ensFluxF,j,TpincementC,TpincementF,deltaTmin,CP,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)#le but est de simuler les prochains échanges avec le flux froid divisé pour connaître la valeur de son b. 
            ensFluxF[j].chargeThE=chargeThEfr
            div=[]
            for h in range(len(ensFluxC)):#on sauvegarde la valeur des div avant division
                div.append(ensFluxC[h].div)
            #print(ensFluxF[j].b)
            
            if verif!=0:
                print("Echange possible avec flux froid divisé : f"+str(ensFluxF[j].numero))
                #print("")
                #CP=CPdiv1
                #print(CP)
                #print(div)
                for k in range(len(ensFluxC)):
                    annul1="non"
                    ensFluxC[k].verif=0
                    #print(ensFluxC[k].chargeThE)
                    #print(ensFluxF[j].chargeThE)
                    if ensFluxC[k].chargeThE!=0 and ensFluxF[j].chargeThE!=0:#si les fluides ne sont pas satisfait et le fluide froid possède encore des branches non utilisées (on considère un échange par branche)
                        puissE=min(ensFluxC[k].chargeThE,ensFluxF[j].chargeThE)
                        if ensFluxC[k].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                            CPbrC=ensFluxC[k].CP
                        else:#sinon on pondère le CP avec la puissance du flux complémentaire
                            if ensFluxC[k].ech=="non":
                                #vérifier que retourner m et test est vraiment utile !?
                                ensFluxC[k].b,annul1,annuldiv,m,test,CP=Division.divE(ensFluxC,ensFluxF,k,j,TpincementC,TpincementF,deltaTmin,ech,CP,"echE1",Reseau,ensFluxCinit,ensFluxFinit,listeCouple)#le but est de simuler les prochains échanges avec le flux chaud divisé pour connaître la valeur de son b
                                CPdiv=CP[k]#on ne va pas diviser le flux actuel alors qu'on cherche à annuler sa division
                                CPdiv1=[]
                                CPdiv1=copy.deepcopy(CP)
                                if annul=="non":
                                    if ensFluxC[k].div>0:
                                        CP[k]=0#permet de ne pas diviser un flux dont toutes ses branches n'ont pas fini d'avoir échangé (sinon problème au niveau des .div)
                                if annuldiv=="oui":
                                    CP[k]=0
                                    CPcompt=0
                                    div=[]
                                    for h in range(len(ensFluxC)):#on sauvegarde la valeur des div avant division
                                        div.append(ensFluxC[h].div)
                                    while ensFluxC[k].div!=0:
                                        for h in range(len(CP)):
                                            verif+=CP[h]
                                        if verif==0:#si verif=0 alors tous les flux sont déjà satisfaits
                                            print("3Tous les flux sont satisfaits. Division d'un flux chaud impossible")
                                            for h in range(len(ensFluxC)):
                                                ensFluxC[h].div=div[h]
                                            CP=CPdiv1
                                            break#permet de stopper la boucle while annul!="non"
                                        CPcompt+=1
                                        if ensFluxC[k].div==1:
                                            ensFluxC[k].div=0
                                        else:
                                            ensFluxC[k].div-=0.5
                                        print("On annule la division du flux c"+str(ensFluxC[k].numero))#car une des branches des flux échange toute sa chaleur
                                        #print(ensFluxC[k].div)
                                        #division d'un nouveau flux pour toujours respecter la règle des flux
                                        ind=CP.index(max(CP))
                                        print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
                                        CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                                        if ensFluxC[ind].div==0:
                                            ensFluxC[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                                        else:
                                            ensFluxC[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                                    CP[k]=CPdiv*2*CPcompt#on lui réattribue sa valeur moins les branches retirées (annulées)
                                    CPbrC=ensFluxC[k].CP
                                else:
                                    CPbrC=puissE*ensFluxC[k].CP/ensFluxC[k].b
                            else:
                                CPbrC=puissE*ensFluxC[k].CP/ensFluxC[k].b
                            if ensFluxC[k].verif!=0:
                                #print("verif")
                                puissE=min((ensFluxC[k].b-ensFluxC[k].b1),ensFluxF[j].chargeThE)
                                ensFluxC[k].b1+=puissE

                        if ensFluxF[j].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                            CPbrF=ensFluxF[j].CP
                        else:#sinon on pondère le CP avec la puissance du flux complémentaire
                            """if ensFluxF[j].ech=="non":
                                ensFluxF[j].b,annul=Division.divE1(ensFluxC,ensFluxF,j,TpincementC,TpincementF,deltaTmin)#le but est de simuler les prochains échanges avec le flux froid divisé pour connaître la valeur de son b. 
                            """
                            """print(ensFluxF[j].b)
                            print(ensFluxF[j].CP)
                            print(ensFluxF[j].div)
                            print(puissE)"""
                            CPbrF=puissE*ensFluxF[j].CP/ensFluxF[j].b
                        if ensFluxF[j].numero==5:
                            """print(ensFluxF[j].numero)
                            print(ensFluxC[k].numero)
                            print(CPbrC)
                            print(CPbrF)
                            print(ensFluxC[k].div)
                            print(puissE)
                            print(ensFluxC[k].test)"""
                        if annul1=="non" and ((ensFluxC[k].div!=0 and ensFluxF[j].numero in ensFluxC[k].test) or ensFluxC[k].div==0):#si un des deux flux ne peut pas échanger, alors on ne fait pas l'échange. Le test permet de vérifier que le b du flux chaud divisé a été calculé pour échanger avec ce flux froid (sinon erreur). Si le flux n'est pas divisé cela n'a pas besoin d'être vérifié
                            bclDiv="non"
                            #print(CP)
                            ech,CP=Fct.echE1(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,k,j,CPbrF,CPbrC,ech,bclDiv,CP,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)
                            #print(CP)
                            #print("div" +str(ensFluxC[k].div))
                        if ensFluxC[k].chargeThE==0:
                            CP[k]=0#cela permet de ne pas diviser à nouveau un flux chaud
    return(longF,longC,Reseau)




