# -*- coding: utf-8 -*-
"""

Created on mai 27  

@author: p-aToussaint
"""
import matplotlib.pyplot as plt
from operator import itemgetter, attrgetter
import copy
import pickle
import time

from creation_reseau_statique import MERContinue1,Division,Fct
from donnees import Donnees
from classes import Flux ,reseau,kpi,ssFlux,utilite


def reseauUp(ensFluxF,ensFluxC,TpincementF,TpincementC,deltaTmin,listeCouple,listeUtilite,listeSsFlux,deltaH,MerDessusTab,k):

    #on créé des nouvelles liste qu'on ne modifiera pas, cela permettra d'avoir accès aux températures d'entrée/sortie dans flux (car elles sont modifiés pour les listes ensFluxC/F)
    ensFluxFinit=copy.deepcopy(ensFluxF)
    ensFluxCinit=copy.deepcopy(ensFluxC)  

    # print("ENSFLUXC CCCCCCCCCCCCCCCCCCCCC", (flux.numero for flux in ensFluxC))
    # print("ENSFLUXF FFFFFFFFFFFFFFFFFFFFF", (flux.numero for flux in ensFluxF))

    ########## Liste des échangeurs que l'on souhaite avoir ##########
    #La liste est une liste de tuples de la forme (numfluxchaud, numfluxfroid)
    Liste_echangeur = [(5,5), (4,3), (4,4), (5,6), (1,1), (1,2)]
    print("Liste des échangeurs que l'on souhaite : ", Liste_echangeur)
    print("On souhaite donc ", len(Liste_echangeur), " échangeurs")

    Reseau1=[]
    puissE=0#puissance de l'échange de chaleur
    puissE1=0#puissance de l'échange de chaleur d'une boucle de la division
    puissE2=0#puissance de l'échange de chaleur d'une boucle de la division
    puissUC=0#puissance de l'utilité chaude
    puissUF=0#puissance de l'utilité chaude
    TeC=0#Température d'entrée du fluide chaud
    Tef=0#Température d'entrée du fluide froid
    TsC=0#Température de sortie du fluide chaud
    Tsf=0#Température de sortie du fluide froid
    if len(ensFluxF)!=0 and len(ensFluxC)!=0:#car sinon aucun échange ne peut avoir lieu, dans ce cas, on ne se servira que des utilités 
        #Respect de la règle sur le nombre de flux
        CP=[]
        longC=len(ensFluxC)
        longF=len(ensFluxF)
        for j in range(len(ensFluxF)):#on divise le fluide chaud qui a le plus grand CP pour que la condition sur les CP soit conservé
            CP.append(ensFluxF[j].CP)
        if longF<longC:#on vérifie la condition sur le nombre de flux et indique à l'utilisateur que le flux doit être divisé en deux
            while longF<longC:
                ind=CP.index(max(CP))
                print("Le fluide froid f"+str(ensFluxF[ind].numero)+" doit être divisé en deux.")
                # print("OOOOOOOOOOOOOOOOOOOO", ensFluxF[ind].numero, "OOOOOOOOOOOOOOOOOOOO")
                CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2. Car il n'est pas encore possible de connaître la valeur de son CP sur chaque branche.
                if ensFluxF[ind].div==0:
                    ensFluxF[ind].div+=1 #on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                else:
                    ensFluxF[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                longF+=1

        newTe=[]
        for i in range(len(ensFluxC)):
            ensFluxC[i].newTe=ensFluxC[i].Te
            ensFluxC[i].newTeNum=-1#pour ne pas lui attribuer un numero de flux
            newTe.append(copy.deepcopy(ensFluxC[i].Te))


        
        
        #Etablissement du réseau
        for i in range(len(ensFluxC)):#détermination des couples et de leurs puissances
            ech=0#détermine si le fluide a pu échanger de la chaleur avec un autre fluide
            imp=0#indique si l'échange avec un fluide est possible (par rapport aux Te et le deltaTmin)
            impCP=0#indique si l'échange avec un fluide est possible (par rapport à la règle des CP)
            div=[]
            # print()
            print("--------------------"+"ensFluxC[i].nom : "+str(ensFluxC[i].nom))
            print("--------------------"+'ensFluxC[i].numero : ' + str(ensFluxC[i].numero))
            # if ensFluxC[i].numero==5:
            #     time.sleep(2000)
            # print()
            for j in range(len(ensFluxF)):
                div.append(ensFluxF[j].div)
            for j in range(len(ensFluxF)):
                annul="non"
                # possible = (ensFluxC[i].numero, ensFluxF[j].numero)
                # if possible in Liste_echangeur :
                if ensFluxC[i].numero==5:
                    print("----------"+"ensFluxF[j].nom : "+str(ensFluxF[j].nom))
                    print("----------"+"ensFluxF[j].numero : "+str(ensFluxF[j].numero))
                # print(ensFluxC[i].Te)
                # print(ensFluxF[j].Te)
                # print()


                if ensFluxC[i].Te<=ensFluxF[j].Te+deltaTmin or ensFluxF[j].chargeThA==0:
                    imp+=1
                    # print(ensFluxC[i].Te)
                    # print(ensFluxF[j].Te)
                    # print(ensFluxF[j].chargeThA)
                    print("impossible")

                if ensFluxC[i].CP<=ensFluxF[j].CP or ensFluxC[i].Ts>TpincementC:#Soit le fluide atteint la température de pincement et la condition sur les CP doit être respectée. Soit le fluide n'atteint pas la température de pincement et la condition des CP n'a pas besoin d'être respectée. 
                    # print("stop1")
                    if ensFluxF[j].chargeThA!=0 and ensFluxC[i].chargeThA>10**(-10) and ensFluxC[i].Te>ensFluxF[j].Te+deltaTmin:#on vérifie que les deux fluides ne sont pas déjà satisfait énergétiquement
                        puissE=min(ensFluxC[i].chargeThA,ensFluxF[j].chargeThA)#calcule la puissance échangée 
                        # print("puissE : "+str(puissE))
                        if ensFluxF[j].div==0:
                            CPbrF=ensFluxF[j].CP
                        else:#nous devons d'abord déterminer avec quel flux le flux divisé va échanger pour connaitre quel sera le dénominateur de CPbrF
                            if ensFluxF[j].ech=="non":#si le fluide divisé a déjà échangé, son b a déjà été calculé
                                ensFluxF[j].b,annul,annuldiv,m,test,CP1=Division.divA(ensFluxC,ensFluxF,i,j,TpincementC,TpincementF,deltaTmin,ech,CP,"echA",Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)
                                # print("Sortie divA")
                                CP=CP1
                                if ensFluxF[j].puissModif=="oui":#lorsque la puissance échangée a été modifié dans la fct divE car on a échangé moins que la charge thermique minimale des deux flux
                                    puissE=ensFluxF[j].b
                                if annul=="non" and annuldiv!="oui":
                                    if ensFluxF[j].div>0:#car sinon cela veut dire qu'on a annulé toutes ses branches
                                        CP[j]=0#permet de ne pas diviser un flux tant que toutes ses branches n'ont pas fini d'avoir échangé (sinon problème au niveau des .div)
                                if annuldiv=="oui":
                                    CPdiv=CP[j]
                                    CP[j]=0
                                    CPcompt=0
                                    div=[]
                                    CPdiv1=[]
                                    CPdiv1=copy.deepcopy(CP)
                                    for h in range(len(ensFluxF)):
                                        div.append(ensFluxF[h].div)
                                    while ensFluxF[j].div!=0:
                                        verif=0
                                        for h in range(len(CP)):
                                            verif+=CP[h]
                                        if verif==0:#si verif=0 alors tous les flux sont déjà satisfaits
                                            print("1Tous les flux sont satisfaits. Division d'un flux froid impossible")
                                            for h in range(len(ensFluxF)):
                                                ensFluxF[h].div=div[h]
                                            CP=CPdiv1
                                            break
                                        if ensFluxF[j].div==1:
                                            ensFluxF[j].div=0
                                        else:
                                            ensFluxF[j].div-=0.5
                                        CPcompt+=1
                                        print("On annule la division du flux f"+str(ensFluxF[j].numero))#car une des branches des flux échanges toutes sa chaleur
                                        longF-=1
                                        ind=CP.index(max(CP))
                                        print("1Le fluide froid f"+str(ensFluxF[ind].numero)+" doit être divisé en deux.")
                                        CP[ind]=CP[ind]/2
                                        if ensFluxC[ind].div==0:
                                            ensFluxC[ind].div+=1
                                        else:
                                            ensFluxC[ind].div+=0.5
                                        longF+=1
                                    CP[j]=CPdiv*2**CPcompt
                                    CPbrF=ensFluxF[j].CP	
                                else:
                                    CPbrF=puissE*ensFluxF[j].CP/ensFluxF[j].b
                            else:
                                CPbrF=puissE*ensFluxF[j].CP/ensFluxF[j].b
                            if ensFluxF[j].verif!=0 and annul!="oui" and ((ensFluxF[j].div!=0 and ensFluxC[i].numero in ensFluxF[j].test) or ensFluxF[j].div==0):#on modifie b1 que si le flux va échanger avec le flux chaud en question et si son verif!=0
                                if ensFluxC[i].chargeThA1==0:
                                    puiss=min((ensFluxF[j].b-ensFluxF[j].b1),ensFluxC[i].chargeThA,(min(ensFluxC[i].Te,ensFluxC[i].Te)-max((max(ensFluxF[j].Te,TpincementF)+deltaTmin),ensFluxC[i].Ts))*ensFluxC[i].CP)
                                else:
                                    puiss=min((ensFluxF[j].b-ensFluxF[j].b1),ensFluxC[i].chargeThA1)
                                puissE=puiss
                                ensFluxF[j].b1+=puiss
                                if ensFluxF[j].b1==ensFluxF[j].b:#car s'il s'agit de la dernière branche alors elle va compléter le b. Et on doit garder la valeur de b1 tel quel calculé la valeeur du dernier échange de la branche du flux divisé dans la fct ech
                                    ensFluxF[j].b1-=puiss
                                CPbrF=puiss*ensFluxF[j].CP/ensFluxF[j].b
                        print(CPbrF)
                        print("ensFluxF[j].nom : "+str(ensFluxF[j].nom))
                        print("ensFluxF[j].Te : "+str(ensFluxF[j].Te))
                        print("ensFluxC[i].Te : "+str(ensFluxC[i].Te))
                        if annul!="oui" and ((ensFluxF[j].div!=0 and ensFluxC[i].numero in ensFluxF[j].test) or ensFluxF[j].div==0) and puissE!=0:
                            # possible = (ensFluxC[i].numero, ensFluxF[j].numero)
                            # if possible in Liste_echangeur :
                                # print("OOOOOOOOOOOOOOOOOOOO", ensFluxC[i].numero, ensFluxF[j].numero, "OOOOOOOOOOOOOOOOOOOO")
                            bclDiv="non"
                            ech,CP=Fct.echA(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,i,j,CPbrF,ech,CP,bclDiv,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)
                else:
                    impCP+=1
                    print("ech non possible car ensFluxC[i].CP>ensFluxF[j].CP")

            if (ech==0 or impCP>=2)  and imp<len(ensFluxF)-1  and ensFluxC[i].chargeThA>10**(-10) and ensFluxC[i].Ts<TpincementC:#  #si impCP>=2 alors on aura assez de flux pour échanger avec 2 branches donc on peut diviser le flux chaud pour finir d'échanger sa chaleur #car si la règle des CP n'est pas respectée pour #or ensFluxC[i].chargeThA>0) #Si le fluide n'a pas pu échanger avec aucun flux mais que sa Te lui permet d'échanger de la chaleur avec au moins deux flux (d'où le len(ensFluxF)-1), alors son CP est trop grand : on va le diviser. On vérifie aussi qu'il atteint la T de pincement car sinon il n'a pas besoin de respecter la règle du CP
                # print("Entrée ech==0")
                # print("CP :"+str(CP))
                CPbrF=0#CP de chaque branche du flux froid divisé
                CPbrC=0#CP de chaque branche du flux chaud divisé
                annul="oui"
                div=[]
                CPdiv1=[]
                CPdiv1=copy.deepcopy(CP)
                #ensFluxC[i].b2=0
                chargeThAch=copy.deepcopy(ensFluxC[i].chargeThA)#car celle-ci est modifié dans la boucle divE1
                #ensFluxF1=copy.deepcopy(ensFluxF)
                ensFluxF[j].echChargeTh="oui"
                for h in range(len(ensFluxF)):#on sauvegarde la valeur des div avant division
                    div.append(copy.deepcopy(ensFluxF[h].div))
                while annul!="non":
                    #ensFluxF[j].b2+=1
                    verif=0
                    for h in range(len(CP)):
                        verif+=CP[h]
                    if verif<0.01:#Car sinon on aura une boucle infini car les flux chauds seront divisés jusqu'à ce que la boucle while soit satisfaite
                        print("2Tous les flux sont satisfaits. Division d'un flux chaud impossible")
                        for h in range(len(ensFluxF)):#comme l'échange n'est pas possible malgré les division, on annule les divisions en rétablissant les div
                            ensFluxF[h].div=div[h]
                        CP=CPdiv1
                        verif=0#car on teste la valeur de verif par la suite par rapport à 0. On considère dans ce cas que verif=0
                        break#permet de stopper la boucle while annul!="non"
                    print("Le fluide chaud c"+str(ensFluxC[i].numero)+" doit être divisé en deux.")
                    if ensFluxC[i].div==0:
                        ensFluxC[i].div+=1
                    else:
                        ensFluxC[i].div+=0.5
                    longC+=1
                    while longC>longF:#on vérifie à nouveau la condition sur le nombre de flux et indique à l'utilisateur que le flux doit être divisé en deux. On divise le fluide chaud qui a le plus grand CP pour que la condition sur les CP soit conservé. Jsuqu'à ce que le nombre de flux froids soit inférieur au nombre de flux chauds.
                        ind=CP.index(max(CP))
                        print("Le fluide froid f"+str(ensFluxF[ind].numero)+" doit être divisé en deux.")
                        CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                        if ensFluxF[ind].div==0:
                            ensFluxF[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                        else:
                            ensFluxF[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                        longF+=1
                    print("Entrée DivA1")
                    ensFluxC[i].b,annul=Division.divA1(ensFluxC,ensFluxF,i,TpincementC,TpincementF,deltaTmin,CP,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)#le but est de simuler les prochains échanges avec le flux froid divisé pour connaître la valeur de son b. 
                    print("Sortie DivA1")
                ensFluxC[i].chargeThA=chargeThAch
                div=[]
                for h in range(len(ensFluxF)):#on sauvegarde la valeur des div avant division
                    div.append(ensFluxF[h].div)
                print("div :"+str(div))
                print("CP :"+str(CP))
                
                if verif<0.01:#alors on va autoriser d'échanger moins que la charge Th du flux chaud (ensFluxC[i].echChargeTh="non")
                    print("")
                    print("On va échanger moins que la charge Th du fluide froid")
                    chargeThAch=copy.deepcopy(ensFluxC[i].chargeThA)#car celle-ci est modifié dans la boucle divE1
                    CP=CPdiv1
                    #ensFluxF=copy.deepcopy(ensFluxF1)
                    ensFluxC[i].echChargeTh="non"
                    annul="oui"
                    ensFluxC[i].div=0
                    print("ensFluxC[i].div : "+str(ensFluxC[i].div))
                    print("ensFluxC[i].test : "+str(ensFluxC[i].test))
                    while annul!="non":
                        verif=0
                        for h in range(len(CP)):
                            verif+=CP[h]
                        if verif<0.01:#Car sinon on aura une boucle infini car les flux chauds seront divisés jusqu'à ce que la boucle while soit satisfaite
                            print("2Tous les flux sont satisfaits. Division d'un flux chaud impossible")
                            for h in range(len(ensFluxF)):#comme l'échange n'est pas possible malgré les division, on annule les divisions en rétablissant les div
                                ensFluxF[h].div=div[h]
                            CP=CPdiv1
                            verif=0#car on teste la valeur de verif par la suite par rapport à 0. On considère dans ce cas que verif=0
                            break#permet de stopper la boucle while annul!="non"
                        print("Le fluide chaud c"+str(ensFluxC[i].numero)+" doit être divisé en deux.")
                        if ensFluxC[i].div==0:
                            ensFluxC[i].div+=1
                        else:
                            ensFluxC[i].div+=0.5
                        longC+=1
                        while longC>longF:#on vérifie à nouveau la condition sur le nombre de flux et indique à l'utilisateur que le flux doit être divisé en deux. On divise le fluide chaud qui a le plus grand CP pour que la condition sur les CP soit conservé. Jsuqu'à ce que le nombre de flux froids soit inférieur au nombre de flux chauds.
                            ind=CP.index(max(CP))
                            print("Le fluide froid f"+str(ensFluxF[ind].numero)+" doit être divisé en deux.")
                            CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                            if ensFluxF[ind].div==0:
                                ensFluxF[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                            else:
                                ensFluxF[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                            longF+=1
                        print("Entrée DivA1")
                        ensFluxC[i].b,annul=Division.divA1(ensFluxC,ensFluxF,i,TpincementC,TpincementF,deltaTmin,CP,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)#le but est de simuler les prochains échanges avec le flux froid divisé pour connaître la valeur de son b. 
                        print("Sortie DivA1")
                    ensFluxC[i].chargeThA=chargeThAch

                # possible = (ensFluxC[], ensFluxF[])
                if verif!=0 :#boucle qui réalise l'échange entre les flux. On y entre que si des flux on était trouvé pour échanger avec le flux chaud (cad que verif>0)
                    print("entrée dernier paraph")
                    ancienCP=0
                    ptCP=0.95 #pour éviter l'égalité des CP
                    for k in range(len(ensFluxF)):
                        annul1="non"
                        ensFluxF[k].verif=0
                        if ensFluxF[k].chargeThA!=0 and ensFluxC[i].chargeThA!=0:#si les fluides ne sont pas satisfait et le fluide chaud possède encore des branches non utilisées (on considère un échange par branche)
                            puissA1=ensFluxF[k].CP*ptCP*(ensFluxC[i].Te-max(TpincementC,ensFluxC[i].Ts))#on égalise le CP du flux chaud et froid pour que l'échange soit possible
                            puissE=min(ensFluxF[k].chargeThA,ensFluxC[i].chargeThA,puissA1)
                            if ensFluxF[k].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                                CPbrF=ensFluxF[k].CP
                            else:#sinon on pondère le CP avec la puissance du flux complémentaire du couple
                                if ensFluxF[k].ech=="non":
                                    ensFluxF[k].b,annul1,annuldiv,m,test,CP=Division.divA(ensFluxC,ensFluxF,i,k,TpincementC,TpincementF,deltaTmin,ech,CP,"echA1",Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)#le but est de simuler les prochains échanges avec le flux chaud divisé pour connaître la valeur de son b ; echE est correct
                                    CPdiv=CP[k]#on ne va pas diviser le flux actuel alors qu'on cherche à annuler sa division
                                    CPdiv1=[]
                                    CPdiv1=copy.deepcopy(CP)
                                    if annul=="non":
                                        if ensFluxF[k].div>0:
                                            CP[k]=0#permet de ne pas diviser un flux dont toutes ses branches n'ont pas fini d'avoir échangé (sinon problème au niveau des .div)
                                    if annuldiv=="oui":
                                        CP[k]=0
                                        CPcompt=0
                                        div=[]
                                        for h in range(len(ensFluxF)):#on sauvegarde la valeur des div avant division
                                            div.append(ensFluxF[h].div)
                                        while ensFluxF[k].div!=0:
                                            for h in range(len(CP)):
                                                verif+=CP[h]
                                            if verif==0:#si verif=0 alors tous les flux sont déjà satisfaits
                                                print("3Tous les flux sont satisfaits. Division d'un flux chaud impossible")
                                                for h in range(len(ensFluxF)):
                                                    ensFluxF[h].div=div[h]
                                                CP=CPdiv1
                                                break#permet de stopper la boucle while annul!="non"
                                            CPcompt+=1
                                            if ensFluxF[k].div==1:
                                                ensFluxF[k].div=0
                                            else:
                                                ensFluxF[k].div-=0.5
                                            print("On annule la division du flux f"+str(ensFluxF[k].numero))#car une des branches des flux échange toute sa chaleur
                                            #division d'un nouveau flux pour toujours respecter la règle des flux
                                            ind=CP.index(max(CP))
                                            print("Le fluide froid f"+str(ensFluxF[ind].numero)+" doit être divisé en deux.")
                                            CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                                            if ensFluxF[ind].div==0:
                                                ensFluxF[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                                            else:
                                                ensFluxF[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                                        CP[k]=CPdiv*2**CPcompt#on lui réattribue sa valeur moins les branches retirées (annulées)
                                        CPbrF=ensFluxF[k].CP
                                    else:
                                        if ensFluxF[k].plusEch=="non":
                                            CPbrF=ensFluxF[k].CP
                                        else:
                                            CPbrF=puissE*ensFluxF[k].CP/ensFluxF[k].b
                                else:
                                    CPbrF=puissE*ensFluxF[k].CP/ensFluxF[k].b
                                if ((ensFluxF[k].verif!=0 and annul1=="non")) and ((ensFluxF[k].div!=0 and ensFluxC[i].numero in ensFluxF[k].test) or ensFluxF[k].div==0):#on modifie b1 que si le flux va échanger avec le flux froid en question et si son verif!=0
                                    print("verif")
                                    puissE=min((ensFluxF[k].b-ensFluxF[k].b1),ensFluxC[i].chargeThA)
                                    ensFluxF[k].b1+=puissE
                                    CPbrF=puissE*ensFluxF[k].CP/ensFluxF[k].b
                            

                            if ensFluxC[i].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                                CPbrC=ensFluxC[i].CP
                            else:#sinon on pondère le CP avec la puissance du flux complémentaire
                                """if ensFluxF[j].ech=="non":
                                    ensFluxF[j].b,annul=Division.divE1(ensFluxC,ensFluxF,j,TpincementC,TpincementF,deltaTmin)#le but est de simuler les prochains échanges avec le flux froid divisé pour connaître la valeur de son b. 
                                """
                                # print(ensFluxF[j].b)
                                # print(ensFluxF[j].CP)
                                # print(ensFluxF[j].div)
                                # print(puissE)
                                if ensFluxC[i].echChargeTh=="non" and annul1=="non" and ensFluxF[k].numero in ensFluxC[i].test and ((ensFluxF[k].div!=0 and ensFluxC[i].numero in ensFluxF[k].test) or ensFluxF[k].div==0) and puissE!=0:#on mets toutes ces conditions pour que ancienCP soit modifié que si l'échange aura lieu
                                    print("ancienCP : "+str(ancienCP))
                                    if ensFluxC[i].div!=0.5:#permet de savoir s'il sagit de la dernière branche ou pas
                                        CPbrC=ensFluxF[k].CP*ptCP
                                        ancienCP+=CPbrC#permettra de connaître la valeur des autres branches lors de l'échange avec la dernière branche
                                    else:
                                        print("ensFluxC[i].CP : "+str(ensFluxC[i].CP))
                                        CPbrC=ensFluxC[i].CP-ancienCP
                                else:
                                    CPbrC=puissE*ensFluxC[i].CP/ensFluxC[i].b
                            if ensFluxC[i].echChargeTh=="non" and ensFluxF[k].numero in ensFluxC[i].test and ((ensFluxF[k].div!=0 and ensFluxC[i].numero in ensFluxF[k].test) or ensFluxF[k].div==0):#on modifie b1 que si le flux va échanger avec le flux froid en question et si son verif!=0
                                print("ensFluxC[i].tempMax :"+str(ensFluxC[i].tempMax))
                                print("(ensFluxC[i].Te-ensFluxC[i].tempMax)*CPbrC : "+str((ensFluxC[i].Te-ensFluxC[i].tempMax)*CPbrC))
                                print("(ensFluxC[i].b-ensFluxC[i].b1) :"+str((ensFluxC[i].b-ensFluxC[i].b1)))
                                print("b :"+str(ensFluxC[i].b))
                                print("b1 :"+str(ensFluxC[i].b1))
                                puissE=min((ensFluxC[i].Te-ensFluxC[i].tempMax)*CPbrC,(ensFluxC[i].b-ensFluxC[i].b1))
                                ensFluxC[i].b1+=puissE

                            """if ensFluxC[i].numero==2:
                                print(ensFluxF[j].numero)
                                print(ensFluxC[k].numero)
                                print(CPbrC)
                                print(CPbrF)
                                print(ensFluxC[k].div)
                                print(puissE)
                                print(ensFluxC[k].test)"""
                            print("puissE : "+str(puissE))
                            if annul1=="non" and ensFluxF[k].numero in ensFluxC[i].test and ((ensFluxF[k].div!=0 and ensFluxC[i].numero in ensFluxF[k].test) or ensFluxF[k].div==0) and puissE!=0:#si un des deux flux ne peut pas échanger, alors on ne fait pas l'échange. Le test permet de vérifier que le b du flux chaud divisé a été calculé pour échanger avec ce flux froid (sinon erreur). Si le flux n'est pas divisé cela n'a pas besoin d'être vérifié
                                # possible1 = (ensFluxC[i].numero, ensFluxF[j].numero)
                                # if possible1 in Liste_echangeur :
                                    # print("OOOOOOOOOOOOOOOOOOOO", ensFluxC[i].numero, ensFluxF[j].numero, "OOOOOOOOOOOOOOOOOOOO")
                                print("échange a lieu ")
                                print("ensFluxF[k].nom :"+str(ensFluxF[k].nom))
                                bclDiv="non"
                                ech,CP=Fct.echA1(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,i,k,CPbrF,CPbrC,ech,bclDiv,CP,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)
                            if ensFluxF[k].chargeThA==0:
                                CP[k]=0#cela permet de ne pas diviser à nouveau un flux chaud
        

        """
        for i in range(len(ensFluxC)):#Si la condition sur les CP est déjà respectée avec un autre flux
            for j in range(len(ensFluxF)): 
                if ensFluxF[j].chargeThA!=0 and ensFluxC[i].chargeThA!=0 and ensFluxC[i].pinc=="oui": #si le fluide chaud atteint déjà la température du pincement grâce à un échange, la règle des CP peut ne pas être respectée
                    puissE=min(ensFluxC[i].chargeThA,ensFluxF[j].chargeThA)
                    if ensFluxF[j].div==0:
                        CPbrF=ensFluxF[j].CP
                    else:#nous devons d'abord déterminer avec quel flux le flud divisé froid va échanger pour connaitre quel sera le dénominateur de CPbrF
                        if ensFluxF[j].ech=="non":
                            ensFluxF[j].b=Division.divA(ensFluxC,ensFluxF,i,j,TpincementC,TpincementF,deltaTmin,ech,CP,echA1,Reseau)
                        CPbrF=puissE*ensFluxF[j].CP/ensFluxF[j].b
                    if ensFluxC[i].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                            CPbrC=ensFluxC[i].CP
                    else:#nous devons d'abord déterminer avec quel flux le flud divisé froid va échanger pour connaitre quel sera le dénominateur de CPbrF
                        if ensFluxC[i].ech=="non":#si le fluide divisé a déjà échangé, la valeur de son b est déjà connu. Il n'est donc pas nécessaire de la recalculer. Si celui-ci n'atteint pas la T du pincementC, la condition des CP n'est pas nécessaire.
                            ensFluxC[i].b,annul=Division.divA1(ensFluxC,ensFluxF,i,TpincementC,TpincementF,deltaTmin,CP,Reseau1)
                        CPbrC=puissE*ensFluxC[i].CP/ensFluxC[i].b
                    if annul!="oui":
                        Fct.echA2(TpincementC,TpincementF,ensFluxC,ensFluxF,deltaTmin,puissE,i,j,CPbrF,CPbrC,ech,CP,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)"""

        if MerDessusTab==[]:#Dans ce cas on est en continu
            for j in range(len(ensFluxF)):#Calcul puissance utilité chaude	
                print(ensFluxF[j].numero)	
                print(ensFluxF[j].chargeThA)			
                if ensFluxF[j].chargeThA>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TeF=max(TpincementF,ensFluxF[j].Te)
                    TsF=TeF+ensFluxF[j].chargeThA/ensFluxF[j].CP
                    print("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThA,1))+" kW - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1)))	
                    Reseau1.append("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThA,1))+" kW - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1)))
                    ssFluxF=ssFlux.ssFlux(TeF,TsF,ensFluxF[j].CP*1000,ensFluxF[j].debVol,ensFluxF[j].rho,ensFluxF[j].mu,ensFluxF[j].lamb,ensFluxF[j].press,ensFluxFinit[j],ensFluxF[j].type,False,True,ensFluxF[j].chargeThA)
                    ensFluxF[j].listeSsFlux.append(ssFluxF)
                    listeUtilite.append(utilite.utilite(ssFluxF,ensFluxF[j].chargeThA,"c",TeF,TsF))
                    puissUC+=ensFluxF[j].chargeThA
            for i in range(len(ensFluxC)):#Calcul puissance utilité chaude				
                if ensFluxC[i].chargeThA>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TsC=max(TpincementC,ensFluxC[i].Ts)
                    TeC=TsC+ensFluxC[i].chargeThA/ensFluxC[i].CP
                    print("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThA,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1)))		
                    Reseau1.append("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThA,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1)))
                    ssFluxC=ssFlux.ssFlux(TeC,TsC,ensFluxC[i].CP*1000,ensFluxC[i].debVol,ensFluxC[i].rho,ensFluxC[i].mu,ensFluxC[i].lamb,ensFluxC[i].press,ensFluxCinit[i],ensFluxC[i].type,False,True,ensFluxC[i].chargeThA)
                    ensFluxC[i].listeSsFlux.append(ssFluxC)
                    listeUtilite.append(utilite.utilite(ssFluxC,ensFluxC[i].chargeThA,"f",TeC,TsC))
                    puissUF+=ensFluxC[i].chargeThA		

            surconsoF=puissUC-deltaH[0]
            if surconsoF>0:
                print("L'utilité chaude totale: "+str(round(puissUC,1))+" kW, soit: "+str(round(surconsoF,1))+" kW de plus que le MER ou "+str(round(surconsoF*100/deltaH[0],2))+" % de plus que le MER")
                Reseau1.append("L'utilité chaude totale: "+str(round(puissUC,1))+" kW, soit: "+str(round(surconsoF,1))+" kW de plus que le MER ou "+str(round(surconsoF*100/deltaH[0],2))+" % de plus que le MER")
            else:
                if puissUF==0:
                    print("Le MER au-dessus du pincement atteint ("+str(round(deltaH[0],1))+" kW)")
                    Reseau1.append("Le MER au-dessus du pincement atteint ("+str(round(deltaH[0],1))+" kW)")
            if puissUF>0:
                print("L'utilité froide totale: "+str(round(puissUF,1))+" kW")
                Reseau1.append("L'utilité froide totale: "+str(round(puissUF,1))+" kW")
        else:#dans ce cas on est en discontinu
            for j in range(len(ensFluxF)):#Calcul puissance utilité chaude	
                print(ensFluxF[j].numero)	
                print(ensFluxF[j].chargeThA)			
                if ensFluxF[j].chargeThA>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TeF=max(TpincementF,ensFluxF[j].Te)
                    TsF=TeF+ensFluxF[j].chargeThA/ensFluxF[j].CP
                    print("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThA,1))+" kW - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1)))	
                    Reseau1.append("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThA,1))+" kW - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1)))
                    ssFluxF=ssFlux.ssFlux(TeF,TsF,ensFluxF[j].CP*1000,ensFluxF[j].debVol,ensFluxF[j].rho,ensFluxF[j].mu,ensFluxF[j].lamb,ensFluxF[j].press,ensFluxFinit[j],ensFluxF[j].type,False,True,ensFluxF[j].chargeThA)
                    ensFluxF[j].listeSsFlux.append(ssFluxF)
                    listeUtilite.append(utilite.utilite(ssFluxF,ensFluxF[j].chargeThA,"c",TeF,TsF))
                    puissUC+=ensFluxF[j].chargeThA
            for i in range(len(ensFluxC)):#Calcul puissance utilité chaude				
                if ensFluxC[i].chargeThA>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TsC=max(TpincementC,ensFluxC[i].Ts)
                    TeC=TsC+ensFluxC[i].chargeThA/ensFluxC[i].CP
                    print("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThA,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1)))		
                    Reseau1.append("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThA,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1)))
                    ssFluxC=ssFlux.ssFlux(TeC,TsC,ensFluxC[i].CP*1000,ensFluxC[i].debVol,ensFluxC[i].rho,ensFluxC[i].mu,ensFluxC[i].lamb,ensFluxC[i].press,ensFluxCinit[i],ensFluxC[i].type,False,True,ensFluxC[i].chargeThA)
                    ensFluxC[i].listeSsFlux.append(ssFluxC)
                    listeUtilite.append(utilite.utilite(ssFluxC,ensFluxC[i].chargeThA,"f",TeC,TsC))
                    puissUF+=ensFluxC[i].chargeThA		

            print("MerDessusTab[k] :"+str(MerDessusTab[k]))
            surconsoF=puissUC-MerDessusTab[k]
            if surconsoF>0:
                print("L'utilité chaude totale: "+str(round(puissUC,1))+" kW, soit: "+str(round(surconsoF,1))+" kW de plus que le MER ou "+str(round(surconsoF*100/max(MerDessusTab[k],1),2))+" % de plus que le MER")
                Reseau1.append("L'utilité chaude totale: "+str(round(puissUC,1))+" kW, soit: "+str(round(surconsoF,1))+" kW de plus que le MER ou "+str(round(surconsoF*100/max(MerDessusTab[k],1),2))+" % de plus que le MER")
            else:
                if puissUF==0:
                    print("Le MER au-dessus du pincement atteint ("+str(round(MerDessusTab[k],1))+" kW)")
                    Reseau1.append("Le MER au-dessus du pincement atteint ("+str(round(MerDessusTab[k],1))+" kW)")
            if puissUF>0:
                print("L'utilité froide totale: "+str(round(puissUF,1))+" kW")
                Reseau1.append("L'utilité froide totale: "+str(round(puissUF,1))+" kW")

        # for b in range(len(ensFluxF)):
        #     #for x in range(len(ensFluxF[b].listeSsFlux)):
        #     print(str(ensFluxF[b].type)+str(ensFluxF[b].numero))
        #     print(len(ensFluxF[b].listeSsFlux))






        return(surconsoF*2,Reseau1)



    else:#Dans ce cas on a uniquement des flux chauds ou uniquement des flux froids
        if MerDessusTab==[]:#Dans ce cas on est en continu
            for j in range(len(ensFluxF)):#Calcul puissance utilité chaude	
                print(ensFluxF[j].numero)	
                print(ensFluxF[j].chargeThA)			
                if ensFluxF[j].chargeThA>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TeF=max(TpincementF,ensFluxF[j].Te)
                    TsF=TeF+ensFluxF[j].chargeThA/ensFluxF[j].CP
                    print("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThA,1))+" kW - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1)))	
                    Reseau1.append("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThA,1))+" kW - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1)))
                    ssFluxF=ssFlux.ssFlux(TeF,TsF,ensFluxF[j].CP*1000,ensFluxF[j].debVol,ensFluxF[j].rho,ensFluxF[j].mu,ensFluxF[j].lamb,ensFluxF[j].press,ensFluxFinit[j],ensFluxF[j].type,False,True,ensFluxF[j].chargeThA)
                    ensFluxF[j].listeSsFlux.append(ssFluxF)
                    listeUtilite.append(utilite.utilite(ssFluxF,ensFluxF[j].chargeThA,"c",TeF,TsF))
                    puissUC+=ensFluxF[j].chargeThA
            for i in range(len(ensFluxC)):#Calcul puissance utilité chaude				
                if ensFluxC[i].chargeThA>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TsC=max(TpincementC,ensFluxC[i].Ts)
                    TeC=TsC+ensFluxC[i].chargeThA/ensFluxC[i].CP
                    print("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThA,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1)))		
                    Reseau1.append("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThA,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1)))
                    ssFluxC=ssFlux.ssFlux(TeC,TsC,ensFluxC[i].CP*1000,ensFluxC[i].debVol,ensFluxC[i].rho,ensFluxC[i].mu,ensFluxC[i].lamb,ensFluxC[i].press,ensFluxCinit[i],ensFluxC[i].type,False,True,ensFluxC[i].chargeThA)
                    ensFluxC[i].listeSsFlux.append(ssFluxC)
                    listeUtilite.append(utilite.utilite(ssFluxC,ensFluxC[i].chargeThA,"f",TeC,TsC))
                    puissUF+=ensFluxC[i].chargeThA		

            surconsoF=0

            print("Le MER au-dessus du pincement atteint ("+str(round(deltaH[0],1))+" kW)")
            Reseau1.append("Le MER au-dessus du pincement atteint ("+str(round(deltaH[0],1))+" kW)")

        else:#dans ce cas on est en discontinu
            for j in range(len(ensFluxF)):#Calcul puissance utilité chaude	
                print(ensFluxF[j].numero)	
                print(ensFluxF[j].chargeThA)			
                if ensFluxF[j].chargeThA>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TeF=max(TpincementF,ensFluxF[j].Te)
                    TsF=TeF+ensFluxF[j].chargeThA/ensFluxF[j].CP
                    print("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThA,1))+" kW - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1)))	
                    Reseau1.append("Utilité chaude f"+str(ensFluxF[j].nom)+": "+str(round(ensFluxF[j].chargeThA,1))+" kW - TeF/TsF : "+str(round(TeF,1))+"/"+str(round(TsF,1)))
                    ssFluxF=ssFlux.ssFlux(TeF,TsF,ensFluxF[j].CP*1000,ensFluxF[j].debVol,ensFluxF[j].rho,ensFluxF[j].mu,ensFluxF[j].lamb,ensFluxF[j].press,ensFluxFinit[j],ensFluxF[j].type,False,True,ensFluxF[j].chargeThA)
                    ensFluxF[j].listeSsFlux.append(ssFluxF)
                    listeUtilite.append(utilite.utilite(ssFluxF,ensFluxF[j].chargeThA,"c",TeF,TsF))
                    puissUC+=ensFluxF[j].chargeThA
            for i in range(len(ensFluxC)):#Calcul puissance utilité chaude				
                if ensFluxC[i].chargeThA>10**(-10):#>10**(-10) car avec les arrondis on a parfois des chargeTh restante de 10^(-12)
                    TsC=max(TpincementC,ensFluxC[i].Ts)
                    TeC=TsC+ensFluxC[i].chargeThA/ensFluxC[i].CP
                    print("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThA,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1)))		
                    Reseau1.append("Utilité froide c"+str(ensFluxC[i].nom)+": "+str(round(ensFluxC[i].chargeThA,1))+" kW - TeC/TsC : "+str(round(TeC,1))+"/"+str(round(TsC,1)))
                    ssFluxC=ssFlux.ssFlux(TeC,TsC,ensFluxC[i].CP*1000,ensFluxC[i].debVol,ensFluxC[i].rho,ensFluxC[i].mu,ensFluxC[i].lamb,ensFluxC[i].press,ensFluxCinit[i],ensFluxC[i].type,False,True,ensFluxC[i].chargeThA)
                    ensFluxC[i].listeSsFlux.append(ssFluxC)
                    listeUtilite.append(utilite.utilite(ssFluxC,ensFluxC[i].chargeThA,"f",TeC,TsC))
                    puissUF+=ensFluxC[i].chargeThA		

            print("MerDessusTab[k] :"+str(MerDessusTab[k]))
            surconsoF=0
            print("Le MER au-dessus du pincement atteint ("+str(round(max(puissUC,puissUF),1))+" kWh)")
            Reseau1.append("Le MER au-dessus du pincement atteint ("+str(round(max(puissUC,puissUF),1))+" kWh)")






        return(surconsoF,Reseau1)