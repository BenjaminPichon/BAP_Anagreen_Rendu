# -*- coding: utf-8 -*-
"""

Created on mai 27  

@author: p-aToussaint
"""
import matplotlib.pyplot as plt
from operator import itemgetter, attrgetter
import copy
import pickle

from creation_reseau_statique import Fct,MERContinue1, Division
from donnees import Donnees
from classes import Flux,reseau,kpi,ssFlux,utilite


def reseauDown(ensFluxF,ensFluxC,TpincementF,TpincementC,deltaTmin,listeCouple,listeUtilite,listeSsFlux,deltaH,kpi,MerDessousTab,r):
    
        
    #on créé des nouvelles liste qu'on ne modifiera pas, cela permettra d'avoir accès aux températures d'entrée/sortie dans flux (car elles sont modifiés pour les listes ensFluxC/F)
    ensFluxFinit=copy.deepcopy(ensFluxF)
    ensFluxCinit=copy.deepcopy(ensFluxC)

    puissE=0#puissance de l'échange de chaleur
    puissUC=0
    puissUF=0
    Reseau=[]
    
    if len(ensFluxF)!=0 and len(ensFluxC)!=0:#car sinon aucun échange ne peut avoir lieu, dans ce cas, on ne se servira que des utilités 

        #Respect de la règle sur le nombre de flux
        CP=[]
        longC=len(ensFluxC)
        longF=len(ensFluxF)
        for i in range(len(ensFluxC)):#on divise le fluide chaud qui a le plus grand CP pour que la condition sur les CP soit conservé. Jsuqu'à ce que le nombre de flux froids soit inférieur au nombre de flux chauds.
            CP.append(ensFluxC[i].CP)
        if longF>longC:#on vérifie la condition sur le nombre de flux et indique à l'utilisateur que le flux doit être divisé en deu
            while longF>longC:
                ind=CP.index(max(CP))
                print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
                CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                if ensFluxC[ind].div==0:
                    ensFluxC[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                else:
                    ensFluxC[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                longC+=1
                
        affichageFluxC=[]
        affichageFluxF=[]
        for i in range(len(ensFluxC)):
            affichageFluxC.append(ensFluxC[i].numero)
        for j in range(len(ensFluxF)):
            affichageFluxF.append(ensFluxF[j].numero)

        newTe=[]
        for j in range(len(ensFluxF)):
            ensFluxF[j].newTe=ensFluxF[j].Te
            ensFluxF[j].newTeNum=-1#pour ne pas lui attribuer un numero de flux
            newTe.append(copy.deepcopy(ensFluxF[j].Te))




        
        #Etablissement du réseau 
        for j in range(len(ensFluxF)):#détermination des couples et de leurs puissances
            print("----------------")
            div=[]
            
            for i in range(len(ensFluxC)):
                div.append(ensFluxC[i].div)
            print("CP : "+str(CP))
            ech=0#indique si le fluide a échangé de la chaleur
            imp=0#indique si le fluide ne peut pas échanger avec les flux chauds car sa Te est supérieur à toute les Te des flux chauds
            for i in range(len(ensFluxC)):
                annul="non"
                print("num flux c"+str(ensFluxC[i].numero)+"-f"+str(ensFluxF[j].numero)+"/divC	: "+str(ensFluxC[i].div)+"/chargeThEC: "+str(ensFluxC[i].chargeThE))
                print(ensFluxF[j].chargeThE)
                if ensFluxC[i].Te<=ensFluxF[j].Te+deltaTmin or ensFluxC[i].chargeThE==0:
                    imp+=1
                if ensFluxF[j].CP<=ensFluxC[i].CP or ensFluxF[j].Ts<TpincementF:#Calcul puissance échangée
                    if ensFluxF[j].chargeThE>10**(-10) and ensFluxC[i].chargeThE!=0 and ensFluxC[i].Te>ensFluxF[j].Te+deltaTmin:#on vérifie que les deux fluides ne sont pas déjà satisfait énergétiquement ; >10**(-10) : car à cause des arrondi pour le test ensFluxC.chargeThE1==0 de la fct divE, celui-ci était vrai alors que la valeur était =10^(-14)  ; ensFluxC[i].Te>ensFluxF[j].Te+deltaTmin : car sinon les deux fluides ne peuvent pas échanger de chaleur
                        puissE=min(ensFluxC[i].chargeThE,ensFluxF[j].chargeThE)
                        if ensFluxC[i].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                            
                            CPbrC=ensFluxC[i].CP
                        else:#nous devons d'abord déterminer avec quel flux le flud divisé froid va échanger pour connaitre quel sera le dénominateur de CPbrF
                            print(ensFluxC[i].ech)
                            if ensFluxC[i].ech=="non":#demande si la valeur du b a déjà été 

                                ensFluxC[i].b,annul,annuldiv,m,test,CP1=Division.divE(ensFluxC,ensFluxF,i,j,TpincementC,TpincementF,deltaTmin,ech,CP,"echE",Reseau,ensFluxCinit,ensFluxFinit,listeCouple)#on connait maitenant le dénominateur de CPbrF

                                CP=CP1

                                if ensFluxC[i].puissModif=="oui":#lorsque la puissance échangée a été modifié dans la fct divE car on a échangé moins que la charge thermique minimale des deux flux
                                    
                                    puissE=ensFluxC[i].b
                                if annul=="non" and annuldiv!="oui":
                                    if ensFluxC[i].div>0:#car sinon cela veut dire qu'on a annulé toutes ses branches
                                        CP[i]=0#permet de ne pas diviser un flux tant que toutes ses branches n'ont pas fini d'avoir échangé (sinon problème au niveau des .div)
             
                                if annuldiv=="oui":
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
                                             
                                            for h in range(len(ensFluxC)):
                                                ensFluxC[h].div=div[h]
                                            CP=CPdiv1
                                            break#permet de stopper la boucle while annul!="non"
                                         
                                        if ensFluxC[i].div==1:
                                            ensFluxC[i].div=0
                                        else:
                                            ensFluxC[i].div-=0.5
                                        CPcompt+=1
                                        
                                        longC-=1
                                        #division d'un nouveau flux pour toujours respecter la règle des flux
                                        ind=CP.index(max(CP))
                                        
                                        CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                                        if ensFluxC[ind].div==0:
                                            ensFluxC[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                                        else:
                                            ensFluxC[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                                        longC+=1
                                    CP[i]=CPdiv*2**CPcompt#on lui réattribue sa valeur moins les branches retirées (annulées)
                                   
                                    CPbrC=ensFluxC[i].CP
                                else:
                                    
                                    CPbrC=puissE*ensFluxC[i].CP/ensFluxC[i].b
                            else:
                                CPbrC=puissE*ensFluxC[i].CP/ensFluxC[i].b
                            
                            if ensFluxC[i].verif!=0 and annul!="oui" and ((ensFluxC[i].div!=0 and ensFluxF[j].numero in ensFluxC[i].test) or ensFluxC[i].div==0):#on modifie b1 que si le flux va échanger avec le flux froid en question et si son verif!=0
                                print("verif")
                                print(ensFluxC[i].b)
                                print(ensFluxC[i].b1)
                                print("ensFluxF[j].chargeThE : "+str(ensFluxF[j].chargeThE))
                                print("ensFluxF[j].chargeThE1 : "+str(ensFluxF[j].chargeThE1))
                                if ensFluxF[j].chargeThE1==0:#car cela veut dire qu'elle n'a pas été modifiée
                                    print("1")
                                    print((ensFluxC[i].b-ensFluxC[i].b1))
                                    puiss=min((ensFluxC[i].b-ensFluxC[i].b1),ensFluxF[j].chargeThE,(min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF[j].Ts)-max(ensFluxF[j].Te,ensFluxF[j].Te))*ensFluxF[j].CP)
                                else:
                                    print("2")
                                    puiss=min((ensFluxC[i].b-ensFluxC[i].b1),ensFluxF[j].chargeThE1)
                                puissE=puiss
                                print("ensFluxC[i].b : "+str(ensFluxC[i].b))
                                print("ensFluxC[i].b1 : "+str(ensFluxC[i].b1))
                                print(ensFluxF[j].chargeThE1)
                                print(puiss)
                                print(ensFluxC[i].b)
                                print(ensFluxC[i].div)
                                ensFluxC[i].b1+=puiss
                                if ensFluxC[i].b1==ensFluxC[i].b:#car s'il s'agit de la dernière branche alors elle va compléter le b. Et on doit garder la valeur de b1 tel quel calculé la valeeur du dernier échange de la branche du flux divisé dans la fct ech
                                    ensFluxC[i].b1-=puiss
                                print("ensFluxC[i].b1 : "+str(ensFluxC[i].b1))
                                CPbrC=puiss*ensFluxC[i].CP/ensFluxC[i].b
                            if ensFluxF[j].numero==1: 
                                print(CPbrC)
                                print(puissE)
                                print(ensFluxC[i].CP)
                                print(ensFluxC[i].numero)
                                print(ensFluxF[j].numero)
                                print(ensFluxC[i].div)
                                print(ensFluxC[i].test)


                        print("puissE 3 : "+str(puissE))
                        if annul!="oui" and ((ensFluxC[i].div!=0 and ensFluxF[j].numero in ensFluxC[i].test) or ensFluxC[i].div==0) and puissE!=0:
                            print("entrée pour échange")

                            bclDiv="non"
                            
                            ech,CP=Fct.echE(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,i,j,CPbrC,ech,CP,bclDiv,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)

                        if ensFluxC[i].chargeThE==0 and len(CP)!=0:#car si aucun flux chaud n'a été divisé, CP[i] n'existera pas
                            CP[i]=0#cela permet de ne pas diviser à nouveau un flux chaud

            if ech==0 and imp<len(ensFluxC)-1:#and ensFluxF[j].Ts>TpincementF # (... or ensFluxF[j].chargeThE!=0) ; Si le fluide n'a pas pu échanger avec aucun flux mais que sa Te lui permet d'échanger de la chaleur, alors son CP est trop grand : on va le diviser. On vérifie aussi qu'il atteint la T de pincement car sinon il n'a pas besoin de respecter la règle du CP
                print("boucle ech==0")
                print("CP : "+str(CP))
                CPbrF=0#CP de chaque branche du flux froid divisé
                CPbrC=0#CP de chaque branche du flux chaud divisé
                annul="oui"
                div=[]
                CPdiv1=[]
                CPdiv1=copy.deepcopy(CP)
                ensFluxF[j].b2=0
                chargeThEfr=copy.deepcopy(ensFluxF[j].chargeThE)#car celle-ci est modifié dans la boucle divE1
                ensFluxC1=copy.deepcopy(ensFluxC)
                ensFluxF[j].echChargeTh="oui"
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
                    if ensFluxF[j].numero!=10 and ensFluxF[j].numero!=7 and ensFluxF[j].numero!=8 and ensFluxF[j].numero!=9 and ensFluxF[j].numero!=3:
                        print("Le fluide froid f"+str(ensFluxF[j].numero)+" doit être divisé en deux.")
                    if ensFluxF[j].div==0:
                        ensFluxF[j].div+=1
                    else:
                        ensFluxF[j].div+=0.5
                    longF+=1
                    while longF>longC:#on vérifie à nouveau la condition sur le nombre de flux et indique à l'utilisateur que le flux doit être divisé en deux. On divise le fluide chaud qui a le plus grand CP pour que la condition sur les CP soit conservé. Jsuqu'à ce que le nombre de flux froids soit inférieur au nombre de flux chauds.
                        ind=CP.index(max(CP))
                        if ensFluxF[j].numero!=10  and ensFluxF[j].numero!=7 and ensFluxF[j].numero!=8 and ensFluxF[j].numero!=9 and ensFluxF[j].numero!=3:
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

                    ensFluxF[j].b,annul=Division.divE1(ensFluxC,ensFluxF,j,TpincementC,TpincementF,deltaTmin,CP,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)#le but est de simuler les prochains échanges avec le flux froid divisé pour connaître la valeur de son b. 
                ensFluxF[j].chargeThE=chargeThEfr
                div=[]
                for h in range(len(ensFluxC)):#on sauvegarde la valeur des div avant division
                    div.append(ensFluxC[h].div)

                if verif<0.01:#alors on va autoriser d'échanger moins que la charge Th du flux froid
                    print("")
                    print("On va échanger moins que la charge Th du fluide froid")
                    chargeThEfr=copy.deepcopy(ensFluxF[j].chargeThE)#car celle-ci est modifié dans la boucle divE1
                    CP=CPdiv1
                    ensFluxC=copy.deepcopy(ensFluxC1)
                    ensFluxF[j].echChargeTh="non"
                    annul="oui"
                    ensFluxF[j].div=0
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
                        if ensFluxF[j].numero!=10 and ensFluxF[j].numero!=7 and ensFluxF[j].numero!=8 and ensFluxF[j].numero!=9 and ensFluxF[j].numero!=3:
                            print("Le fluide froid f"+str(ensFluxF[j].numero)+" doit être divisé en deux.")
                        if ensFluxF[j].div==0:
                            ensFluxF[j].div+=1
                        else:
                            ensFluxF[j].div+=0.5
                        longF+=1
                        while longF>longC:#on vérifie à nouveau la condition sur le nombre de flux et indique à l'utilisateur que le flux doit être divisé en deux. On divise le fluide chaud qui a le plus grand CP pour que la condition sur les CP soit conservé. Jsuqu'à ce que le nombre de flux froids soit inférieur au nombre de flux chauds.
                            ind=CP.index(max(CP))
                            if ensFluxF[j].numero!=10  and ensFluxF[j].numero!=7 and ensFluxF[j].numero!=8 and ensFluxF[j].numero!=9 and ensFluxF[j].numero!=3:
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
                                
                        ensFluxF[j].b,annul=Division.divE1(ensFluxC,ensFluxF,j,TpincementC,TpincementF,deltaTmin,CP,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)#le but est de simuler les prochains échanges avec le flux froid divisé pour connaître la valeur de son b. 
                    ensFluxF[j].chargeThE=chargeThEfr




                
                if verif!=0:
                    print("Echange possible avec flux froid divisé : f"+str(ensFluxF[j].numero))
                    
                    ancienCP=0
                    print("ancien CP : "+str(ancienCP))
                    for k in range(len(ensFluxC)):
                        annul1="non"
                        ensFluxC[k].verif=0
                        
                        if ensFluxC[k].chargeThE!=0 and ensFluxF[j].chargeThE!=0:#si les fluides ne sont pas satisfait et le fluide froid possède encore des branches non utilisées (on considère un échange par branche)
                            puissA1=ensFluxC[k].CP*(min(TpincementF,ensFluxF[j].Ts)-ensFluxF[j].Te)#on égalise le CP du flux chaud et froid pour que l'échange soit possible
                            puissE=min(ensFluxC[k].chargeThE,ensFluxF[j].chargeThE,puissA1)
                            if ensFluxC[k].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                                CPbrC=ensFluxC[k].CP
                            else:#sinon on pondère le CP avec la puissance du flux complémentaire
                                if ensFluxC[k].ech=="non":
                                    if ensFluxF[j].numero==5:
                                        print("1-entréedivE")
                                        
                                    #vérifier que retourner m et test est vraiment utile !?
                                    
                                    print(ensFluxF[j].chargeThE)
                                    ensFluxC[k].b,annul1,annuldiv,m,test,CP=Division.divE(ensFluxC,ensFluxF,k,j,TpincementC,TpincementF,deltaTmin,ech,CP,"echE1",Reseau,ensFluxCinit,ensFluxFinit,listeCouple)#le but est de simuler les prochains échanges avec le flux chaud divisé pour connaître la valeur de son b ; echE est correct
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
                                            
                                            #division d'un nouveau flux pour toujours respecter la règle des flux
                                            ind=CP.index(max(CP))
                                            print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
                                            CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                                            if ensFluxC[ind].div==0:
                                                ensFluxC[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                                            else:
                                                ensFluxC[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                                        CP[k]=CPdiv*2**CPcompt#on lui réattribue sa valeur moins les branches retirées (annulées)
                                        CPbrC=ensFluxC[k].CP
                                    else:
                                        if ensFluxC[k].plusEch=="non":
                                            CPbrC=ensFluxC[k].CP
                                        else:
                                            """print("puissE : "+str(puissE))
                                            print("ensFluxC[k].CP : "+str(ensFluxC[k].CP))
                                            print("ensFluxC[k].b :"+str(puissE))"""
                                            CPbrC=puissE*ensFluxC[k].CP/ensFluxC[k].b
                                else:
                                    """print("puissE : "+str(puissE))
                                    print("ensFluxC[k].CP : "+str(ensFluxC[k].CP))
                                    print("ensFluxC[k].b :"+str(puissE))"""
                                    CPbrC=puissE*ensFluxC[k].CP/ensFluxC[k].b
                                if ((ensFluxC[k].verif!=0 and annul1=="non")) and ((ensFluxC[k].div!=0 and ensFluxF[j].numero in ensFluxC[k].test) or ensFluxC[k].div==0):#on modifie b1 que si le flux va échanger avec le flux froid en question et si son verif!=0
                                    print("verif")
                                    puissE=min((ensFluxC[k].b-ensFluxC[k].b1),ensFluxF[j].chargeThE)
                                    ensFluxC[k].b1+=puissE
                                    CPbrC=puissE*ensFluxC[k].CP/ensFluxC[k].b
                                
                                
                                



                            if ensFluxF[j].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                                CPbrF=ensFluxF[j].CP
                            else:#sinon on pondère le CP avec la puissance du flux complémentaire
                                """if ensFluxF[j].ech=="non":
                                    ensFluxF[j].b,annul=Division.divE1(ensFluxC,ensFluxF,j,TpincementC,TpincementF,deltaTmin)#le but est de simuler les prochains échanges avec le flux froid divisé pour connaître la valeur de son b. 
                                """
                                print(ensFluxF[j].b)
                                print(ensFluxF[j].CP)
                                print(ensFluxF[j].div)
                                print(puissE)

                                if ensFluxF[j].echChargeTh=="non" and annul1=="non" and ensFluxC[k].numero in ensFluxF[j].test and ((ensFluxC[k].div!=0 and ensFluxF[j].numero in ensFluxC[k].test) or ensFluxC[k].div==0) and puissE!=0:#on mets toutes ces conditions pour que ancienCP soit modifié que si l'échange aura lieu
                                    print("ancienCP : "+str(ancienCP))
                                    if ensFluxF[j].div!=0.5:#permet de savoir s'il sagit de la dernière branche ou pas
                                        CPbrF=ensFluxC[k].CP
                                        ancienCP+=CPbrF#permettra de connaître la valeur des autres branches lors de l'échange avec la dernière branche
                                    else:
                                        print("ensFluxF[j].CP : "+str(ensFluxF[j].CP))
                                        CPbrF=ensFluxF[j].CP-ancienCP
                                else:
                                    CPbrF=puissE*ensFluxF[j].CP/ensFluxF[j].b

                            if ensFluxF[j].echChargeTh=="non" and ensFluxC[k].numero in ensFluxF[j].test and ((ensFluxC[k].div!=0 and ensFluxF[j].numero in ensFluxC[k].test) or ensFluxC[k].div==0):#on modifie b1 que si le flux va échanger avec le flux froid en question et si son verif!=0
                                puissE=min((ensFluxF[j].tempMin-ensFluxF[j].Te)*CPbrF,(ensFluxF[j].b-ensFluxF[j].b1))
                                ensFluxF[j].b1+=puissE

                            print(ensFluxF[j].Te)
                            print(CPbrF)
                            print(ensFluxF[j].b)
                            print(ensFluxF[j].b1)
                            print("min((ensFluxC[k].b-ensFluxC[k].b1),ensFluxF[j].chargeThE,(ensFluxF[j].b-ensFluxF[j].b1))"+str(min((ensFluxC[k].b-ensFluxC[k].b1),ensFluxF[j].chargeThE,(ensFluxF[j].b-ensFluxF[j].b1))))

                            if ensFluxF[j].numero==11:
                                print(ensFluxF[j].numero)
                                print(ensFluxC[k].numero)
                                print(CPbrC)
                                print(CPbrF)
                                print(ensFluxC[k].div)
                                print(puissE)
                                print(ensFluxC[k].test)
                            if annul1=="non" and ensFluxC[k].numero in ensFluxF[j].test and ((ensFluxC[k].div!=0 and ensFluxF[j].numero in ensFluxC[k].test) or ensFluxC[k].div==0) and puissE!=0:#si un des deux flux ne peut pas échanger, alors on ne fait pas l'échange. Le test permet de vérifier que le b du flux chaud divisé a été calculé pour échanger avec ce flux froid (sinon erreur). Si le flux n'est pas divisé cela n'a pas besoin d'être vérifié
                                bclDiv="non"
                                ech,CP=Fct.echE1(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,k,j,CPbrF,CPbrC,ech,bclDiv,CP,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)
                            if ensFluxC[k].chargeThE==0:
                                CP[k]=0#cela permet de ne pas diviser à nouveau un flux chaud



        if MerDessousTab==[]:#Dans ce cas on est en continu
            for i in range(len(ensFluxC)):#Calcul puissance utilité froide				
                if ensFluxC[i].chargeThE>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TeC=min(TpincementC,ensFluxC[i].Te)
                    TsC=TeC-ensFluxC[i].chargeThE/ensFluxC[i].CP
                    if ensFluxC[i].process==True:
                        print("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3)))		
                        Reseau.append("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3)))
                    ssFluxC=ssFlux.ssFlux(TeC,TsC,ensFluxC[i].CP*1000,ensFluxC[i].debVol,ensFluxC[i].rho,ensFluxC[i].mu,ensFluxC[i].lamb,ensFluxC[i].press,ensFluxCinit[i],ensFluxC[i].type,False,True,ensFluxC[i].chargeThE)
                    ensFluxC[i].listeSsFlux.append(ssFluxC)
                    listeUtilite.append(utilite.utilite(ssFluxC,ensFluxC[i].chargeThE,"f",TeC,TsC))
                    puissUF+=ensFluxC[i].chargeThE
            for j in range(len(ensFluxF)):#Calcul puissance utilité chaude				
                if ensFluxF[j].chargeThE>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TsF=min(TpincementF,ensFluxF[j].Ts)
                    TeF=TsF-ensFluxF[j].chargeThE/ensFluxF[j].CP
                    print("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThE,3))+" kW - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3)))		
                    Reseau.append("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThE,3))+" kW - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3)))
                    ssFluxF=ssFlux.ssFlux(TeF,TsF,ensFluxF[j].CP*1000,ensFluxF[j].debVol,ensFluxF[j].rho,ensFluxF[j].mu,ensFluxF[j].lamb,ensFluxF[j].press,ensFluxFinit[j],ensFluxF[j].type,False,True,ensFluxF[j].chargeThE)
                    ensFluxF[j].listeSsFlux.append(ssFluxF)
                    listeUtilite.append(utilite.utilite(ssFluxF,ensFluxF[j].chargeThE,"c",TeF,TsF))
                    puissUC+=ensFluxF[j].chargeThE						

            surconsoC=round(puissUF-deltaH[int(len(deltaH)-1)],10)#on fait un arrondi car sinon même quand le MER est atteint (pas d'utilité chaude), à cause des erreurs de calcul, la différence entre les deux donne une valeur supérieure à 0 (de l'ordre de 10^(-11))
            if surconsoC>0:
                print("L'utilité froide totale: "+str(round(puissUF,1))+" kW, soit: "+str(round(surconsoC,3))+" kW ou " +str(round(surconsoC*100/max(deltaH[int(len(deltaH)-1)],1),2))+" % de plus que le MER")
                Reseau.append("L'utilité froide totale: "+str(round(puissUF,1))+" kW, soit: "+str(round(surconsoC,3))+" kW ou " +str(round(surconsoC*100/max(deltaH[int(len(deltaH)-1)],1),2))+" % de plus que le MER")
            else:
                if puissUC==0:
                    print("Le MER en-dessous du pincement atteint ("+str(round(deltaH[int(len(deltaH)-1)],1))+" kW)")
                    Reseau.append("Le MER en-dessous du pincement atteint ("+str(round(deltaH[int(len(deltaH)-1)],1))+" kW)")
            if puissUC>0:
                print("L'utilité chaude totale: "+str(round(puissUC,1))+" kW")
                Reseau.append("L'utilité chaude totale: "+str(round(puissUC,1))+" kW")
        else:
            for i in range(len(ensFluxC)):#Calcul puissance utilité froide				
                if ensFluxC[i].chargeThE>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TeC=min(TpincementC,ensFluxC[i].Te)
                    TsC=TeC-ensFluxC[i].chargeThE/ensFluxC[i].CP
                    if ensFluxC[i].process==True:
                        print("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3)))		
                        Reseau.append("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3)))
                    ssFluxC=ssFlux.ssFlux(TeC,TsC,ensFluxC[i].CP*1000,ensFluxC[i].debVol,ensFluxC[i].rho,ensFluxC[i].mu,ensFluxC[i].lamb,ensFluxC[i].press,ensFluxCinit[i],ensFluxC[i].type,False,True,ensFluxC[i].chargeThE)
                    ensFluxC[i].listeSsFlux.append(ssFluxC)
                    listeUtilite.append(utilite.utilite(ssFluxC,ensFluxC[i].chargeThE,"f",TeC,TsC))
                    puissUF+=ensFluxC[i].chargeThE
            for j in range(len(ensFluxF)):#Calcul puissance utilité chaude				
                if ensFluxF[j].chargeThE>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TsF=min(TpincementF,ensFluxF[j].Ts)
                    TeF=TsF-ensFluxF[j].chargeThE/ensFluxF[j].CP
                    print("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThE,3))+" kW - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3)))		
                    Reseau.append("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThE,3))+" kW - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3)))
                    ssFluxF=ssFlux.ssFlux(TeF,TsF,ensFluxF[j].CP*1000,ensFluxF[j].debVol,ensFluxF[j].rho,ensFluxF[j].mu,ensFluxF[j].lamb,ensFluxF[j].press,ensFluxFinit[j],ensFluxF[j].type,False,True,ensFluxF[j].chargeThE)
                    ensFluxF[j].listeSsFlux.append(ssFluxF)
                    listeUtilite.append(utilite.utilite(ssFluxF,ensFluxF[j].chargeThE,"c",TeF,TsF))
                    puissUC+=ensFluxF[j].chargeThE						

            surconsoC=round(puissUF-MerDessousTab[r],10)#on fait un arrondi car sinon même quand le MER est atteint (pas d'utilité chaude), à cause des erreurs de calcul, la différence entre les deux donne une valeur supérieure à 0 (de l'ordre de 10^(-11))
            if surconsoC>0:
                print("L'utilité froide totale: "+str(round(puissUF,1))+" kW, soit: "+str(round(surconsoC,3))+" kW ou " +str(round(surconsoC*100/max(MerDessousTab[r],1),2))+" % de plus que le MER")
                Reseau.append("L'utilité froide totale: "+str(round(puissUF,1))+" kW, soit: "+str(round(surconsoC,3))+" kW ou " +str(round(surconsoC*100/max(MerDessousTab[r],1),2))+" % de plus que le MER")
            else:
                if puissUC==0:
                    print("Le MER en-dessous du pincement atteint ("+str(round(MerDessousTab[r],1))+" kW)")
                    Reseau.append("Le MER en-dessous du pincement atteint ("+str(round(MerDessousTab[r],1))+" kW)")
            if puissUC>0:
                print("L'utilité chaude totale: "+str(round(puissUC,1))+" kW")
                Reseau.append("L'utilité chaude totale: "+str(round(puissUC,1))+" kW")




        return(surconsoC,Reseau)


    else:#Dans ce cas on a uniquement des flux chauds ou uniquement des flux froids
        
        if MerDessousTab==[]:#Dans ce cas on est en continu
            for i in range(len(ensFluxC)):#Calcul puissance utilité froide				
                if ensFluxC[i].chargeThE>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TeC=min(TpincementC,ensFluxC[i].Te)
                    TsC=TeC-ensFluxC[i].chargeThE/ensFluxC[i].CP
                    if ensFluxC[i].process==True:
                        print("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3)))		
                        Reseau.append("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3)))
                    ssFluxC=ssFlux.ssFlux(TeC,TsC,ensFluxC[i].CP*1000,ensFluxC[i].debVol,ensFluxC[i].rho,ensFluxC[i].mu,ensFluxC[i].lamb,ensFluxC[i].press,ensFluxCinit[i],ensFluxC[i].type,False,True,ensFluxC[i].chargeThE)
                    ensFluxC[i].listeSsFlux.append(ssFluxC)
                    listeUtilite.append(utilite.utilite(ssFluxC,ensFluxC[i].chargeThE,"f",TeC,TsC))
                    puissUF+=ensFluxC[i].chargeThE
            for j in range(len(ensFluxF)):#Calcul puissance utilité chaude				
                if ensFluxF[j].chargeThE>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TsF=min(TpincementF,ensFluxF[j].Ts)
                    TeF=TsF-ensFluxF[j].chargeThE/ensFluxF[j].CP
                    print("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThE,3))+" kW - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3)))		
                    Reseau.append("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThE,3))+" kW - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3)))
                    ssFluxF=ssFlux.ssFlux(TeF,TsF,ensFluxF[j].CP*1000,ensFluxF[j].debVol,ensFluxF[j].rho,ensFluxF[j].mu,ensFluxF[j].lamb,ensFluxF[j].press,ensFluxFinit[j],ensFluxF[j].type,False,True,ensFluxF[j].chargeThE)
                    ensFluxF[j].listeSsFlux.append(ssFluxF)
                    listeUtilite.append(utilite.utilite(ssFluxF,ensFluxF[j].chargeThE,"c",TeF,TsF))
                    puissUC+=ensFluxF[j].chargeThE						

            surconsoC=0
            print("Le MER en-dessous du pincement atteint ("+str(round(deltaH[int(len(deltaH)-1)],1))+" kW)")
            Reseau.append("Le MER en-dessous du pincement atteint ("+str(round(deltaH[int(len(deltaH)-1)],1))+" kW)")
        else:
            for i in range(len(ensFluxC)):#Calcul puissance utilité froide				
                if ensFluxC[i].chargeThE>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TeC=min(TpincementC,ensFluxC[i].Te)
                    TsC=TeC-ensFluxC[i].chargeThE/ensFluxC[i].CP
                    if ensFluxC[i].process==True:
                        print("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3)))		
                        Reseau.append("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThE,3))+" kW - TeC/TsC : "+str(round(TeC,3))+"/"+str(round(TsC,3)))
                    ssFluxC=ssFlux.ssFlux(TeC,TsC,ensFluxC[i].CP*1000,ensFluxC[i].debVol,ensFluxC[i].rho,ensFluxC[i].mu,ensFluxC[i].lamb,ensFluxC[i].press,ensFluxCinit[i],ensFluxC[i].type,False,True,ensFluxC[i].chargeThE)
                    ensFluxC[i].listeSsFlux.append(ssFluxC)
                    listeUtilite.append(utilite.utilite(ssFluxC,ensFluxC[i].chargeThE,"f",TeC,TsC))
                    puissUF+=ensFluxC[i].chargeThE
            for j in range(len(ensFluxF)):#Calcul puissance utilité chaude				
                if ensFluxF[j].chargeThE>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TsF=min(TpincementF,ensFluxF[j].Ts)
                    TeF=TsF-ensFluxF[j].chargeThE/ensFluxF[j].CP
                    print("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThE,3))+" kW - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3)))		
                    Reseau.append("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThE,3))+" kW - TeF/TsF : "+str(round(TeF,3))+"/"+str(round(TsF,3)))
                    ssFluxF=ssFlux.ssFlux(TeF,TsF,ensFluxF[j].CP*1000,ensFluxF[j].debVol,ensFluxF[j].rho,ensFluxF[j].mu,ensFluxF[j].lamb,ensFluxF[j].press,ensFluxFinit[j],ensFluxF[j].type,False,True,ensFluxF[j].chargeThE)
                    ensFluxF[j].listeSsFlux.append(ssFluxF)
                    listeUtilite.append(utilite.utilite(ssFluxF,ensFluxF[j].chargeThE,"c",TeF,TsF))
                    puissUC+=ensFluxF[j].chargeThE						

            surconsoC=0
            print("Le MER en-dessous du pincement atteint ("+str(round(max(puissUC,puissUF),1))+" kWh)")#max(puissUC,puissUF) : car un des deux sera nul
            Reseau.append("Le MER en-dessous du pincement atteint ("+str(round(max(puissUC,puissUF),1))+" kWh)")#max(puissUC,puissUF) : car un des deux sera nul





        return(surconsoC,Reseau)