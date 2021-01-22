# -*- coding: utf-8 -*-
"""
Created on april 29 

@author: p-aToussaint
"""
import matplotlib.pyplot as plt
from operator import itemgetter, attrgetter
import copy

from creation_reseau_statique import Fct, Division
from classes import Flux
   


def divA(ensFluxC,ensFluxF,i,j,TpincementC,TpincementF,deltaTmin,ech,CP,typeEch,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple):#division d'un fluide chaud en-dessous du pincement
    # ########## Liste des échangeurs que l'on souhaite avoir ##########
    # #La liste est une liste de tuples de la forme (numfluxchaud, numfluxfroid)
    # Liste_echangeur = [(5,5), (4,3), (4,4), (5,6), (1,1), (1,2)]
    # print("Liste des échangeurs que l'on souhaite : ", Liste_echangeur)
    # print("On souhaite donc ", len(Liste_echangeur), " échangeurs")
    # possibilite = (ensFluxC[i].numero, ensFluxF[j].numero)
    # if possibilite in Liste_echangeur :
    print("Entrée divA")
    sup=[]
    cond="non"
    ensFluxF[j].test=[]
    while cond!="oui":
        a=0
        b=1
        test=[]
        ensFluxC1=[]
        ensFluxF1=[]
        ensFluxC1=copy.deepcopy(ensFluxC)
        ensFluxF1=copy.deepcopy(ensFluxF)
        ensFluxC2=[]
        ensFluxF2=[]
        ensFluxC2=copy.deepcopy(ensFluxC)
        ensFluxF2=copy.deepcopy(ensFluxF)
        compt=ensFluxF[j].div
        compt1=len(ensFluxC1)-i #compt1 permet de compter le nombre de flux ne pouvant pas échanger avec le flux chaud divisé en question.On retire j car on ne prend pas en compte les flux froids dont les échanges ont déjà été déterminés. 
        ensFluxF[j].verif=0#indique si une des températures du flux froid a été modifiée pour pouvoir échanger avec un flux. Si la boucle permettant d'échanger moins que la charge thermique des deux flux a été utilisée.
        maxPuissEchC=2#représente la quantité maximale pouvant être absorbée par les flux froids ; valeur prise arbitrairement pour pouvoir entrer dans la boucle while ci-dessous
        print("compt avant :"+str(compt))
        print("sup :"+str(sup))
        """print(compt1)
        print(len(ensFluxF1))
        print(ensFluxF1[j].numero)
        print(j)"""
        condEch="non"#"non" indique que la condition n'est pas respectée
        condEch2="non"#"non" indique que la condition n'est pas respectée
        while (b<maxPuissEchC or b==0) and condEch=="non":#or à la place des and #b<maxPuissEchF and (condEch=="non" or condEch2=="non")
            

            CPdiv=0
            if len(ensFluxC2)-len(sup)<ensFluxF[j].div*2:#cela signifierait qu'il n'y a plus de flux chaud qui puisse échanger avec le flux froid. Dans ce cas on doit supprimer une des branche du flux froid # on met cette condition en haut du while car si len(ensFluxC2)=ensFluxF[j].div*2 alors len(ensFluxC2)-sup sera inférieur à ensFluxF[j].div*2 sans qu'on ait le temps de tester les flux présents dans sup
                if ensFluxF[j].div!=1 and ensFluxF[j].div!=0.5:
                    print("0 On annule la division du flux c"+str(ensFluxF2[j].numero))#car une des branches des flux échange toute sa chaleur
                    CPdiv=CP[i]*2
                    ensFluxF[j].div+=0.5
                    CP[i]=0#pour ne pas le divisé (dans la rechercher du max de CP)
                    # print(CP)
                    # print(len(CP))
                    # print(len(ensFluxF))
                    ind=CP.index(max(CP))
                    print("Le fluide froid f"+str(ensFluxF[ind].numero)+" doit être divisé en deux.")
                    if ensFluxF[ind].div==0:
                        ensFluxF[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                    else:
                        ensFluxF[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                    CP[i]=CPdiv#on rétablit la valeur du CP avant la recherche du max
                    #on remet à 0 la valeur des tableaux car on recommence la recherche de flux avec un div différent
                    sup=[]
                    ensFluxF[j].test=[]
                    test=[]
                else:#si c'est le cas alors il ne reste plus qu'à annuler la division et à tester la compatiblité avec le flux froid j ; si cela ne marche pas alors annul="oui"
                    # print("Else ICI")
                    if ensFluxC2[i].numero in test:
                        puissE1=min(ensFluxC2[i].chargeThA,ensFluxF2[j].chargeThA)
                        ech1=copy.deepcopy(ech)
                        if typeEch=="echA1" or typeEch=="echE1-divA1":
                            if ensFluxC1[i].div==0:
                                CPbrC=ensFluxC1[i].CP
                            else:
                                CPbrC=puissE1*ensFluxC1[i].CP/ensFluxC1[i].b
                            CPbrF=ensFluxF[j].CP#car si on arrive ici alors la division de ce flux a été totalement annulée
                            #print("echE1 avant")
                            bclDiv="oui"
                            ech,CP=Fct.echA1(TpincementC,TpincementF,ensFluxC2,ensFluxF2,deltaTmin,puissE1,i,j,CPbrF,CPbrC,ech,bclDiv,CP,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)
                            #print("echE1 après")
                        else:
                            #print("echE avant")
                            CPbrF=ensFluxF[j].CP#car si on arrive ici alors la division de ce flux a été totalement annulée
                            bclDiv="oui"
                            ech,CP=Fct.echA(TpincementC,TpincementF,ensFluxC2,ensFluxF2,deltaTmin,puissE1,i,j,CPbrF,ech,CP,bclDiv,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)
                            #print("echE après")
                        if ech!=ech1:#permet de vérifier que l'échange a été possible lors de l'appel de la fct echE ou echE1
                            #ensFluxC[p].div-=0.5#une branche échange donc on l'a retire sans diviser un autre flux par la suite 
                            #print("ech!=ech1")
                            ensFluxF[j].verif=0
                            annul="non"
                            annuldiv="oui"
                            return(b,annul,annuldiv,i,test,CP)  
                        else:
                            ensFluxF[j].verif=0
                            annul="oui"
                            annuldiv="oui"
                            return(b,annul,annuldiv,i,test,CP)
                    else:
                        ensFluxF[j].verif=0
                        annul="oui"
                        annuldiv="oui"
                        return(b,annul,annuldiv,i,test,CP)
            
            
            
            a=0
            test=[]
            print("condEch : " +str(condEch))
            for p in range(len(ensFluxC1)):
                for m in range(len(ensFluxF1)):
                    # print("m"+str(ensFluxF1[m].numero)+"-p"+str(ensFluxC1[p].numero))
                    # print(sup)
                    #pour le flux chaud divisé ; on prend par défaut les premiers flux froids de la liste ensFluxF1 ; la liste sup permettra de ne pas prendre en compte les flux froids non-compatibles avec le flux chaud divisé
                    #print(ensFluxC1[p].chargeThE)
                    #if ensFluxF1[m].numero==10:
                        #print("froid num: "+ str(ensFluxF1[m].numero)+"-"+str(ensFluxC1[p].numero)+ "-froid charge Th :"+str(ensFluxF1[m].chargeThE))
                    #if p==i and m>=j:
                    """print("--")
                    print("ensFluxF1[m].numero : "+ str(ensFluxF1[m].numero))
                    print("ensFluxC1[p].numero : "+ str(ensFluxC1[p].numero))
                    print(ensFluxC1[p].div)
                    print("ensFluxC1[p].chargeThE : "+ str(ensFluxC1[p].chargeThE))
                    print("ensFluxF1[m].chargeThE : "+ str(ensFluxF1[m].chargeThE))"""
                    # print(p)
                    # print(i)
                    # print(m)
                    # print(j)
                    if p>=i and m==j and ensFluxF1[m].chargeThA!=0 and ensFluxF1[m].div>0:#m>=j : on simule les échanges qu'avec les fluides froids non-traités dans la boucle du code ; ensFluxF1m.numero not in sup : s'il appartient à sup c'est qu'il ne peut pas échanger avec le fluide divisé car il ne respecte pas les règles ; ensFluxC1[p].div>0 : on vérifie que le flux divisé possède encore des branches pour échanger  
                        print(" p>=i and m==j ")
                        if ensFluxC1[p].numero not in sup: 
                            if ensFluxC1[p].chargeThA!=0:
                                print("ensFluxF1[m].div"+str(ensFluxF1[m].div))
                                if typeEch=="echA1-divA1" or typeEch=="echA1":
                                    puissA1=ensFluxF1[m].CP*(ensFluxC1[p].Te-max(TpincementC,ensFluxC1[p].Ts))
                                    puissE1=min(ensFluxF1[m].chargeThA,ensFluxC1[p].chargeThA,puissA1)
                                else:
                                    puissE1=min(ensFluxF1[m].chargeThA,ensFluxC1[p].chargeThA)
                                #if ensFluxF1[m].numero==10:
                                    #print("froid num: "+ str(ensFluxF1[m].numero)+ "-froid charge ThF1 :"+str(ensFluxF1[m].chargeThE)+ "-froid charge ThF2 :"+str(ensFluxF2[m].chargeThE)+"puissE :"+str(puissE1))
                                """print("froid")"""
                                test.append(ensFluxC1[p].numero)
                                ensFluxF[m].test=test
                                #print(ensFluxF1[m].numero)
                                #print(ensFluxF1[m].chargeThE)
                                #print("ensFluxC[p].chargeThE : "+str(ensFluxC[p].chargeThE))
                                #print("puissE1 : "+str(puissE1))
                                # print(test)
                                # print()
                                if puissE1==ensFluxF[m].chargeThA:#si le flux échange toute sa chaleur avec un flux, il n'aura plus d'énergie à échanger avec un autre flux donc on supprime sa division
                                    print("ouiii")
                                    annuldiv="oui"
                                    #verif=0
                                    bclDiv="oui"
                                    CPbrF=ensFluxF[m].CP
                                    ech1=copy.deepcopy(ech)
                                    if typeEch=="echA1" or typeEch=="echA1-divA1":
                                        if ensFluxC1[p].div==0:
                                            CPbrC=ensFluxC1[p].CP
                                        else:
                                            CPbrC=puissE1*ensFluxC1[m].CP/ensFluxC1[m].b
                                            """print("CPbrF avant echE1 : "+str(CPbrF))
                                            print("puissE1 avant echE1 : "+str(puissE1))
                                            print("ensFluxF1[m].b avant echE1 : "+str(ensFluxF1[m].b))
                                            print("ensFluxF1[m].CP avant echE1 : "+str(ensFluxF1[m].CP))"""
                                        #print("echE1 avant")
                                        ech,CP=Fct.echA1(TpincementC,TpincementF,ensFluxC1,ensFluxF1,deltaTmin,puissE1,p,m,CPbrF,CPbrC,ech,bclDiv,CP,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)
                                        #print("echE1 après")
                                    else:
                                        print("echE avant ici")
                                        ech,CP=Fct.echA(TpincementC,TpincementF,ensFluxC1,ensFluxF1,deltaTmin,puissE1,p,m,CPbrF,ech,CP,bclDiv,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)
                                        #print("echE après")
                                    if ech!=ech1:#permet de vérifier que l'échange a été possible lors de l'appel de la fct echE ou echE1
                                        #ensFluxC[p].div-=0.5#une branche échange donc on l'a retire sans diviser un autre flux par la suite 
                                        #print("ech!=ech1")
                                        if p==i:
                                            annul="non"
                                        else:
                                            annul="oui"
                                        return(b,annul,annuldiv,m,test,CP)
                                """print(puissE1)"""
                                a+=puissE1
                                ensFluxF1[m].div-=0.5
                                ensFluxF1[m].chargeThA-=puissE1
                                ensFluxC1[p].chargeThA-=puissE1
                                #if ensFluxF1[m].numero==10:
                                    #print("froid num: "+ str(ensFluxF1[m].numero)+ "-froid charge Th :"+str(ensFluxF1[m].chargeThE)+ "-froid charge ThF2 :"+str(ensFluxF2[m].chargeThE)+"puissE :"+str(puissE1))
                                sup.append(ensFluxC1[p].numero)
                            else:#si sa charge Th est nulle cela signifie que le flux froid a déjà échangé avec les flux chauds précédents et donc qu'il ne pourra jamais échanger avec le flux divisé en question [i]. 
                                """print("Charge Th nulle")
                                print(ensFluxF1[m].numero)"""
                                compt1-=1#permet de vérifier que des flux peuvent encore échanger de la chaleur avec le flux divisé. Car la liste sup ne prend pas cette condition en compte.
                        else:
                            """print("Dans sup")
                            print(ensFluxF1[m].numero)"""
                            compt1-=1#si le flux est dans la liste sup alors cela signifie qu'il ne peut pas échanger avec le flux chaud divisé en question. On l'ajoute donc à compt1

                    #pour les autres flux chauds
                    if p>i and m<j and ensFluxC1[p].chargeThA!=0 and ensFluxF1[m].chargeThA!=0 and (ensFluxF1[m].test==[] or ensFluxC1[p].numero in ensFluxF1[m].test):#and ensFluxF1[m].numero in ensFluxC1[p].test car sinon les fluides froids n'ayant pas encore échangé avec tous les flux de leur test vont se voir attribuer des flux avec lesquelles ils n'échangeront pas réellement (car ils ne sont pas dans leur test), cela n'est vrai que pour les flux possédant un test (flux divisés)
                        print("flux chaud : p<i")
                        puissE1=min(ensFluxF1[m].chargeThA,ensFluxC1[p].chargeThA)
                        if ensFluxC1[p].div==0:
                            CPbrC=ensFluxC1[p].CP
                        else:
                            CPbrC=puissE1*ensFluxC1[p].CP/ensFluxC1[p].b
                        if ensFluxF1[m].div==0:
                            CPbrF=ensFluxF1[m].CP
                        else:#si il s'agit d'un flux placé avant déjà divisé, alors son b aura été calculé
                            CPbrF=puissE1*ensFluxF1[m].CP/ensFluxF1[m].b
                        bclDiv="oui"  
                        ech,CP=Fct.echA1(TpincementC,TpincementF,ensFluxC1,ensFluxF1,deltaTmin,puissE1,p,m,CPbrF,CPbrC,ech,bclDiv,CP,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)
            
            if a==0:#cela veut dire que aucun flux n'a pu échanger avec le flux divisé
                b=1
                print("a==0")
                print("Aucun flux n'a été trouvé pour échanger avec le flux divisé c"+str(ensFluxC[i].numero))
                annul="oui"
                ensFluxF[j].test=test
                annuldiv="oui"
                #verif=0
                return(b,annul,annuldiv,m,test,CP)

            # print("test : "+str(test))
            # print("a"+str(a))
            #on travaille avec ensFluxC/F2 car c'est avec cette liste qu'on travaille en-dessous
            Fct.newTeSimuUp(ensFluxC2,ensFluxF2,ensFluxC,ensFluxF,i,j,test,TpincementC,TpincementF,deltaTmin,compt)#permet de connaître la température qu'auront les flux chauds lorsqu'ils rencontreront le flux froid en question
            #print("#-#")
            listeTeC=[]
            maxPuissEchC=0#représente la quantité maximale pouvant être absorbée par les flux froids
            condEch1=[]
            maxPuissEchC1=[]#récupére la puissance maximale échangeable par chaque flux froid
            minListeTeC=0
            indexNewTeNum=0
            for k in range(len(ensFluxC2)):
                if ensFluxC2[k].numero in test:
                    """print("````")
                    print(ensFluxF2[k].numero)
                    print(ensFluxF[k].newTeNum)
                    print(ensFluxF[k].newTe)
                    print(ensFluxF[k].Te)
                    print(ensFluxF2[k].Te)"""
                    for l in range(len(ensFluxF2)):#on cherche l'index du flux contenu ayant pour numéro newTeNum pour vérifier que le flux se trouve bien avant le flux chaud i 
                        if ensFluxF2[l].numero==ensFluxC[k].newTeNum:
                            indexNewTeNum=l                    
                    if indexNewTeNum>=j or k==i:# condition rempli s'il s'agit du flux froid et chaud appelant la fct divE ; test sur la liste ensFluxF car c'est elle qu'on modifie pour l'attribut newTenum et newTe                   
                        if max((max(ensFluxF[j].Te,TpincementF)+deltaTmin),ensFluxC2[k].Ts)<ensFluxC2[k].Te:#on vérifie que la puissance calculée ne sera pas négative ; on vérifie que TeC>TsC
                            print("choix1")
                            maxPuissEchC+=min(ensFluxC[k].chargeThA,(ensFluxC2[k].Te-max((max(ensFluxF[j].Te,TpincementF)+deltaTmin),ensFluxC2[k].Ts))*ensFluxC2[k].CP)#min(ensFluxC[i].Te,TpincementC) car si il a déjà échangé, sa température d'entrée sera inférieur à TpincemenC sinon elle sera supérieure ; min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts : si jamais la T de sortie du flux froid est inférieure à TeC-deltaTmin
                            maxPuissEchC1.append(min(ensFluxC[k].chargeThA,(ensFluxC2[k].Te-max((max(ensFluxF[j].Te,TpincementF)+deltaTmin),ensFluxC2[k].Ts))*ensFluxC2[k].CP))#min(ensFluxC[i].Te,TpincementC) car si il a déjà échangé, sa température d'entrée sera inférieur à TpincemenC sinon elle sera supérieure ; min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts : si jamais la T de sortie du flux froid est inférieure à TeC-deltaTmin
                            listeTeC.append(ensFluxC2[k].Te)
                    
                    else:
                        print("choix2")
                        """print(ensFluxF2[k].numero)
                        print(ensFluxF[k].newTe)
                        print(ensFluxF2[k].Te)
                        print(max(ensFluxF2[k].Te,ensFluxF2[k].newTe))"""
                        #print("min(ensFluxC[k].chargeThA,(min(ensFluxC2[k].Te,ensFluxC2[k].newTe)-max((max(ensFluxF[j].Te,TpincementF)+deltaTmin),ensFluxC2[k].Ts))*ensFluxC2[k].CP)"+str(min(ensFluxC[k].chargeThA,(min(ensFluxC2[k].Te,ensFluxC2[k].newTe)-max((max(ensFluxF[j].Te,TpincementF)+deltaTmin),ensFluxC2[k].Ts))*ensFluxC2[k].CP)))
                        if max((max(ensFluxF[j].Te,TpincementF)+deltaTmin),ensFluxC2[k].Ts)<min(ensFluxC2[k].Te,ensFluxC2[k].newTe):#on vérifie que la puissance calculée ne sera pas négative ; on vérifie que TeC>TsC
                            maxPuissEchC+=min(ensFluxC[k].chargeThA,(min(ensFluxC2[k].Te,ensFluxC2[k].newTe)-max((max(ensFluxF[j].Te,TpincementF)+deltaTmin),ensFluxC2[k].Ts))*ensFluxC2[k].CP) #max(,) car si le fluide a déjà échangé, sa newTe est égale à la température d'entrée de départ du flux froid
                            maxPuissEchC1.append(min(ensFluxC[k].chargeThA,(min(ensFluxC2[k].Te,ensFluxC2[k].newTe)-max((max(ensFluxF[j].Te,TpincementF)+deltaTmin),ensFluxC2[k].Ts))*ensFluxC2[k].CP)) #max(,) car si le fluide a déjà échangé, sa newTe est égale à la température d'entrée de départ du flux froid
                            listeTeC.append(min(ensFluxC2[k].Te,ensFluxC[k].newTe))#max(,) car si le fluide a déjà échangé, sa newTe est égale à la température d'entrée de départ du flux froid
            if len(listeTeC)==0:#cela signifie que test=[] ou que le if au-dessus n'est pas respecté pour tous les flux
                test=[]
            else:
                minListeTeC=min(listeTeC)#valeur max des Te des flux froids car même si le flux chaud peut par rapport aux chargeTh des flux froids être satisfait, il ne pourra pas l'être par rapport au respect du deltaTmin
            # print(minListeTeC)
            maxPuissEchF=(min((minListeTeC-deltaTmin),ensFluxF[j].Ts)-max(ensFluxF[j].Te,TpincementF))*ensFluxF[j].CP#représente la quantité maximale pouvant être transmise par le flux chaud
            # print("maxPuissEchC : "+str(maxPuissEchC))
            # print("maxPuissEchF : "+str(maxPuissEchF))
            # print("ensFluxF[j].chargeThA : "+str(ensFluxF[j].chargeThA))
            b=min(maxPuissEchC,maxPuissEchF,ensFluxF[j].chargeThA)
            b1=copy.deepcopy(b)

            # print("maxPuissEchC : "+str(maxPuissEchC))
            if b!=0:
                for k in range(len(maxPuissEchC1)):
                    if maxPuissEchC1[k]<b1 or k==len(maxPuissEchC1)-1:#si tous les flux froids sont satisfait par l'échange avec le flux chaud sauf éventuellement le dernier alors on peut sortir du while. 
                        condEch1.append("oui")
                        b1-=maxPuissEchC1[k]
                    else:
                        condEch1.append("non")
                        b1-=maxPuissEchC1[k]
                # print("condEch1 : "+str(condEch1))
                comptCondEch=0
                for k in range(len(condEch1)):
                    if condEch1[k]=="oui":
                        comptCondEch+=1
                if comptCondEch==len(condEch1):
                    condEch="oui"
                # print("condEch : "+str(condEch))  
                    


            if b==maxPuissEchC or b==maxPuissEchF or condEch=="oui":#si c'est le cas, alors on ne vas pas travailler avec ThE1 et non avec ThE (car on échangera moins que la charge Th du flux chaud)
                ensFluxF2[j].chargeThA1=b
                ensFluxF[j].verif+=1
                ensFluxF2[j].verif+=1

            ensFluxF2[j].b=b#on connait maitenant le dénominateur de CPbrF

            # print(b)

            if len(maxPuissEchC1)!=0:#car sinon maxPuissEchC1[0] n'existe pas
                if maxPuissEchC1[0]==maxPuissEchF:#si le premier flux est le flux limitant alors on annule les divisions et on échange avec lui (jeu de données boite grise MIDREX)
                    if ensFluxC2[i].numero in test:
                        puissE1=min(ensFluxC2[i].chargeThA,ensFluxF2[j].chargeThA)
                        ech1=copy.deepcopy(ech)
                        if typeEch=="echA1" or typeEch=="echA1-divA1":
                            if ensFluxC1[p].div==0:
                                CPbrC=ensFluxC1[i].CP
                            else:
                                CPbrC=puissE1*ensFluxC1[i].CP/ensFluxC1[i].b
                            CPbrF=ensFluxF[j].CP#car si on arrive ici alors la division de ce flux a été totalement annulée
                            #print("echE1 avant")
                            bclDiv="oui"
                            ech,CP=Fct.echA1(TpincementC,TpincementF,ensFluxC2,ensFluxF2,deltaTmin,puissE1,i,j,CPbrF,CPbrC,ech,bclDiv,CP,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)
                            #print("echE1 après")
                        else:
                            # print("echE avant là")
                            CPbrF=ensFluxF[j].CP#car si on arrive ici alors la division de ce flux a été totalement annulée
                            bclDiv="oui"
                            ech,CP=Fct.echA(TpincementC,TpincementF,ensFluxC2,ensFluxF2,deltaTmin,puissE1,i,j,CPbrC,ech,CP,bclDiv,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)
                            #print("echE après")
                        if ech!=ech1:#permet de vérifier que l'échange a été possible lors de l'appel de la fct echE ou echE1
                            #ensFluxC[p].div-=0.5#une branche échange donc on l'a retire sans diviser un autre flux par la suite 
                            # print("ech!=ech1")
                            ensFluxF[j].verif=0
                            annul="non"
                            annuldiv="oui"
                            return(b,annul,annuldiv,m,test,CP)  


            # print("sup début : "+str(sup))

            nbFluxMax=0
            for h in range(len(ensFluxC2)):#permet de compter combien de flux ont la même température que la température max 
                if ensFluxC2[h].numero in sup and ensFluxC2[h].numero in test and (ensFluxC2[h].Te==minListeTeC or ensFluxC[h].newTe==minListeTeC):
                    nbFluxMax+=1

            comptNbFluxMax=0
            nbSup=0#permet de ne supprimer qu'un flux dans la liste sup
            supLong=len(sup)
            if b<maxPuissEchC and condEch=="non":#nous allons laisser dans le sup uniquement le flux avec la plus petite Ts car c'est lui qui limite la valeur de b
                #print("len(ensFluxF2)"+str(len(ensFluxF2)))
                for h in range(len(ensFluxC2)): 
                    # print(h)
                    if ensFluxC2[h].numero in sup and ensFluxC2[h].numero in test and nbSup<supLong-1:
                        if (ensFluxC2[h].Te!=minListeTeC and ensFluxC[h].newTe!=minListeTeC):
                            #on remet les valeurs à la valeur initiale pour recommencer la recherche de flux froid
                            ensFluxC1[h].chargeThA=ensFluxC[h].chargeThA
                            sup.remove(ensFluxC2[h].numero)
                            nbSup+=1
                            # print("if")
                        else:
                            if comptNbFluxMax!=nbFluxMax-1:#s'il s'agit du dernier flux atteignant la Te max, on le laisse dans la liste sup
                                ensFluxC1[h].chargeThA=ensFluxF[h].chargeThA
                                sup.remove(ensFluxC2[h].numero)
                                nbSup+=1
                                comptNbFluxMax+=1
                                # print("elseif")
                ensFluxF[j].test=[]
                test=[]

                ensFluxF1[j].chargeThA=ensFluxF[j].chargeThA#??
                ensFluxF1[j].div=ensFluxF[j].div#??

            if test!=[]:#car une des boucles au-dessus remet test à vide
                # print("test[(len(test)-1)"+str(test[len(test)-1]))
                for g in range(len(ensFluxC2)):#on vérifie que ce n'est pas le dernier flux froid de la liste test qui possède la plus grande Te
                    # print("ensFluxC2[g].numero : "+str(ensFluxC2[g].numero))
                    if ensFluxC2[g].numero==test[len(test)-1]:
                        # print("stop1")
                        if ensFluxC[g].newTeNum==ensFluxF2[j].numero:
                            # print("stop2")
                            if ensFluxC2[g].Te==minListeTeC and nbFluxMax==1:
                                condEch2="non"
                            else:#car si un autre flux avant le dernier atteint la Tmax, si le dernier flux n'atteint pas la température max cela n'aura pas d'impact sur le b
                                condEch2="oui"
                        else:
                            # print("stop3")
                            # print("nbFluxMax : "+str(nbFluxMax))
                            # print(max(ensFluxC2[g].Te,ensFluxC[g].newTe))
                            # print(minListeTeC)
                            if max(ensFluxC2[g].Te,ensFluxC[g].newTe)==minListeTeC and nbFluxMax==1:
                                condEch2="non"
                            else:#car si un autre flux avant le dernier atteint la Tmax, si le dernier flux n'atteint pas la température max cela n'aura pas d'impact sur le b
                                condEch2="oui"
                # print("condEch2 : "+str(condEch2))
                # print("sup fin : "+str(sup))
                # print(test)


        

            
        

        #print("i"+str(i))
        #print(sup)
        print("compt : "+str(compt))
        for m in range(len(ensFluxF2)):
            ensFluxF2[m].test1=[]#permet de connaître avec quel échange le flux chaud a pu échanger (valeur modifiée que pour p==i)
            ensFluxF2[m].puissE4=0#si le flux chaud échange avec qu'un flux alors on connaitra la puissance de cette échange
            ensFluxF2[m].puissE3=0#si le flux chaud échange avec qu'un flux alors on connaitra la puissance de cette échange
        for p in range(len(ensFluxC2)):
            for m in range(len(ensFluxF2)):
                #verif=0
                #print("p"+str(ensFluxC2[p].numero)+"-m"+str(ensFluxF2[m].numero))
                #print(ensFluxC2[p].div)
                #print("ensFluxF[j].chargeThE : "+str(ensFluxF[j].chargeThE))
                if m==j and ensFluxF2[m].chargeThA1<10**(-10) and ensFluxF2[m].div>0:#and ensFluxC2[p].verif!=0 ; <10**(-10) : car parfois la chargeTh restante du flux chaud est de l'ordre de 10^(-14), cela entraine donc des delta de température négligeables et donc des échanges impossibles. 
                    if typeEch=="echA1" or typeEch=="echA":#car pour le cas où typeEch=="echE1-divE1", on n'a pas accés à ensFluxC mais à ensFluxC1
                        CPdiv=CP[m]#on ne va pas diviser le flux actuel alors qu'on cherche à annuler sa division
                        CP[m]=0
                        CPcompt=0
                        #print("boucle chargeThE1==0 -- div flux chaud : "+str(ensFluxC2[p].div))
                        if ensFluxF[m].div-ensFluxF2[m].div==0.5:#s'il n'y a eu qu'un échange alors on doit amener son div à 0
                            ensFluxF[m].div=0
                            ensFluxF[m].puissModif="oui"
                            ensFluxF[m].plusEch="non"#indique qu'il n'y a pas plusieurs échanges
                            plusEch="non"
                            if ensFluxF2[m].verif!=0:
                                ensFluxF[m].verif=0
                            if ensFluxF2[m].puissE3!=0:
                                b=ensFluxF2[m].puissE3#car sinon la valeur de b est égale à celle déterminé précédemment ; puissE3 est la puissance échangée dans la boucle qui permet d'échanger moins que la charge thermique des deux flux
                            else:
                                b=ensFluxF2[m].puissE4#puissE4 est la puissance échangée dans la boucle principale
                                # print("b puissE4 : " + str(b))
                        else:
                            plusEch="oui"
                        while ensFluxF2[m].div>0:#boucle différente de celle lorsque annuldiv=="oui" car on ne supprimer les branches où l'échange n'aura pas lieu (et non toutes les branches)
                            # print("ici")
                            # print("1On annule la division du flux f"+str(ensFluxF2[m].numero))#car une des branches des flux échange toute sa chaleur
                            CPcompt+=1
                            ensFluxF2[m].div-=0.5
                            if plusEch=="oui":
                                ensFluxF[m].div-=0.5###### vérifier qu'il est correct de le laisser en sachant que : boucle différente de celle lorsque annuldiv=="oui" car on ne supprimer les branches où l'échange n'aura pas lieu (et non toutes les branches)
                            #print(test)
                            #if len(test)!=0:
                            #test.remove(test[len(test)-1])#retire les flux qui n'ont pas pu échanger avec le flux chaud car celui-ci était déjà satisfait. On commence par les flux 
                            #print(test)
                            ind=CP.index(max(CP))
                            print("Le fluide froid f"+str(ensFluxF[ind].numero)+" doit être divisé en deux.")
                            CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                            if ensFluxF[ind].div==0:
                                ensFluxF[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                            else:
                                ensFluxF[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                        ensFluxF[m].test=ensFluxF2[m].test1#normalement correct mais pas encore testé
                        CP[m]=CPdiv*2**CPcompt#on autorise à nouveau la disivion de ce flux - ** = puissance
                        annul="non"
                        annuldiv="non"
                        ensFluxF[m].b1=0
                        #print("stop")
                        #print(CP)
                        return(b,annul,annuldiv,m,test,CP)
                    else:
                        annul="non"
                        annuldiv="oui"
                        ensFluxF[m].b1=0
                        if ensFluxF2[m].div==ensFluxF[m].div-0.5:#car cela signifie que le flux a échangé qu'une seule fois et donc il n'y a pas d'intérêt d'avoir un verif >0
                            ensFluxF[m].verif=0
                        return(b,annul,annuldiv,m,test,CP)

                if compt==0:
                    cond="oui"
                    annul="non"
                    annuldiv="non"
                    ensFluxF[j].test=test
                    #if ensFluxF[j].numero==5:
                    #print("stop2")
                    return(b,annul,annuldiv,m,test,CP)
                """print(ensFluxF2[m].chargeThE)
                print(ensFluxC2[p].chargeThE)
                print(test)
                print("m : "+str(m))
                print("j : "+str(j))
                print("p : "+str(m))
                print("i : "+str(i))"""
                if ((p>=i and m==j)  or (p>i and m<j)) and ensFluxC2[p].chargeThA!=0 and ensFluxF2[m].chargeThA!=0 and ((m==j and ensFluxC2[p].numero in test) or m!=j) :#on vérifie la condition du deltaTmin uniquement avec les fluides sélectionnés dans la boucle précédente (car sinon entraine une erreur)
                    print("Entrée dans bouclle ")
                    """print(ensFluxC2[p].chargeThE)
                    print(ensFluxF2[m].chargeThE)"""
                    """if ensFluxF2[m].numero==10:
                        print("2numero flux froid"+str(ensFluxF2[m].numero))
                        print("2numero flux chaud"+str(ensFluxC2[p].numero))"""
                    #print("ensFluxC2[p].chargeThE1 : "+str(ensFluxC2[p].chargeThE1))
                    if ensFluxC2[p].newTe>ensFluxC2[p].Te:
                        # print("ensFluxF2[m].CP"+str(ensFluxC2[p].CP))
                        # print("min(ensFluxF2[m].Ts,TpincementF) : "+str(min(ensFluxC2[p].Ts,TpincementF)))
                        # print("ensFluxF2[m].newTe : "+str(ensFluxC2[p].newTe))
                        # print("ensFluxF2[m].Te : "+str(ensFluxC2[p].Te))
                        # print(ensFluxC[p].chargeThA)
                        ensFluxC2[p].chargeThA=min(ensFluxC[p].chargeThA,(ensFluxC2[p].newTe-max(ensFluxC2[p].Ts,TpincementC))*ensFluxC2[p].CP)
                    else:
                        # print("ensFluxF2[m].CP"+str(ensFluxF2[m].CP))
                        # print("min(ensFluxF2[m].Ts,TpincementF) : "+str(min(ensFluxF2[m].Ts,TpincementF)))
                        # print("ensFluxF2[m].Te : "+str(ensFluxF2[m].Te))
                        # print(ensFluxC[p].chargeThA)
                        ensFluxC2[p].chargeThA=min(ensFluxC[p].chargeThA,(ensFluxC2[p].Te-max(ensFluxC2[p].Ts,TpincementC))*ensFluxC2[p].CP)
                    # print("puiss Fluide FROId : " +str(ensFluxF2[m].chargeThA))
                    if ensFluxF2[m].chargeThA1!=0:#alors ThE1 est égale à b
                        # print("2 puissE")
                        puissE1=min(ensFluxF2[m].chargeThA1,ensFluxC2[p].chargeThA)
                    else:
                        # print("1 puissE")
                        puissE1=min(ensFluxF2[m].chargeThA,ensFluxC2[p].chargeThA)
                    if ensFluxC2[p].div==0:
                        CPbrC=ensFluxC2[p].CP
                    else:
                        CPbrC=puissE1*ensFluxC2[p].CP/ensFluxC2[p].b
                    if ensFluxF2[m].div==0:
                        CPbrF=ensFluxF2[m].CP
                    else:#si il s'agit d'un flux placé avant déjà divisé, alors son b aura été calculé
                        if puissE1==ensFluxF2[m].b:#car sinon la valeur de CPbrC est légèrement différent du CP
                            CPbrF=ensFluxF2[m].CP
                        else:
                            CPbrF=puissE1*ensFluxF2[m].CP/ensFluxF2[m].b
                    TsC=max(TpincementC,ensFluxC2[p].Ts)#le but est que les fluides froids atteignent la température de pincementF. Et que le refroidissement des fluides chauds se fasse à la température la plus faible. 
                    TeF=max(TpincementF,ensFluxF2[m].Te)
                    TeC=TsC+puissE1/CPbrC
                    TsF=TeF+puissE1/CPbrF
                    # print("/oui")
                    # print(ensFluxF2[m].numero)
                    # print(ensFluxC2[p].numero)
                    # #print(ensFluxC2[p].div)
                    # #print(ensFluxC2[p].CP)
                    # print(ensFluxC2[p].b)
                    # print(puissE1)
                    # print(ensFluxF2[m].chargeThA)
                    # print(TeC)
                    # print(TsC)
                    # print(TeF)
                    # print(TsF)
                    # print(CPbrF)
                    # print(CPbrC)
                    if TeC>=(TsF+deltaTmin) and TsC>=TeF+deltaTmin  and (CPbrC<=round(CPbrF,3) or ensFluxC2[p].Ts>TpincementC):#on n'a pas besoin de simuler les échanges ayant lieu avec les fluides froids positionnés après le fluide froid en question car ils n'auront pas d'impact sur les échanges du fluide froid en question.:
                        print("echange possible")
                        ensFluxF2[m].chargeThA-=puissE1
                        ensFluxF2[m].puissE4+=puissE1
                        if (ensFluxF[m].verif!=0 or ensFluxF2[m].chargeThA1!=0) and m==j:
                            ensFluxF2[m].chargeThA1-=puissE1
                        ensFluxC2[p].chargeThA-=puissE1
                        if m==j:#si le flux respecte les règles on le retire de la liste sup
                            print("flux validé")
                            sup.remove(ensFluxC2[p].numero)
                            compt-=0.5
                            ensFluxF2[m].test1.append(ensFluxC2[p].numero)
                        if ensFluxF2[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                            ensFluxF2[m].Te=TsF
                        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                            if ensFluxF2[m].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                ensFluxF2[m].div-=0.5
                                ensFluxF2[m].Te=TsF
                            else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                ensFluxF2[m].div-=0.5
                        if ensFluxC2[p].div==0:
                            ensFluxC2[p].Ts=TeC
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            if ensFluxC2[p].div==0.5:
                                ensFluxC2[p].div-=0.5
                                ensFluxC2[p].Ts=TeC
                                ensFluxC2[p].pinc="oui"
                            else:
                                ensFluxC2[p].div-=0.5
        
                    else:#prend en compte que l'échange peut-être inférieure à la charge Th d'un des flux (car sinon la condition deltaTmin n'est pas respectée)
                        #print("else")
                        #print("verif flux chaud :" +str(ensFluxC2[p].verif))
                        if ensFluxF2[m].Te<ensFluxC2[p].Te:#and ensFluxC2[p].verif==0 #on vérifie que verif est nul car sinon cela signifie que les températures du flux chauds ont déjà été modifiés pour s'adapter un flux. Si on les modifie à nouveau, les températures ne seront plus adaptées pour le premier flux.
                            #print("stop")
                            """print(ensFluxF2[m].numero)
                            print(ensFluxC2[p].numero)
                            print(ensFluxC2[p].chargeThE1)"""
                            if TeC<=TeF+deltaTmin:
                                b=b#inutile (permet juste de ne pas afficher print("PB ..."))
                            else:
                                #print("EEELLLLLSSEE")
                                """print("b1 : "+str(ensFluxC2[p].b))
                                print("ensFluxC2[i].b : "+str(ensFluxC2[i].b))
                                print("puissMaxEch : "+str(maxPuissEch))
                                print("maxListeTeF : "+str(maxListeTeF))
                                print("ensFluxC[i].Te : "+str(ensFluxC[i].Te))
                                print("ensFluxC[i].CP : "+str(ensFluxC[i].CP))"""
                                if TsC<(TeF+deltaTmin):# / hypothèse : la chargeTh minimale est celle du fluide chaud / on va augmenter la température de sortie du fluide chaud. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                                    if TeC<ensFluxC2[p].Te:
                                        TeC=ensFluxC2[p].Te
                                    if ensFluxF2[m].verif!=0:
                                        TsF=TeF+ensFluxF2[m].b/ensFluxF2[m].CP
                                    else:
                                        TsF=TeC-deltaTmin
                                    TsC=max(ensFluxC2[p].Ts,TeF+deltaTmin)
                                    ensFluxC2[p].chargeThA1=(TeC-TsC)*ensFluxC2[p].CP
                                    if typeEch!="echA" and p==i:
                                        ensFluxC[i].chargeThA1=(TeC-TsC)*ensFluxC[i].CP
                                    puissE=min(ensFluxC2[p].chargeThA1,ensFluxF2[m].chargeThA1)
                                    CPbrF=puissE*ensFluxF2[m].CP/ensFluxF2[m].b

                                
                                    # print("$")
                                    # print(puissE)
                                    # print(TeC)
                                    # print(TsC)
                                    # print(TeF)
                                    # print(TsF)
                                    # print(CPbrC)
                                    if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                                        print("échange1")
                                        ensFluxF2[m].chargeThA1-=puissE
                                        ensFluxC2[p].chargeThA-=puissE
                                        ensFluxF2[m].puissE3=puissE
                                        #print(ensFluxC2[p].puissE3)
                                        #if ensFluxF2[m].numero==10:
                                            #print(puissE)
                                            #print(ensFluxC2[p].chargeThE1)
                                        #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                                        if m==j:#si le flux respecte les règles on le retire de la liste sup
                                            if ensFluxF2[m].verif==0:
                                                #ensFluxC2[p].chargeThE1=ensFluxC2[p].chargeThE
                                                b=(TsF-TeF)*ensFluxF2[m].CP
                                                ensFluxF[m].verif+=1
                                                ensFluxF2[m].verif+=1
                                                print("verif +1")
                                            sup.remove(ensFluxC2[p].numero)
                                            compt-=0.5
                                            ensFluxF2[m].puissE4+=puissE
                                            ensFluxF2[m].test1.append(ensFluxC2[p].numero)
                                        if ensFluxF2[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                                            ensFluxF2[m].Te=TsF
                                        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                                            if ensFluxF2[m].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                                ensFluxF2[m].div-=0.5
                                                ensFluxF2[m].Te=TsF
                                            else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                                ensFluxF2[m].div-=0.5
                                        #ensFluxF2[m].Ts=TeF  on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                                        if ensFluxC2[p].div!=0:
                                            if ensFluxC2[p].div==0.5:
                                                ensFluxC2[p].div-=0.5
                                                ensFluxC2[p].Te=TsC
                                                ensFluxC[p].newTe=TsC
                                                ensFluxC[p].newTeNum=ensFluxF2[m].numero
                                                ensFluxC2[p].pinc="oui"
                                            else:
                                                ensFluxC2[p].div-=0.5 
                                        else:
                                            ensFluxC2[p].Te=TsC
                                            ensFluxC[p].newTe=TsC
                                            ensFluxC[p].newTeNum=ensFluxF2[m].numero
                                if TeC<(TsF+deltaTmin): #hypothèse : "la chargeTh minimale est celle du fluide froid". On va réduire la température de sortie du flux froid. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)

                                    TeC1=copy.deepcopy(TeC)
                                    TeC=ensFluxC2[p].Te#car sinon TeF est égal à la valeur calculé dans la 1ère boucle ; si newTe n'a pas été modifé, il est égale à Te sinon il est égale à la Te qu'aura ce flux froid quand il rencontrera ce flux chaud
                                    if ensFluxF2[m].verif!=0:#car si le flux a déjà échangé sa temp de sortie est déjà déterminé
                                        # print("stop2")
                                        # print(TeC)
                                        # print(ensFluxC2[p].CP)
                                        # print(ensFluxC2[p].b)
                                        TsF=TeF+ensFluxF2[m].b/ensFluxF2[m].CP
                                    else:
                                        # print("stop3")
                                        TsF=TeC-deltaTmin#comme la puissance échangé sera inférieure à la charge Th du flux chaud, sa température de sortie sera différente. 
                                    if TsF>ensFluxF2[m].Ts:
                                        TeC=TeC1
                                        TsF=TeC-deltaTmin
                                    TsC=min(ensFluxC2[p].Ts,TeF+deltaTmin)
                                    ensFluxC2[p].chargeThA1=(TeC-TsC)*ensFluxC2[p].CP
                                    if typeEch!="echA":#new boite Midrex False/False
                                        ensFluxC[i].chargeThA1=(TeC-TsC)*ensFluxC[i].CP
                                    """print(ensFluxC2[p].chargeThE1)
                                    print(ensFluxF2[m].chargeThE1)"""
                                    puissE=min(ensFluxC2[p].chargeThA1,ensFluxF2[m].chargeThA1)
                                    if puissE==ensFluxF2[m].chargeThA1:
                                        TsC=TeC-puissE/ensFluxC2[p].CP

                                    if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                                        # print("échange2")
                                        ensFluxF2[m].chargeThA1-=puissE
                                        ensFluxC2[p].chargeThA-=puissE
                                        ensFluxF2[m].puissE3=puissE
                                        if m==j:#si le flux respecte les règles on le retire de la liste sup
                                            if ensFluxF2[m].verif==0:
                                                #ensFluxC2[p].chargeThE1=ensFluxC2[p].chargeThE
                                                b=(TsF-TeF)*ensFluxF2[m].CP
                                                print("verif +1")
                                                ensFluxF[m].verif+=1
                                                ensFluxF2[m].verif+=1
                                            sup.remove(ensFluxC2[p].numero)
                                            compt-=0.5
                                            ensFluxF2[m].puissE4+=puissE
                                            ensFluxF2[m].test1.append(ensFluxC2[p].numero)
                                            #print(ensFluxC2[p].chargeThE1)
                                        if ensFluxF2[m].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                                            ensFluxF2[m].Te=TsF
                                        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                                            if ensFluxF2[m].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                                ensFluxF2[m].div-=0.5
                                                ensFluxF2[m].Te=TsF
                                            else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                                ensFluxF2[m].div-=0.5
                                        #ensFluxF2[m].Ts=TeF  on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                                        if ensFluxC2[p].div!=0:
                                            if ensFluxC2[p].div==0.5:
                                                ensFluxC2[p].div-=0.5
                                                ensFluxC2[p].Te=TsC
                                                ensFluxC[p].newTe=TsC
                                                ensFluxC[p].newTeNum=ensFluxF2[m].numero
                                            else:
                                                ensFluxC2[p].div-=0.5
                                        else:
                                            ensFluxC2[p].Te=TsC
                                            ensFluxC[p].newTe=TsC
                                            ensFluxC[p].newTeNum=ensFluxF2[m].numero

        if compt==0:#la même boucle que au-dessus mais permet de vérifier aussi cette condition à la fin des deux boucles
            cond="oui"
            annul="non"
            annuldiv="non"
            ensFluxF[j].test=test
            return(b,annul,annuldiv,m,test,CP)                 

        # print(" len(ensFluxC1): "+str(len(ensFluxC1)))
        # print("sup : "+str(sup))

        if len(ensFluxC1)-len(sup)<ensFluxF[j].div*2 or compt1<ensFluxF[j].div*2:
            if len(ensFluxF2[j].test1)==0:
                b=1
                print("1 Aucun flux n'a été trouvé pour échanger avec le flux divisé c"+str(ensFluxC[i].numero))
                annul="oui"
                ensFluxF[j].test=test
                annuldiv="oui"
                return(b,annul,annuldiv,m,test,CP)
            else:#si toute les branches n'ont pas pu être satisfaite mais que le flux chaud peut quand même échanger avec un flux froid
                print("boucle TESSST")
                """print(ensFluxC2[i].test1)
                print(ensFluxC2[i].puissE4)"""
                b=ensFluxF2[j].puissE4
                ensFluxF[j].test=ensFluxF2[j].test1
                if typeEch!="echA1":#car pour le cas contraire, on a pas accés à ensFluxC mais à ensFluxC1
                    CPdiv=CP[j]#on ne va pas diviser le flux actuel alors qu'on cherche à annuler sa division
                    CP[j]=0
                    CPcompt=0
                    #print("boucle chargeThE1==0 -- div flux chaud : "+str(ensFluxC2[p].div))
                    if ensFluxF[j].div-ensFluxF2[j].div==0.5:#s'il n'y a eu qu'un échange alors on doit amener son div à 0
                        ensFluxF[j].div=0
                        ensFluxF[j].verif=0
                        ensFluxF[j].puissModif="oui"
                        plusEch="non"
                    else:
                        plusEch="oui"
                    while ensFluxF2[j].div>0:#boucle différente de celle lorsque annuldiv=="oui" car on ne supprimer les branches où l'échange n'aura pas lieu (et non toutes les branches)
                        print("2On annule la division du flux c"+str(ensFluxF2[j].numero))#car une des branches des flux échange toute sa chaleur
                        CPcompt+=1
                        ensFluxF2[j].div-=0.5
                        if plusEch=="oui":
                            ensFluxF[j].div-=0.5###### vérifier qu'il est correct de le laisser en sachant que : boucle différente de celle lorsque annuldiv=="oui" car on ne supprimer les branches où l'échange n'aura pas lieu (et non toutes les branches)
                        #print(test)
                        #if len(test)!=0:
                        #test.remove(test[len(test)-1])#retire les flux qui n'ont pas pu échanger avec le flux chaud car celui-ci était déjà satisfait. On commence par les flux 
                        #print(test)
                        ind=CP.index(max(CP))
                        print("Le fluide froid f"+str(ensFluxF[ind].numero)+" doit être divisé en deux.")
                        CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                        if ensFluxF[ind].div==0:
                            ensFluxF[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                        else:
                            ensFluxF[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                    ensFluxF[j].test=ensFluxF2[j].test1#normalement correct mais pas encore testé
                    CP[j]=CPdiv*2**CPcompt#on autorise à nouveau la disivion de ce flux - ** = puissance
                    annul="non"
                    annuldiv="non"
                    ensFluxF[j].b1=0
                    #print("stop")
                    #print(CP)
                    return(b,annul,annuldiv,m,test,CP)
                else:#vérifier utilité de ce else
                    annul="non"
                    annuldiv="oui"
                    ensFluxF[j].b1=0
                    if ensFluxF2[j].div==ensFluxF[j].div-0.5:#car cela signifie que le flux a échangé qu'une seule fois et donc il n'y a pas d'intérêt d'avoir un verif >0
                        ensFluxF[j].verif=0
                    return(b,annul,annuldiv,m,test,CP)
    # else : 
    #     return ()










# def divA1(ensFluxC,ensFluxF3,i,TpincementC,TpincementF,deltaTmin,CP1,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple):#division d'un fluide froid en-dessous du pincement    
#     ensFluxF2=[]
#     ensFluxF2=copy.deepcopy(ensFluxF3)
#     ensFluxF=copy.deepcopy(ensFluxF3)
#     cond="a"
#     CP=copy.deepcopy(CP1)
#     annul="non"#si le flux chaud divisé ne trouve pas de fluide froid, alors on ne le fait échanger avec aucun flux
#     ech=0
#     affich=0
#     chargeThEch=copy.deepcopy(ensFluxC[i].chargeThA)
#     print()
#     while cond!="ok":#la boucle s'arrête une fois qu'on a trouvé autant de flux que de branches pour échanger
#         # print("-----------")
#         # print("ensFluxC[i].div :"+str(ensFluxC[i].div))
#         #print("len(ensFluxC2) : "+str(len(ensFluxC2)))
#         a=0
#         b=1
#         compt=0
#         compt2=0
#         sup=[]
#         compt3=ensFluxC[i].div#donne le div du flux froid
#         ensFluxC[i].chargeThA=chargeThEch#car on modifie sa valeur à chaque boucle
#         #nbBrF=compt3*2#donne le nb de branche du flux froid


#         # if ensFluxC[i].echChargeTh=="non":#on cherche les flux avec la plus petite Te pour pouvoir échanger un maximum avec le flux chaud (car comme ça le flux chaud pourra descendre plus bas en température). On fait cela que quand echChargeTh="non" car sinon cela n'a pas d'intérêt comme on va tenter d'échanger toute la chargeTh du fluid chaud
#         #     # print("ensFluxC[i].echChargeTh==non")
#         #     ensFluxF4=[]
#         #     minTeTab1=[]
#         #     minTeTab2=[]
#         #     chargeThFTab=[]
#         #     ensFluxF4=copy.deepcopy(ensFluxF2)
#         #     while compt2<compt3:
#         #         minTeTab=[]
#         #         #print("compt2 : "+str(compt2))
#         #         #print("compt3 : "+str(compt3))
#         #         for h in range(len(ensFluxF4)):
#         #             minTeTab.append(max(ensFluxF4[h].Te,TpincementF))#liste qui rassemble les Te des flux froids
#         #         minTe=minTeTab.index(min(minTeTab))#permet de connaitre l'indice des Te min
#         #         minTeTab2.append(min(minTeTab))#permet de connaitre les Te min
#         #         ensFluxF4[minTe].Te=0 #pour ne pas qu'il soit rappelé dans minTeTab
#         #         chargeThFTab.append(ensFluxF4[minTe].chargeThA)
#         #         minTeTab1.append(ensFluxF4[minTe].numero)#permettra de regarder en-dessous si le flux froid en question fait partie des flux froids avec la plus petite Te
#         #         compt2+=0.5
#         #         print("Flux sélectionné :"+str(ensFluxF4[minTe].nom))
#         #     tempMax=max(minTeTab2)+deltaTmin#permettra de calculer le b du flux froid car on se basera sur la température max des flux froids avec la plus faible Te


#         if ensFluxC[i].echChargeTh=="non":#on cherche les flux avec le plus grand CP
#             # print("ensFluxC[i].echChargeTh==non")
#             ensFluxF4=[]
#             minTeTab1=[]
#             minTeTab2=[]
#             chargeThFTab=[]
#             ensFluxF4=copy.deepcopy(ensFluxF2)
#             while compt2<compt3:
#                 minTeTab=[]
#                 for h in range(len(ensFluxF4)):
#                     if ensFluxF4[h].chargeThA!=0: 
#                         minTeTab.append(ensFluxF4[h].CP)#liste qui rassemble les CP des flux froids
#                     else:
#                         minTeTab.append(0)#pour avoir le même nb d'élements dans minTeTab et ensFluxF4
#                 minTe=minTeTab.index(max(minTeTab))#permet de connaitre l'indice des CP max #on garde la même notation que le paragraphe précédent pour avoir les mêmes noms dans le reste du code (et non 2 différents)
#                 #print("minTe : "+str(minTe))
#                 minTeTab2.append(max(ensFluxF4[minTe].Te,TpincementF))#permet de connaitre les Te min parmis les flux sélectionné
#                 ensFluxF4[minTe].CP=0 #pour ne pas qu'il soit rappelé dans minTeTab
#                 chargeThFTab.append(ensFluxF4[minTe].chargeThA)
#                 minTeTab1.append(ensFluxF4[minTe].numero)#permettra de regarder en-dessous si le flux froid en question fait partie des flux froids avec la plus petite Te
#                 compt2+=0.5
#                 print("Flux sélectionné :"+str(ensFluxF4[minTe].nom))
#                 #print(minTeTab1)
#             tempMax=max(minTeTab2)+deltaTmin#permettra de calculer le b du flux froid car on se basera sur la température max des flux froids avec la plus faible Te





#         if ensFluxC[i].chargeThA==0:#car sinon on ne va pas rentrer dans la boucle while et cela va poser problème pour la suite de la fonction (car certaine liste et variables ne seront pas crées)
#             # print("ensFluxC[i].chargeThA==0")
#             annul="oui"
#             b=1#pour éviter le message d'erreur float division by zero
#             return(b,annul)

        

#         while a<ensFluxC[i].chargeThA-10**(-12):#-10**(-12) car sinon cela va créer un échange avec une puissance trop faible et cela n'aura pas de sens#n'implique pas que le b sera toujours égale à ensFluxF[j].chargeThE car si on a ensFluxC[i].echChargeTh=="non", alors le return présent en dessous permet de sortir du while sans respecter la condition là
#             #print("compt4: "+str(compt3))
#             a=0
#             compt=0
#             ensFluxF1=[]
#             puissA=[]
#             fluxSelec=[]#contient le numéro des flux sélectionnés pour échanger avec le flux froid
#             chargeThFluxSelec=[]#contient la charge Th des flux sélectionnés pour échanger avec le flux froid
            
#             if ensFluxC[i].echChargeTh=="oui":#on supprime les flux qui ne peuvent pas satisfaire totalement le fluide chaud (car le Te est trop haute)
#                 for n in range(len(ensFluxF)):
#                     if ensFluxF[n].Te>max(TpincementC,ensFluxC[i].Ts)-deltaTmin: 
#                         for l in range(len(ensFluxF2)):
#                             if ensFluxF2[l].numero==ensFluxF[n].numero:
#                                 ensFluxF2.remove(ensFluxF2[l])
#                                 break
            
#             ancienCP=0
#             comptNb=0
#             tempSortC=0
#             if ensFluxC[i].echChargeTh=="non":#on vérifie que la charge qui sera échangée avec le flux froid ne dépasse pas sa chargeThe car sinon cela veut dire que la valeur de b est trop grande
#                 for d in range(len(ensFluxF2)):
#                     if ensFluxF2[d].numero in minTeTab1:
#                         #print("ensFluxF2[d].numero : "+str(ensFluxF2[d].numero))
#                         if comptNb!=len(minTeTab1):
#                             puissEch=ensFluxF2[d].CP*(ensFluxC[i].Te-tempMax)
#                             ancienCP+=ensFluxF2[d].CP
#                             comptNb+=1
#                         else:
#                             puissEch=(ensFluxC[i].CP-ancienCP)*(ensFluxC[i].Te-tempMax)
#                         if puissEch>ensFluxF2[d].chargeThA:
#                             if comptNb!=len(minTeTab1):
#                                 tempSortC=ensFluxC[i].Te-ensFluxF2[d].chargeThA/ensFluxF2[d].CP
#                             else:
#                                 tempSortC=ensFluxC[i].Te-ensFluxF2[d].chargeThA/(ensFluxC[i].CP-ancienCP)
#                             ensFluxC[i].b=ensFluxC[i].CP*(ensFluxC[i].Te-tempSortC)
#                 if tempSortC!=0:
#                     #print("tempSortC : "+str(tempSortC))
#                     tempMax=tempSortC
#                 ensFluxC[i].b=ensFluxC[i].CP*(ensFluxC[i].Te-tempMax)
#                 ensFluxC[i].tempMax=tempMax#servira dans la suite 
            
#             #print("ensFluxC[i].b : "+str(ensFluxC[i].b))






#             #On rassemble les flux qui vont échanger avec le flux chaud dans une liste
#             ancienCP=0
#             for m in range(len(ensFluxF2)):
#                 # print("ensFluxF2[m].nom : "+str(ensFluxF2[m].nom))
#                 # print(ensFluxF2[m].chargeThA)
#                 if (ensFluxC[i].echChargeTh=="oui" and compt<compt3 and ensFluxF2[m].chargeThA!=0 and ensFluxF2[m].numero not in sup) or (ensFluxC[i].echChargeTh=="non" and  ensFluxF2[m].numero in minTeTab1 and compt<compt3 and ensFluxF2[m].chargeThA!=0 and ensFluxF2[m].numero not in sup) :#and (ensFluxC2[m].numero in maxTeTab1)#on choisit arbitrairement les 1er flux chauds de la liste
#                     #print("min(TpincementC,ensFluxC2[m].Te)-deltaTmin : "+str(min(TpincementC,ensFluxF2[m].Te)-deltaTmin))
#                     print("ensFluxF2[m].numero "+str(ensFluxF2[m].numero))
#                     #print("in minTeTab1 : "+str(minTeTab1))
#                     puissA1=ensFluxF2[m].CP*(ensFluxC[i].Te-max(TpincementC,ensFluxC[i].Ts,max(TpincementF,ensFluxF2[m].Te)+deltaTmin))#on égalise le CP du flux chaud et froid pour que l'échange soit possible
#                     if ensFluxC[i].echChargeTh=="non":
#                         if compt3-compt!=0.5:
#                             CPbrC=ensFluxF2[m].CP
#                             ancienCP+=CPbrC#permettra de connaître la valeur des autres branches lors de l'échange avec la dernière branche
#                         else:
#                             CPbrC=ensFluxC[i].CP-ancienCP
#                         # print(CPbrC)
#                         # print(min(TpincementF,ensFluxF[m].Ts,min(TpincementC,ensFluxF2[m].Te)-deltaTmin))
#                         print("tempMax : "+str(tempMax))
#                         puissA1=CPbrC*(ensFluxC[i].Te-max(TpincementC,ensFluxC[i].Ts,max(TpincementF,ensFluxF2[m].Te)+deltaTmin,tempMax))
#                         print("puissA1 : "+str(puissA1))
#                         # print("puissA1 : "+str(puissA1))
#                         #puissA2=ensFluxC2[m].CP*(min(TpincementC,ensFluxC2[m].Te)-puissA1/ensFluxC2[m].CP)# à revoir car si flux divisé, ce sera CPbrC ; et puissA1 n'est pas correct car il se base sur .CP du flux froid aulieu de CPbrF
#                         #print("puissA2 : "+str(puissA2))
#                     # print("ensFluxC2[m].chargeThE : "+str(ensFluxF2[m].chargeThA))
#                     # print("ensFluxF[j].chargeThE : "+str(ensFluxC[i].chargeThA))
#                     # print("puissA1 : "+str(puissA1))
#                     if ensFluxC[i].echChargeTh=="non":
#                         #print("Ajouté à a : "+str(min(ensFluxC2[m].chargeThE,ensFluxF[j].chargeThE,puissA1)))
#                         puissA.append(min(ensFluxF2[m].chargeThA,ensFluxC[i].chargeThA,puissA1))#,puissA2
#                         a+=min(ensFluxF2[m].chargeThA,ensFluxC[i].chargeThA,puissA1)#,puissA1,puissA2 ; on ajoute la valeur de la puissance échangée à "a"
#                     else:
#                         puissA.append(min(ensFluxF2[m].chargeThA,ensFluxC[i].chargeThA,puissA1))#,puissA1
#                         a+=min(ensFluxF2[m].chargeThA,ensFluxC[i].chargeThA,puissA1)#,puissA1 ; on ajoute la valeur de la puissance échangée à "a"
#                     #print("a : "+str(a))
#                     ensFluxF1.append(ensFluxF2[m])#comprend les flux qui vont échanger avec le flux divisé
#                     #print("Flux ajouté à ensFluxF1 : "+str(ensFluxF2[m].numero))
#                     compt+=0.5
#                     fluxSelec.append(ensFluxF2[m].numero)
#                     chargeThFluxSelec.append(ensFluxF2[m].chargeThA)
#                     print("flux froid fluxSelec : "+str(ensFluxF2[m].numero))

#             if ensFluxC[i].echChargeTh=="oui":
#                 ensFluxC[i].b=min(a,ensFluxC[i].chargeThA)
#             compt1=0

#             if len(ensFluxF2)==0 or a<=0 or b<=0 or len(ensFluxF1)==0:
#                 print("len(ensFluxC2)==0 or a<=0 or b<=0 or len(ensFluxC1)==0")
#                 # print("len(ensFluxF2) : "+str(len(ensFluxF2)))
#                 # print("len(ensFluxF1) : "+str(len(ensFluxF1)))
#                 # print("a : "+str(a))
#                 # print("b : "+str(b))
#                 annul="oui"
#                 b=1#pour éviter le message d'erreur float division by zero
#                 return(b,annul)


#             if ensFluxC[i].echChargeTh=="non":#car sinon la règle a>ensFluxC[i].chargeThA n'est jamais respecté car on va échanger moins que la chargeThA du flud chaud
#                 break


#             """print("a : "+str(a))
#             print("ensFluxF[j].chargeThE : "+str(ensFluxF[j].chargeThE))
#             print("ensFluxF[j].b : "+str(ensFluxF[j].b))"""
#             if a<ensFluxC[i].chargeThA:#nous allons supprimer le flux sélectionnés précédemment qui a la chargeThE la plus basse (valable que si on échange toute la chargeTh du fluide chaud)
#                 indMin=chargeThFluxSelec.index(min(chargeThFluxSelec))#contient l'index du flux avec le minimum de chargeThE
#                 """print(chargeThFluxSelec)
#                 print(fluxSelec)
#                 print(indMin)
#                 print(fluxSelec[indMin])"""
#                 p=0
#                 for k in range(len(ensFluxF2)):
#                     """print("k : "+str(k))
#                     print("ensFluxC2[k].numero : "+str(ensFluxC2[k].numero))"""
#                     if ensFluxF2[k].numero==fluxSelec[indMin]:
#                         p=k
#                 ensFluxF2.remove(ensFluxF2[p])
            
#         compt4=0
#         ancienCP=0
#         print("entrée dans boucle !:!:!")
#         print(a)
#         print(ensFluxC[i].b)
#         #print("ensFluxF[j].Te : "+str(ensFluxC[i].Te))
#         for m in range(len(ensFluxF1)):#on vérifie que les flux sélectionnés respectent le deltaTmin
#             puissE=min(puissA[m],ensFluxC[i].chargeThA)#car pour le dernier échange, la puissance échangée doit permettre de finir de satisfaire le flux chaud
#             print("ensFluxF1[m].nom : "+str(ensFluxF1[m].nom))
#             if ensFluxC[i].echChargeTh=="non":
#                 if compt3-compt4!=0.5:#permet de savoir s'il sagit de la dernière branche ou pas
#                     CPbrC=ensFluxF1[m].CP
#                     ancienCP+=CPbrC#permettra de connaître la valeur des autres branches lors de l'échange avec la dernière branche
#                 else:
#                     CPbrC=ensFluxC[i].CP-ancienCP
#             else:
#                 CPbrC=puissE*ensFluxC[i].CP/ensFluxC[i].b

#             print(puissE)
#             print(ensFluxF1[m].b)
#             print(CPbrC)
#             print(round(CPbrC,10))
#             print(ensFluxF1[m].CP)
#             print(ensFluxF1[m].chargeThA)
#             print(ensFluxC[i].chargeThA)
#             if round(CPbrC,10)<=round(ensFluxF1[m].CP,10) and ensFluxF1[m].chargeThA!=0 and ensFluxC[i].chargeThA!=0:#1.4900000000000002 vs 1.49
#                 for k in range(len(ensFluxF)):
#                     if ensFluxF1[m].numero==ensFluxF[k].numero:#car les flux ne sont pas disposés de la même manière dans les deux listes
#                         ensFluxF1[m].div=ensFluxF[k].div#car on modifie les div lorsqu'on annule des flux
#                 ensFluxF1[m].verif=0
#                 if ensFluxF1[m].chargeThA!=0 and ensFluxC[i].chargeThA!=0:#si les fluides ne sont pas satisfait et le fluide froid possède encore des branches non utilisées (on considère un échange par branche)
#                     if ensFluxF1[m].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
#                         CPbrF=ensFluxF1[m].CP
#                     else:#sinon on pondère le CP avec la puissance du flux complémentaire
#                         if ensFluxF1[m].ech=="non":
#                             div=[]
#                             for h in range(len(ensFluxF1)):#on sauvegarde la valeur des div avant division
#                                 div.append(ensFluxF1[h].div)
#                             # print("--  Entrée divE dans divE1")
#                             # print("ensFluxC1[p].numero"+str(ensFluxF1[m].numero))
#                             # print("ensFluxF[j].chargeThE : "+str(ensFluxC[i].chargeThA))
#                             ensFluxF1[m].b,annul,annuldiv,n,test,CP=Division.divA(ensFluxC,ensFluxF,i,m,TpincementC,TpincementF,deltaTmin,ech,CP,"echA1-divA1",Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)#le but est de simuler les prochains échanges avec le flux chaud divisé pour connaître la valeur de son b. Mais il ne faut pas modifier les attributs "test"... car on n'est pas dans la boucle principale ; on simule avec ensFluxC3 pour pouvoir connaître le b en prennant en compte tous les flux chauds présents sous le pincement
#                             # print("--  Sortie divE dans divE1")
#                             # print(CPbrC)
#                             CPdiv=CP[m]#on ne va pas diviser le flux actuel alors qu'on cherche à annuler sa division
#                             CPdiv1=[]
#                             CPdiv1=copy.deepcopy(CP)
#                             #if annul=="non":
#                                 #CP[p]=0#permet de ne pas diviser un flux dont toutes ses branches n'ont pas fini d'avoir échangé (sinon problème au niveau des .div)
#                             if annuldiv=="oui":
#                                 CP[m]=0
#                                 CPcompt=0
#                                 div=[]
#                                 for h in range(len(ensFluxF)):#on sauvegarde la valeur des div avant division
#                                     div.append(ensFluxF[h].div)
#                                 #print(div)
#                                 while ensFluxF1[m].div!=0:
#                                     verif=0
#                                     for h in range(len(CP)):
#                                         verif+=CP[h]
#                                     if verif==0:#si verif=0 alors tous les flux sont déjà satisfaits
#                                         #print("3Tous les flux sont satisfaits. Division d'un flux chaud impossible")
#                                         for h in range(len(ensFluxF)):#sur ensFluxC car ensFluxC1 et C2 n'ont pas la même taille que la liste div (puis on égalise les div entre ensFluxC1 et ensFluxC à chaque itération)
#                                             ensFluxF[h].div=div[h]
#                                         CP=CPdiv1
#                                         #ensFluxC2.remove(ensFluxC1[p])
#                                         break#permet de stopper la boucle while annul=="oui"
#                                     CPcompt+=1
#                                     if ensFluxF1[m].div==1:#on ne modifie pas C2 car l'annulation de la division de ce flux n'a pas d'importance pour la suite comme ce flux ne sera plus traité après (car on passe au k suivant)
#                                         ensFluxF1[m].div=0
#                                     else:
#                                         ensFluxF1[m].div-=0.5
#                                     #if ensFluxF[j].numero==5:
#                                     #print("On annule la division du flux c"+str(ensFluxC1[p].numero))#car une des branches des flux échange toute sa chaleur
#                                     #division d'un nouveau flux pour toujours respecter la règle des flux
#                                     ind=CP.index(max(CP))
#                                     #if ensFluxF[j].numero==5:
#                                     #print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
#                                     CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
#                                     if ensFluxF[ind].div==0:#on utilise ensFluxC car sinon les indices de CP et ensFluxC2 ne correspondent pas toujours (car on supprime des flux de ensFluxC2)
#                                         ensFluxF[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
#                                     else:
#                                         ensFluxF[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
#                                     for g in range(len(ensFluxF1)):#car sinon on modifie uniquement ensFluxC
#                                         if ensFluxF1[g].numero==ensFluxF[ind].numero:
#                                             ensFluxF1[g].div=ensFluxF[ind].div
#                                 if verif!=0:
#                                     CP[m]=CPdiv*2**CPcompt#on lui réattribue sa valeur moins les branches retirées (annulées)
#                                 else:
#                                     CP[m]=CPdiv
#                                 CPbrF=ensFluxF1[m].CP
#                                 div=[]
#                                 for h in range(len(ensFluxF)):
#                                     div.append(ensFluxF[h].div)
#                                 """if ensFluxF[j].numero==5:
#                                     print(CP)
#                                     print(div)"""
#                             else:
#                                 CPbrF=puissE*ensFluxF1[m].CP/ensFluxF1[m].b
#                         else:
#                             CPbrF=puissE*ensFluxF1[m].CP/ensFluxF1[m].b

#                 TeF=max(TpincementF,ensFluxF1[m].Te)
#                 TsF=TeF+puissE/CPbrF       
#                 if ensFluxC[i].echChargeTh=="non":#si on échange pas toute la charge Th alors le flux chaud démare de sa Te pour atteindre une certaine température de sortie
#                     TeC=ensFluxC[i].Te
#                     TsC=TeC-puissE/CPbrC
#                 else:#si on échange toute la charge Th du flux chaud, on l'amène à sa température de sortie
#                     TsC=max(TpincementC,ensFluxC[i].Ts)#le but est que les fluides froids atteignent la température de pincementF. Et que le refroidissement des fluides chauds se fasse à la température la plus faible. 
#                     TeC=TsC+puissE/CPbrC
#                 #print(ensFluxF[j].numero)
#                 #if ensFluxF[j].numero==5:
#                 affich+=1
#                 if ensFluxC[i].numero==4:
#                     print("/")
#                     print(ensFluxF1[m].nom)
#                     print(puissE)
#                     print(ensFluxC[i].CP)
#                     print(TeC)
#                     print(round(TeC,10))
#                     print(TsC)
#                     print(TeF)
#                     print(TsF)
#                     print(round(TsF,10))
#                     print(CPbrC)
#                     print(round(CPbrC,10))
#                     print(CPbrF)
#                     print(round(CPbrF,10))
#                     print(ensFluxC[i].chargeThA)
#                     print("/")
#                 if annul!="oui" and (round(CPbrF,10)>=round(CPbrC,10) or ensFluxC[i].Ts>TpincementC):
#                     print("hello1")
#                     if round(TeC,10)>=round((TsF+deltaTmin),10) and round(TsC,10)>=round(TeF+deltaTmin,10):
#                         print("echange1")
#                         #print("chargeThE-froid : "+str(ensFluxF[j].chargeThE))
#                         ensFluxC[i].chargeThA-=puissE
#                         ensFluxF1[m].chargeThA-=puissE
#                         ensFluxF[m].chargeThA-=puissE#car c'est lui qu'on met dans l'appel de la fct divE
#                         #print(puissE)
#                         #print("chargeThE-froid : "+str(ensFluxF[j].chargeThE))
#                         if ensFluxF1[m].chargeThA==0:
#                             for j in range(len(ensFluxF)):
#                                 if ensFluxF1[m].numero==ensFluxF[j].numero:
#                                     CP[j]=0
#                         compt1+=1
#                         compt4+=0.5
#                     else:
#                         #print("stop2")
#                         if TeC<=TeF+deltaTmin:
#                             # print("TeC<=TeF+deltaTmin")
#                             for f in range(len(ensFluxF2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
#                                 if ensFluxF2[f].numero==ensFluxF1[m].numero:
#                                     ensFluxF2.remove(ensFluxF2[f])
#                                     break
#                         else:
#                             if TeC<(TsF+deltaTmin):#hypothèse : "la chargeTh minimale est celle du fluide froid". On va réduire la température de sortie du flux froid. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                                                          
#                                 TsF=(min(TeC-deltaTmin,ensFluxF1[m].Ts))
#                                 puissE=(TsF-TeF)*CPbrF
#                                 TsC=max(TeC-puissE/ensFluxC[i].CP,TeF+deltaTmin,ensFluxC[i].Ts,TpincementC)#problème
#                                 # print("stop3")
                             
#                                 if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
#                                     # print("echange2")
#                                     ensFluxC[i].chargeThA-=puissE
#                                     #print("ensFluxC1[p].numero : "+str(ensFluxC1[p].numero))
#                                     # print("ensFluxC[p].numero : "+str(ensFluxC[p].numero))
#                                     ensFluxF1[m].chargeThA-=puissE
#                                     ensFluxF[m].chargeThA-=puissE#car c'est lui qu'on met dans l'appel de la fct divE
#                                     if ensFluxF1[m].chargeThA==0:
#                                         for j in range(len(ensFluxF)):
#                                             if ensFluxF1[m].numero==ensFluxF[j].numero:
#                                                 CP[j]=0
#                                     #print(puissE)
#                                     #print("chargeThE-froid : "+str(ensFluxF[j].chargeThE))
#                                     compt1+=1
#                                     compt4+=0.5
#                                 else:
#                                     for f in range(len(ensFluxF2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
#                                         if ensFluxF2[f].numero==ensFluxF1[m].numero:
#                                             ensFluxF2.remove(ensFluxF2[f])
#                                             break
#                             else:# TsC<(TeF+deltaTmin) / hypothèse : la chargeTh minimale est celle du fluide froid / on va augmenter la température de sortie du fluide chaud. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)

#                                 if ensFluxC[i].echChargeTh=="non":
#                                     TsC=ensFluxC[i].tempMax
#                                 else:
#                                     TsC=TeF+deltaTmin
#                                 if TeC<ensFluxC[i].Te:
#                                     TeC=ensFluxC[i].Te
                                
#                                 puissE=min(ensFluxF1[m].chargeThA,(TeC-TsC)*CPbrC)
#                                 TsF=TeF+puissE/CPbrF
#                                 if puissE==ensFluxF1[m].chargeThA and puissE!=(TeC-TsC)*CPbrC:#cela voudra dire qu'imposer une TsF à deltaTmin de l'entrée du fluide chaud implique que le fluide chaud ne peut pas fournir la chaleur demandé par le fluide froid. Ainsi, si le fluide chaud ne peut pas fournir plus, on recalcule quelle T va atteindre le fluide froid avec cette puissance ; puissE!=(TsF-TeF)*CPbrF : car si les puissE est égale à la charge Th du flux chaux mais aussi à (TsF-TeF)*CPbrF alors le fluide froid pourra absorber cette puissance et il ne sera pas nécessaire de modifier ces températures
#                                     print("stop!!")
#                                     if TeC<TsF+deltaTmin:#si la condition du deltaTmin n'est pas respectée
#                                         TeC=TsF+deltaTmin
#                                     TsC=TeC-puissE/CPbrC


#                                 if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
#                                     print("echange3")
#                                     ensFluxC[i].chargeThA-=puissE
#                                     ensFluxF1[m].chargeThA-=puissE
#                                     ensFluxF[m].chargeThA-=puissE#car c'est lui qu'on met dans l'appel de la fct divE
#                                     #print("chargeThE-froid : "+str(ensFluxF[j].chargeThE))
#                                     if ensFluxF1[m].chargeThA==0:
#                                         for j in range(len(ensFluxF)):
#                                             if ensFluxF1[m].numero==ensFluxF[j].numero:
#                                                 CP[j]=0
#                                     compt1+=1
#                                     compt4+=0.5
#                                 else:
#                                     for f in range(len(ensFluxF2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
#                                         if ensFluxF2[f].numero==ensFluxF1[m].numero:
#                                             ensFluxF2.remove(ensFluxF2[f])
#                                             break
#                 else:
#                     for f in range(len(ensFluxF2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
#                         if ensFluxF2[f].numero==ensFluxF1[m].numero:
#                             ensFluxF2.remove(ensFluxF2[f])
#                             break               
#             else:
#                 for f in range(len(ensFluxF2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
#                     if ensFluxF2[f].numero==ensFluxF1[m].numero:
#                         ensFluxF2.remove(ensFluxF2[f])
#                         break
#         if compt1==compt3*2:#si le deltaTmin est respecté pour chaque flux on sort de la boucle
#             print("cond=ok")
#             cond="ok"
#             ensFluxC[i].test=fluxSelec
#             return(ensFluxC[i].b,annul)#on connait maitenant le dénominateur de CPbrF
#         if len(ensFluxF2)<ensFluxC[i].div*2 or len(ensFluxF1)==0:
#             #if ensFluxC[i].numero!=10 and ensFluxF[j].numero!=11 and ensFluxF[j].numero!=7 and ensFluxF[j].numero!=8 and ensFluxF[j].numero!=9 and ensFluxF[j].numero!=3 and ensFluxF[j].numero!=5:
#             print("Aucun flux n'a été trouvé pour échanger avec le flux divisé c"+str(ensFluxC[i].numero))
#             #ensFluxF[j].div=0#pour annuler la division du flux (car aucun flux ne peux échanger avec)
#             annul="oui"
#             b=1#pour éviter le message d'erreur float division by zero
#             return(b,annul)





def divA1(ensFluxC,ensFluxF3,i,TpincementC,TpincementF,deltaTmin,CP1,Reseau1,ensFluxCinit,ensFluxFinit,listeCouple):#division d'un fluide froid en-dessous du pincement    
    
    ptCP=0.95

    ensFluxF2=[]
    ensFluxF2=copy.deepcopy(ensFluxF3)
    ensFluxF=copy.deepcopy(ensFluxF3)
    cond="a"
    CP=copy.deepcopy(CP1)
    annul="non"#si le flux chaud divisé ne trouve pas de fluide froid, alors on ne le fait échanger avec aucun flux
    ech=0
    affich=0
    chargeThEch=copy.deepcopy(ensFluxC[i].chargeThA)
    print()
    while cond!="ok":#la boucle s'arrête une fois qu'on a trouvé autant de flux que de branches pour échanger
        # print("-----------")
        # print("ensFluxC[i].div :"+str(ensFluxC[i].div))
        #print("len(ensFluxC2) : "+str(len(ensFluxC2)))
        a=0
        b=1
        compt=0
        compt2=0
        sup=[]
        compt3=ensFluxC[i].div#donne le div du flux froid
        ensFluxC[i].chargeThA=chargeThEch#car on modifie sa valeur à chaque boucle
        #nbBrF=compt3*2#donne le nb de branche du flux froid


        # if ensFluxC[i].echChargeTh=="non":#on cherche les flux avec la plus petite Te pour pouvoir échanger un maximum avec le flux chaud (car comme ça le flux chaud pourra descendre plus bas en température). On fait cela que quand echChargeTh="non" car sinon cela n'a pas d'intérêt comme on va tenter d'échanger toute la chargeTh du fluid chaud
        #     # print("ensFluxC[i].echChargeTh==non")
        #     ensFluxF4=[]
        #     minTeTab1=[]
        #     minTeTab2=[]
        #     chargeThFTab=[]
        #     ensFluxF4=copy.deepcopy(ensFluxF2)
        #     while compt2<compt3:
        #         minTeTab=[]
        #         #print("compt2 : "+str(compt2))
        #         #print("compt3 : "+str(compt3))
        #         for h in range(len(ensFluxF4)):
        #             minTeTab.append(max(ensFluxF4[h].Te,TpincementF))#liste qui rassemble les Te des flux froids
        #         minTe=minTeTab.index(min(minTeTab))#permet de connaitre l'indice des Te min
        #         minTeTab2.append(min(minTeTab))#permet de connaitre les Te min
        #         ensFluxF4[minTe].Te=0 #pour ne pas qu'il soit rappelé dans minTeTab
        #         chargeThFTab.append(ensFluxF4[minTe].chargeThA)
        #         minTeTab1.append(ensFluxF4[minTe].numero)#permettra de regarder en-dessous si le flux froid en question fait partie des flux froids avec la plus petite Te
        #         compt2+=0.5
        #         print("Flux sélectionné :"+str(ensFluxF4[minTe].nom))
        #     tempMax=max(minTeTab2)+deltaTmin#permettra de calculer le b du flux froid car on se basera sur la température max des flux froids avec la plus faible Te


        if ensFluxC[i].echChargeTh=="non":#on cherche les flux avec le plus grand CP
            # print("ensFluxC[i].echChargeTh==non")
            ensFluxF4=[]
            minTeTab1=[]
            minTeTab2=[]
            chargeThFTab=[]
            ensFluxF4=copy.deepcopy(ensFluxF2)
            while compt2<compt3:
                minTeTab=[]
                for h in range(len(ensFluxF4)):
                    if ensFluxF4[h].chargeThA!=0: 
                        minTeTab.append(ensFluxF4[h].CP)#liste qui rassemble les CP des flux froids
                    else:
                        minTeTab.append(0)#pour avoir le même nb d'élements dans minTeTab et ensFluxF4
                minTe=minTeTab.index(max(minTeTab))#permet de connaitre l'indice des CP max #on garde la même notation que le paragraphe précédent pour avoir les mêmes noms dans le reste du code (et non 2 différents)
                #print("minTe : "+str(minTe))
                minTeTab2.append(max(ensFluxF4[minTe].Te,TpincementF))#permet de connaitre les Te min parmis les flux sélectionné
                ensFluxF4[minTe].CP=0 #pour ne pas qu'il soit rappelé dans minTeTab
                chargeThFTab.append(ensFluxF4[minTe].chargeThA)
                minTeTab1.append(ensFluxF4[minTe].numero)#permettra de regarder en-dessous si le flux froid en question fait partie des flux froids avec la plus petite Te
                compt2+=0.5
                print("Flux sélectionné :"+str(ensFluxF4[minTe].nom))
                #print(minTeTab1)
            tempMax=max(minTeTab2)+deltaTmin#permettra de calculer le b du flux froid car on se basera sur la température max des flux froids avec la plus faible Te





        if ensFluxC[i].chargeThA==0:#car sinon on ne va pas rentrer dans la boucle while et cela va poser problème pour la suite de la fonction (car certaine liste et variables ne seront pas crées)
            # print("ensFluxC[i].chargeThA==0")
            annul="oui"
            b=1#pour éviter le message d'erreur float division by zero
            return(b,annul)

        

        while a<ensFluxC[i].chargeThA:#-10**(-12) car sinon cela va créer un échange avec une puissance trop faible et cela n'aura pas de sens#n'implique pas que le b sera toujours égale à ensFluxF[j].chargeThE car si on a ensFluxC[i].echChargeTh=="non", alors le return présent en dessous permet de sortir du while sans respecter la condition là
            #print("compt4: "+str(compt3))
            a=0
            compt=0
            ensFluxF1=[]
            puissA=[]
            fluxSelec=[]#contient le numéro des flux sélectionnés pour échanger avec le flux froid
            chargeThFluxSelec=[]#contient la charge Th des flux sélectionnés pour échanger avec le flux froid
            
            if ensFluxC[i].echChargeTh=="oui":#on supprime les flux qui ne peuvent pas satisfaire totalement le fluide chaud (car le Te est trop haute)
                for n in range(len(ensFluxF)):
                    if ensFluxF[n].Te>max(TpincementC,ensFluxC[i].Ts)-deltaTmin: 
                        for l in range(len(ensFluxF2)):
                            if ensFluxF2[l].numero==ensFluxF[n].numero:
                                ensFluxF2.remove(ensFluxF2[l])
                                break
            
            ancienCP=0
            comptNb=0
            tempSortC=0
            if ensFluxC[i].echChargeTh=="non":#on vérifie que la charge qui sera échangée avec le flux froid ne dépasse pas sa chargeThe car sinon cela veut dire que la valeur de b est trop grande
                for d in range(len(ensFluxF2)):
                    if ensFluxF2[d].numero in minTeTab1:
                        #print("ensFluxF2[d].numero : "+str(ensFluxF2[d].numero))
                        if comptNb!=len(minTeTab1):
                            puissEch=ensFluxF2[d].CP*ptCP*(ensFluxC[i].Te-tempMax)
                            ancienCP+=ensFluxF2[d].CP
                            comptNb+=1
                        else:
                            puissEch=(ensFluxC[i].CP-ancienCP)*(ensFluxC[i].Te-tempMax)
                        if puissEch>ensFluxF2[d].chargeThA:
                            if comptNb!=len(minTeTab1):
                                tempSortC=ensFluxC[i].Te-ensFluxF2[d].chargeThA/ensFluxF2[d].CP*ptCP
                            else:
                                tempSortC=ensFluxC[i].Te-ensFluxF2[d].chargeThA/(ensFluxC[i].CP-ancienCP)
                            ensFluxC[i].b=ensFluxC[i].CP*(ensFluxC[i].Te-tempSortC)
                if tempSortC!=0:
                    #print("tempSortC : "+str(tempSortC))
                    tempMax=tempSortC
                ensFluxC[i].b=ensFluxC[i].CP*(ensFluxC[i].Te-tempMax)
                ensFluxC[i].tempMax=tempMax#servira dans la suite 
            
            #print("ensFluxC[i].b : "+str(ensFluxC[i].b))






            #On rassemble les flux qui vont échanger avec le flux chaud dans une liste
            ancienCP=0
            ensFluxC5=copy.deepcopy(ensFluxC)
            for m in range(len(ensFluxF2)):
                # print("ensFluxF2[m].nom : "+str(ensFluxF2[m].nom))
                # print(ensFluxF2[m].chargeThA)
                if (ensFluxC[i].echChargeTh=="oui" and compt<compt3 and ensFluxF2[m].chargeThA!=0 and ensFluxF2[m].numero not in sup) or (ensFluxC[i].echChargeTh=="non" and  ensFluxF2[m].numero in minTeTab1 and compt<compt3 and ensFluxF2[m].chargeThA!=0 and ensFluxF2[m].numero not in sup) :#and (ensFluxC2[m].numero in maxTeTab1)#on choisit arbitrairement les 1er flux chauds de la liste
                    #print("min(TpincementC,ensFluxC2[m].Te)-deltaTmin : "+str(min(TpincementC,ensFluxF2[m].Te)-deltaTmin))
                    print("ensFluxF2[m].numero "+str(ensFluxF2[m].numero))
                    #print("in minTeTab1 : "+str(minTeTab1))
                    puissA1=ensFluxF2[m].CP*ptCP*(ensFluxC[i].Te-max(TpincementC,ensFluxC[i].Ts,max(TpincementF,ensFluxF2[m].Te)+deltaTmin))#-20% du CP froid #on égalise le CP du flux chaud et froid pour que l'échange soit possible
                    if ensFluxC[i].echChargeTh=="non":
                        if compt3-compt!=0.5:
                            CPbrC=ensFluxF2[m].CP*ptCP
                            ancienCP+=CPbrC#permettra de connaître la valeur des autres branches lors de l'échange avec la dernière branche
                        else:
                            CPbrC=ensFluxC[i].CP-ancienCP
                        # print(CPbrC)
                        # print(min(TpincementF,ensFluxF[m].Ts,min(TpincementC,ensFluxF2[m].Te)-deltaTmin))
                        print("tempMax : "+str(tempMax))
                        puissA1=CPbrC*(ensFluxC[i].Te-max(TpincementC,ensFluxC[i].Ts,max(TpincementF,ensFluxF2[m].Te)+deltaTmin,tempMax))
                        print("puissA1 : "+str(puissA1))
                        # print("puissA1 : "+str(puissA1))
                        #puissA2=ensFluxC2[m].CP*(min(TpincementC,ensFluxC2[m].Te)-puissA1/ensFluxC2[m].CP)# à revoir car si flux divisé, ce sera CPbrC ; et puissA1 n'est pas correct car il se base sur .CP du flux froid aulieu de CPbrF
                        #print("puissA2 : "+str(puissA2))
                    # print("ensFluxC2[m].chargeThE : "+str(ensFluxF2[m].chargeThA))
                    # print("ensFluxF[j].chargeThE : "+str(ensFluxC[i].chargeThA))
                    # print("puissA1 : "+str(puissA1))
                    if ensFluxC[i].echChargeTh=="non":
                        #print("Ajouté à a : "+str(min(ensFluxC2[m].chargeThE,ensFluxF[j].chargeThE,puissA1)))
                        puissA.append(min(ensFluxF2[m].chargeThA,ensFluxC5[i].chargeThA,puissA1))#,puissA2
                        a+=min(ensFluxF2[m].chargeThA,ensFluxC5[i].chargeThA,puissA1)#,puissA1,puissA2 ; on ajoute la valeur de la puissance échangée à "a"
                    else:
                        puissA.append(min(ensFluxF2[m].chargeThA,ensFluxC5[i].chargeThA,puissA1))#,puissA1
                        a+=min(ensFluxF2[m].chargeThA,ensFluxC5[i].chargeThA,puissA1)#,puissA1 ; on ajoute la valeur de la puissance échangée à "a"
                    #print("a : "+str(a))
                    ensFluxF1.append(ensFluxF2[m])#comprend les flux qui vont échanger avec le flux divisé
                    #print("Flux ajouté à ensFluxF1 : "+str(ensFluxF2[m].numero))
                    compt+=0.5
                    fluxSelec.append(ensFluxF2[m].numero)
                    chargeThFluxSelec.append(ensFluxF2[m].chargeThA)
                    ensFluxC5[i].chargeThA-=min(ensFluxF2[m].chargeThA,ensFluxC5[i].chargeThA,puissA1)
                    print("flux froid fluxSelec : "+str(ensFluxF2[m].numero))


            if ensFluxC[i].echChargeTh=="oui":
                ensFluxC[i].b=min(a,ensFluxC[i].chargeThA)
            compt1=0

            if len(ensFluxF2)==0 or a<=0 or b<=0 or len(ensFluxF1)==0:
                print("len(ensFluxC2)==0 or a<=0 or b<=0 or len(ensFluxC1)==0")
                # print("len(ensFluxF2) : "+str(len(ensFluxF2)))
                # print("len(ensFluxF1) : "+str(len(ensFluxF1)))
                # print("a : "+str(a))
                # print("b : "+str(b))
                annul="oui"
                b=1#pour éviter le message d'erreur float division by zero
                return(b,annul)


            if ensFluxC[i].echChargeTh=="non":#car sinon la règle a>ensFluxC[i].chargeThA n'est jamais respecté car on va échanger moins que la chargeThA du flud chaud
                break


            """print("a : "+str(a))
            print("ensFluxF[j].chargeThE : "+str(ensFluxF[j].chargeThE))
            print("ensFluxF[j].b : "+str(ensFluxF[j].b))"""
            if a<ensFluxC[i].chargeThA:#nous allons supprimer le flux sélectionnés précédemment qui a la chargeThE la plus basse (valable que si on échange toute la chargeTh du fluide chaud)
                indMin=chargeThFluxSelec.index(min(chargeThFluxSelec))#contient l'index du flux avec le minimum de chargeThE
                """print(chargeThFluxSelec)
                print(fluxSelec)
                print(indMin)
                print(fluxSelec[indMin])"""
                p=0
                for k in range(len(ensFluxF2)):
                    """print("k : "+str(k))
                    print("ensFluxC2[k].numero : "+str(ensFluxC2[k].numero))"""
                    if ensFluxF2[k].numero==fluxSelec[indMin]:
                        p=k
                ensFluxF2.remove(ensFluxF2[p])
            
        compt4=0
        ancienCP=0
        print("entrée dans boucle !:!:!")
        print(a)
        print(ensFluxC[i].b)
        #print("ensFluxF[j].Te : "+str(ensFluxC[i].Te))
        for m in range(len(ensFluxF1)):#on vérifie que les flux sélectionnés respectent le deltaTmin
            puissE=min(puissA[m],ensFluxC[i].chargeThA)#car pour le dernier échange, la puissance échangée doit permettre de finir de satisfaire le flux chaud
            print("ensFluxF1[m].nom : "+str(ensFluxF1[m].nom))
            if ensFluxC[i].echChargeTh=="non":
                if compt3-compt4!=0.5:#permet de savoir s'il sagit de la dernière branche ou pas
                    CPbrC=ensFluxF1[m].CP*ptCP
                    ancienCP+=CPbrC#permettra de connaître la valeur des autres branches lors de l'échange avec la dernière branche
                else:
                    CPbrC=ensFluxC[i].CP-ancienCP
            else:
                CPbrC=puissE*ensFluxC[i].CP/ensFluxC[i].b

            print(puissE)
            print(ensFluxF1[m].b)
            print(CPbrC)
            print(round(CPbrC,10))
            print(ensFluxF1[m].CP)
            print(ensFluxF1[m].chargeThA)
            print(ensFluxC[i].chargeThA)
            if round(CPbrC,10)<=round(ensFluxF1[m].CP,10) and ensFluxF1[m].chargeThA!=0 and ensFluxC[i].chargeThA!=0:#1.4900000000000002 vs 1.49
                for k in range(len(ensFluxF)):
                    if ensFluxF1[m].numero==ensFluxF[k].numero:#car les flux ne sont pas disposés de la même manière dans les deux listes
                        ensFluxF1[m].div=ensFluxF[k].div#car on modifie les div lorsqu'on annule des flux
                ensFluxF1[m].verif=0
                if ensFluxF1[m].chargeThA!=0 and ensFluxC[i].chargeThA!=0:#si les fluides ne sont pas satisfait et le fluide froid possède encore des branches non utilisées (on considère un échange par branche)
                    if ensFluxF1[m].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                        CPbrF=ensFluxF1[m].CP
                    else:#sinon on pondère le CP avec la puissance du flux complémentaire
                        if ensFluxF1[m].ech=="non":
                            div=[]
                            for h in range(len(ensFluxF1)):#on sauvegarde la valeur des div avant division
                                div.append(ensFluxF1[h].div)
                            # print("--  Entrée divE dans divE1")
                            # print("ensFluxC1[p].numero"+str(ensFluxF1[m].numero))
                            # print("ensFluxF[j].chargeThE : "+str(ensFluxC[i].chargeThA))
                            ensFluxF1[m].b,annul,annuldiv,n,test,CP=Division.divA(ensFluxC,ensFluxF,i,m,TpincementC,TpincementF,deltaTmin,ech,CP,"echA1-divA1",Reseau1,ensFluxCinit,ensFluxFinit,listeCouple)#le but est de simuler les prochains échanges avec le flux chaud divisé pour connaître la valeur de son b. Mais il ne faut pas modifier les attributs "test"... car on n'est pas dans la boucle principale ; on simule avec ensFluxC3 pour pouvoir connaître le b en prennant en compte tous les flux chauds présents sous le pincement
                            # print("--  Sortie divE dans divE1")
                            # print(CPbrC)
                            CPdiv=CP[m]#on ne va pas diviser le flux actuel alors qu'on cherche à annuler sa division
                            CPdiv1=[]
                            CPdiv1=copy.deepcopy(CP)
                            #if annul=="non":
                                #CP[p]=0#permet de ne pas diviser un flux dont toutes ses branches n'ont pas fini d'avoir échangé (sinon problème au niveau des .div)
                            if annuldiv=="oui":
                                CP[m]=0
                                CPcompt=0
                                div=[]
                                for h in range(len(ensFluxF)):#on sauvegarde la valeur des div avant division
                                    div.append(ensFluxF[h].div)
                                #print(div)
                                while ensFluxF1[m].div!=0:
                                    verif=0
                                    for h in range(len(CP)):
                                        verif+=CP[h]
                                    if verif==0:#si verif=0 alors tous les flux sont déjà satisfaits
                                        #print("3Tous les flux sont satisfaits. Division d'un flux chaud impossible")
                                        for h in range(len(ensFluxF)):#sur ensFluxC car ensFluxC1 et C2 n'ont pas la même taille que la liste div (puis on égalise les div entre ensFluxC1 et ensFluxC à chaque itération)
                                            ensFluxF[h].div=div[h]
                                        CP=CPdiv1
                                        #ensFluxC2.remove(ensFluxC1[p])
                                        break#permet de stopper la boucle while annul=="oui"
                                    CPcompt+=1
                                    if ensFluxF1[m].div==1:#on ne modifie pas C2 car l'annulation de la division de ce flux n'a pas d'importance pour la suite comme ce flux ne sera plus traité après (car on passe au k suivant)
                                        ensFluxF1[m].div=0
                                    else:
                                        ensFluxF1[m].div-=0.5
                                    #if ensFluxF[j].numero==5:
                                    #print("On annule la division du flux c"+str(ensFluxC1[p].numero))#car une des branches des flux échange toute sa chaleur
                                    #division d'un nouveau flux pour toujours respecter la règle des flux
                                    ind=CP.index(max(CP))
                                    #if ensFluxF[j].numero==5:
                                    #print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
                                    CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                                    if ensFluxF[ind].div==0:#on utilise ensFluxC car sinon les indices de CP et ensFluxC2 ne correspondent pas toujours (car on supprime des flux de ensFluxC2)
                                        ensFluxF[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                                    else:
                                        ensFluxF[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                                    for g in range(len(ensFluxF1)):#car sinon on modifie uniquement ensFluxC
                                        if ensFluxF1[g].numero==ensFluxF[ind].numero:
                                            ensFluxF1[g].div=ensFluxF[ind].div
                                if verif!=0:
                                    CP[m]=CPdiv*2**CPcompt#on lui réattribue sa valeur moins les branches retirées (annulées)
                                else:
                                    CP[m]=CPdiv
                                CPbrF=ensFluxF1[m].CP
                                div=[]
                                for h in range(len(ensFluxF)):
                                    div.append(ensFluxF[h].div)
                                """if ensFluxF[j].numero==5:
                                    print(CP)
                                    print(div)"""
                            else:
                                CPbrF=puissE*ensFluxF1[m].CP/ensFluxF1[m].b
                        else:
                            CPbrF=puissE*ensFluxF1[m].CP/ensFluxF1[m].b

                TeF=max(TpincementF,ensFluxF1[m].Te)
                TsF=TeF+puissE/CPbrF       
                if ensFluxC[i].echChargeTh=="non":#si on échange pas toute la charge Th alors le flux chaud démare de sa Te pour atteindre une certaine température de sortie
                    TeC=ensFluxC[i].Te
                    TsC=TeC-puissE/CPbrC
                else:#si on échange toute la charge Th du flux chaud, on l'amène à sa température de sortie
                    TsC=max(TpincementC,ensFluxC[i].Ts)#le but est que les fluides froids atteignent la température de pincementF. Et que le refroidissement des fluides chauds se fasse à la température la plus faible. 
                    TeC=TsC+puissE/CPbrC
                #print(ensFluxF[j].numero)
                #if ensFluxF[j].numero==5:
                affich+=1
                if ensFluxC[i].numero==4:
                    print("/")
                    print(ensFluxF1[m].nom)
                    print(puissE)
                    print(ensFluxC[i].CP)
                    print(TeC)
                    print(round(TeC,10))
                    print(TsC)
                    print(TeF)
                    print(TsF)
                    print(round(TsF,10))
                    print(CPbrC)
                    print(round(CPbrC,10))
                    print(CPbrF)
                    print(round(CPbrF,10))
                    print(ensFluxC[i].chargeThA)
                    print("/")
                if annul!="oui" and (round(CPbrF,10)>=round(CPbrC,10) or ensFluxC[i].Ts>TpincementC):
                    print("hello1")
                    if round(TeC,10)>=round((TsF+deltaTmin),10) and round(TsC,10)>=round(TeF+deltaTmin,10):
                        print("echange1")
                        #print("chargeThE-froid : "+str(ensFluxF[j].chargeThE))
                        ensFluxC[i].chargeThA-=puissE
                        ensFluxF1[m].chargeThA-=puissE
                        ensFluxF[m].chargeThA-=puissE#car c'est lui qu'on met dans l'appel de la fct divE
                        #print(puissE)
                        #print("chargeThE-froid : "+str(ensFluxF[j].chargeThE))
                        if ensFluxF1[m].chargeThA==0:
                            for j in range(len(ensFluxF)):
                                if ensFluxF1[m].numero==ensFluxF[j].numero:
                                    CP[j]=0
                        compt1+=1
                        compt4+=0.5
                    else:
                        #print("stop2")
                        if TeC<=TeF+deltaTmin:
                            # print("TeC<=TeF+deltaTmin")
                            for f in range(len(ensFluxF2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
                                if ensFluxF2[f].numero==ensFluxF1[m].numero:
                                    ensFluxF2.remove(ensFluxF2[f])
                                    break
                        else:
                            if TeC<(TsF+deltaTmin):#hypothèse : "la chargeTh minimale est celle du fluide froid". On va réduire la température de sortie du flux froid. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                                                          
                                TsF=(min(TeC-deltaTmin,ensFluxF1[m].Ts))
                                puissE=(TsF-TeF)*CPbrF
                                TsC=max(TeC-puissE/ensFluxC[i].CP,TeF+deltaTmin,ensFluxC[i].Ts,TpincementC)#problème
                                # print("stop3")
                             
                                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                                    # print("echange2")
                                    ensFluxC[i].chargeThA-=puissE
                                    #print("ensFluxC1[p].numero : "+str(ensFluxC1[p].numero))
                                    # print("ensFluxC[p].numero : "+str(ensFluxC[p].numero))
                                    ensFluxF1[m].chargeThA-=puissE
                                    ensFluxF[m].chargeThA-=puissE#car c'est lui qu'on met dans l'appel de la fct divE
                                    if ensFluxF1[m].chargeThA==0:
                                        for j in range(len(ensFluxF)):
                                            if ensFluxF1[m].numero==ensFluxF[j].numero:
                                                CP[j]=0
                                    #print(puissE)
                                    #print("chargeThE-froid : "+str(ensFluxF[j].chargeThE))
                                    compt1+=1
                                    compt4+=0.5
                                else:
                                    for f in range(len(ensFluxF2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
                                        if ensFluxF2[f].numero==ensFluxF1[m].numero:
                                            ensFluxF2.remove(ensFluxF2[f])
                                            break
                            else:# TsC<(TeF+deltaTmin) / hypothèse : la chargeTh minimale est celle du fluide froid / on va augmenter la température de sortie du fluide chaud. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)

                                if ensFluxC[i].echChargeTh=="non":
                                    TsC=ensFluxC[i].tempMax
                                else:
                                    TsC=TeF+deltaTmin
                                if TeC<ensFluxC[i].Te:
                                    TeC=ensFluxC[i].Te
                                
                                puissE=min(ensFluxF1[m].chargeThA,(TeC-TsC)*CPbrC)
                                TsF=TeF+puissE/CPbrF
                                if puissE==ensFluxF1[m].chargeThA and puissE!=(TeC-TsC)*CPbrC:#cela voudra dire qu'imposer une TsF à deltaTmin de l'entrée du fluide chaud implique que le fluide chaud ne peut pas fournir la chaleur demandé par le fluide froid. Ainsi, si le fluide chaud ne peut pas fournir plus, on recalcule quelle T va atteindre le fluide froid avec cette puissance ; puissE!=(TsF-TeF)*CPbrF : car si les puissE est égale à la charge Th du flux chaux mais aussi à (TsF-TeF)*CPbrF alors le fluide froid pourra absorber cette puissance et il ne sera pas nécessaire de modifier ces températures
                                    print("stop!!")
                                    if TeC<TsF+deltaTmin:#si la condition du deltaTmin n'est pas respectée
                                        TeC=TsF+deltaTmin
                                    TsC=TeC-puissE/CPbrC


                                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                                    print("echange3")
                                    ensFluxC[i].chargeThA-=puissE
                                    ensFluxF1[m].chargeThA-=puissE
                                    ensFluxF[m].chargeThA-=puissE#car c'est lui qu'on met dans l'appel de la fct divE
                                    #print("chargeThE-froid : "+str(ensFluxF[j].chargeThE))
                                    if ensFluxF1[m].chargeThA==0:
                                        for j in range(len(ensFluxF)):
                                            if ensFluxF1[m].numero==ensFluxF[j].numero:
                                                CP[j]=0
                                    compt1+=1
                                    compt4+=0.5
                                else:
                                    for f in range(len(ensFluxF2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
                                        if ensFluxF2[f].numero==ensFluxF1[m].numero:
                                            ensFluxF2.remove(ensFluxF2[f])
                                            break
                else:
                    for f in range(len(ensFluxF2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
                        if ensFluxF2[f].numero==ensFluxF1[m].numero:
                            ensFluxF2.remove(ensFluxF2[f])
                            break               
            else:
                for f in range(len(ensFluxF2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
                    if ensFluxF2[f].numero==ensFluxF1[m].numero:
                        ensFluxF2.remove(ensFluxF2[f])
                        break
        if compt1==compt3*2:#si le deltaTmin est respecté pour chaque flux on sort de la boucle
            print("cond=ok")
            cond="ok"
            ensFluxC[i].test=fluxSelec
            return(ensFluxC[i].b,annul)#on connait maitenant le dénominateur de CPbrF
        if len(ensFluxF2)<ensFluxC[i].div*2 or len(ensFluxF1)==0:
            #if ensFluxC[i].numero!=10 and ensFluxF[j].numero!=11 and ensFluxF[j].numero!=7 and ensFluxF[j].numero!=8 and ensFluxF[j].numero!=9 and ensFluxF[j].numero!=3 and ensFluxF[j].numero!=5:
            print("Aucun flux n'a été trouvé pour échanger avec le flux divisé c"+str(ensFluxC[i].numero))
            #ensFluxF[j].div=0#pour annuler la division du flux (car aucun flux ne peux échanger avec)
            annul="oui"
            b=1#pour éviter le message d'erreur float division by zero
            return(b,annul)






def divE(ensFluxC,ensFluxF,i,j,TpincementC,TpincementF,deltaTmin,ech,CP,typeEch,Reseau,ensFluxCinit,ensFluxFinit,listeCouple):#division d'un fluide chaud en-dessous du pincement
    sup=[]
    cond="non"
    ensFluxC[i].test=[]
    while cond!="oui":
        a=0
        b=1
        test=[]
        ensFluxC1=[]
        ensFluxF1=[]
        ensFluxC1=copy.deepcopy(ensFluxC)
        ensFluxF1=copy.deepcopy(ensFluxF)
        ensFluxC2=[]
        ensFluxF2=[]
        ensFluxC2=copy.deepcopy(ensFluxC)
        ensFluxF2=copy.deepcopy(ensFluxF)
        compt=ensFluxC[i].div
        compt1=len(ensFluxF1)-j #compt1 permet de compter le nombre de flux ne pouvant pas échanger avec le flux chaud divisé en question.On retire j car on ne prend pas en compte les flux froids dont les échanges ont déjà été déterminés. 
        ensFluxC[i].verif=0#indique si une des températures du flux chaud a été modifiée pour pouvoir échanger avec un flux. Si la boucle permettant d'échanger moins que la charge thermique des deux flux a été utilisée.
        maxPuissEchF=2#représente la quantité maximale pouvant être absorbée par les flux froids ; valeur prise arbitrairement pour pouvoir entrer dans la boucle while ci-dessous
        """print("compt avant :"+str(compt))
        print(compt1)
        print(len(ensFluxF1))
        print(ensFluxF1[j].numero)
        print(j)"""
        condEch="non"#"non" indique que la condition n'est pas respectée
        condEch2="non"#"non" indique que la condition n'est pas respectée
        while (b<maxPuissEchF or b==0) and condEch=="non":#or à la place des and #b<maxPuissEchF and (condEch=="non" or condEch2=="non")
            
            
            CPdiv=0
            if len(ensFluxF2)-len(sup)<ensFluxC[i].div*2:#cela signifierait qu'il n'y a plus de flux froid qui puisse échanger avec le flux chaud. Dans ce cas on doit supprimer une des branche du flux chaud
                print("len(ensFluxF2)-len(sup)<ensFluxC[i].div*2")
                if ensFluxC[i].div!=1 and ensFluxC[i].div!=0.5:
                    print("0 On annule la division du flux c"+str(ensFluxC2[i].numero))#car une des branches des flux échange toute sa chaleur
                    CPdiv=CP[i]*2
                    ensFluxC[i].div+=0.5
                    CP[i]=0#pour ne pas le divisé (dans la rechercher du max de CP)
                    print(CP)
                    print(len(CP))
                    print(len(ensFluxC))
                    ind=CP.index(max(CP))
                    print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
                    if ensFluxC[ind].div==0:
                        ensFluxC[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                    else:
                        ensFluxC[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                    CP[i]=CPdiv#on rétablit la valeur du CP avant la recherche du max
                    #on remet à 0 la valeur des tableaux car on recommence la recherche de flux avec un div différent
                    sup=[]
                    ensFluxC[i].test=[]
                    test=[]
                else:#si c'est le cas alors il ne reste plus qu'à annuler la division et à tester la compatiblité avec le flux froid j ; si cela ne marche pas alors annul="oui"
                    if ensFluxF2[j].numero in test:
                        puissE1=min(ensFluxF2[j].chargeThE,ensFluxC2[i].chargeThE)
                        ech1=copy.deepcopy(ech)
                        if typeEch=="echE1" or typeEch=="echE1-divE1":
                            if ensFluxF1[j].div==0:
                                CPbrF=ensFluxF1[j].CP
                            else:
                                CPbrF=puissE1*ensFluxF1[j].CP/ensFluxF1[j].b
                            CPbrC=ensFluxC[i].CP#car si on arrive ici alors la division de ce flux a été totalement annulée
                            #print("echE1 avant")
                            bclDiv="oui"
                            ech,CP=Fct.echE1(TpincementC,TpincementF,ensFluxC2,ensFluxF2,deltaTmin,puissE1,i,j,CPbrF,CPbrC,ech,bclDiv,CP,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)
                            #print("echE1 après")
                        else:
                            #print("echE avant")
                            CPbrC=ensFluxC[i].CP#car si on arrive ici alors la division de ce flux a été totalement annulée
                            bclDiv="oui"
                            ech,CP=Fct.echE(TpincementC,TpincementF,ensFluxC2,ensFluxF2,deltaTmin,puissE1,i,j,CPbrC,ech,CP,bclDiv,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)
                            #print("echE après")
                        if ech!=ech1:#permet de vérifier que l'échange a été possible lors de l'appel de la fct echE ou echE1
                            #ensFluxC[p].div-=0.5#une branche échange donc on l'a retire sans diviser un autre flux par la suite 
                            print("ech!=ech1")
                            ensFluxC[i].verif=0
                            annul="non"
                            annuldiv="oui"
                            return(b,annul,annuldiv,j,test,CP)  
                        else:
                            ensFluxC[i].verif=0
                            annul="oui"
                            annuldiv="oui"
                            return(b,annul,annuldiv,j,test,CP)
                    else:
                        ensFluxC[i].verif=0
                        annul="oui"
                        annuldiv="oui"
                        return(b,annul,annuldiv,j,test,CP)


            
            
            
            
            a=0
            test=[]
            print("condEch : " +str(condEch))
            for m in range(len(ensFluxF1)):
                for p in range(len(ensFluxC1)):
                    #print("m"+str(ensFluxF1[m].numero)+"-p"+str(ensFluxC1[p].numero))
                    """print(sup)"""
                    #pour le flux chaud divisé ; on prend par défaut les premiers flux froids de la liste ensFluxF1 ; la liste sup permettra de ne pas prendre en compte les flux froids non-compatibles avec le flux chaud divisé
                    #print(ensFluxC1[p].chargeThE)
                    #if ensFluxF1[m].numero==10:
                        #print("froid num: "+ str(ensFluxF1[m].numero)+"-"+str(ensFluxC1[p].numero)+ "-froid charge Th :"+str(ensFluxF1[m].chargeThE))
                    #if p==i and m>=j:
                    """print("--")
                    print("ensFluxF1[m].numero : "+ str(ensFluxF1[m].numero))
                    print("ensFluxC1[p].numero : "+ str(ensFluxC1[p].numero))
                    print(ensFluxC1[p].div)
                    print("ensFluxC1[p].chargeThE : "+ str(ensFluxC1[p].chargeThE))
                    print("ensFluxF1[m].chargeThE : "+ str(ensFluxF1[m].chargeThE))"""
                    
                    if m>=j and p==i and ensFluxC1[p].chargeThE!=0 and ensFluxC1[p].div>0:#m>=j : on simule les échanges qu'avec les fluides froids non-traités dans la boucle du code ; ensFluxF1m.numero not in sup : s'il appartient à sup c'est qu'il ne peut pas échanger avec le fluide divisé car il ne respecte pas les règles ; ensFluxC1[p].div>0 : on vérifie que le flux divisé possède encore des branches pour échanger  
                        if ensFluxF1[m].numero not in sup: 
                            if ensFluxF1[m].chargeThE!=0:
                                print("ensFluxC1[p].div"+str(ensFluxC1[p].div))
                                if typeEch=="echE1-divE1" or typeEch=="echE1":
                                    puissA1=ensFluxC1[p].CP*(min(TpincementF,ensFluxF1[m].Ts)-ensFluxF1[m].Te)
                                    puissE1=min(ensFluxC1[p].chargeThE,ensFluxF1[m].chargeThE,puissA1)
                                else:
                                    puissE1=min(ensFluxC1[p].chargeThE,ensFluxF1[m].chargeThE)
                                #if ensFluxF1[m].numero==10:
                                    #print("froid num: "+ str(ensFluxF1[m].numero)+ "-froid charge ThF1 :"+str(ensFluxF1[m].chargeThE)+ "-froid charge ThF2 :"+str(ensFluxF2[m].chargeThE)+"puissE :"+str(puissE1))
                                """print("froid")"""
                                test.append(ensFluxF1[m].numero)
                                ensFluxC[p].test=test
                                #print(ensFluxF1[m].numero)
                                #print(ensFluxF1[m].chargeThE)
                                #print("ensFluxC[p].chargeThE : "+str(ensFluxC[p].chargeThE))
                                #print("puissE1 : "+str(puissE1))
                                print(test)
                                print()
                                if puissE1==ensFluxC[p].chargeThE:#si le flux échange toute sa chaleur avec un flux, il n'aura plus d'énergie à échanger avec un autre flux donc on supprime sa division
                                    print("ouiii")
                                    annuldiv="oui"
                                    #verif=0
                                    bclDiv="oui"
                                    CPbrC=ensFluxC[p].CP
                                    ech1=copy.deepcopy(ech)
                                    if typeEch=="echE1" or typeEch=="echE1-divE1":
                                        if ensFluxF1[m].div==0:
                                            CPbrF=ensFluxF1[m].CP
                                        else:
                                            CPbrF=puissE1*ensFluxF1[m].CP/ensFluxF1[m].b
                                            """print("CPbrF avant echE1 : "+str(CPbrF))
                                            print("puissE1 avant echE1 : "+str(puissE1))
                                            print("ensFluxF1[m].b avant echE1 : "+str(ensFluxF1[m].b))
                                            print("ensFluxF1[m].CP avant echE1 : "+str(ensFluxF1[m].CP))"""
                                        #print("echE1 avant")
                                        ech,CP=Fct.echE1(TpincementC,TpincementF,ensFluxC1,ensFluxF1,deltaTmin,puissE1,p,m,CPbrF,CPbrC,ech,bclDiv,CP,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)
                                        #print("echE1 après")
                                    else:
                                        print("echE avant ici")
                                        ech,CP=Fct.echE(TpincementC,TpincementF,ensFluxC1,ensFluxF1,deltaTmin,puissE1,p,m,CPbrC,ech,CP,bclDiv,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)
                                        #print("echE après")
                                    if ech!=ech1:#permet de vérifier que l'échange a été possible lors de l'appel de la fct echE ou echE1
                                        #ensFluxC[p].div-=0.5#une branche échange donc on l'a retire sans diviser un autre flux par la suite 
                                        #print("ech!=ech1")
                                        if m==j:
                                            annul="non"
                                        else:
                                            annul="oui"
                                        return(b,annul,annuldiv,m,test,CP)
                                """print(puissE1)"""
                                a+=puissE1
                                ensFluxC1[p].div-=0.5
                                ensFluxC1[p].chargeThE-=puissE1
                                ensFluxF1[m].chargeThE-=puissE1
                                #if ensFluxF1[m].numero==10:
                                    #print("froid num: "+ str(ensFluxF1[m].numero)+ "-froid charge Th :"+str(ensFluxF1[m].chargeThE)+ "-froid charge ThF2 :"+str(ensFluxF2[m].chargeThE)+"puissE :"+str(puissE1))
                                sup.append(ensFluxF1[m].numero)
                            else:#si sa charge Th est nulle cela signifie que le flux froid a déjà échangé avec les flux chauds précédents et donc qu'il ne pourra jamais échanger avec le flux divisé en question [i]. 
                                """print("Charge Th nulle")
                                print(ensFluxF1[m].numero)"""
                                compt1-=1#permet de vérifier que des flux peuvent encore échanger de la chaleur avec le flux divisé. Car la liste sup ne prend pas cette condition en compte.
                        else:
                            """print("Dans sup")
                            print(ensFluxF1[m].numero)"""
                            compt1-=1#si le flux est dans la liste sup alors cela signifie qu'il ne peut pas échanger avec le flux chaud divisé en question. On l'ajoute donc à compt1

                    #pour les autres flux chauds
                    if m>j and p<i and ensFluxF1[m].chargeThE!=0 and ensFluxC1[p].chargeThE!=0 and (ensFluxC1[p].test==[] or ensFluxF1[m].numero in ensFluxC1[p].test):#and ensFluxF1[m].numero in ensFluxC1[p].test car sinon les fluides froids n'ayant pas encore échangé avec tous les flux de leur test vont se voir attribuer des flux avec lesquelles ils n'échangeront pas réellement (car ils ne sont pas dans leur test), cela n'est vrai que pour les flux possédant un test (flux divisés)
                        print("flux chaud : p<i")
                        puissE1=min(ensFluxC1[p].chargeThE,ensFluxF1[m].chargeThE)
                        if ensFluxF1[m].div==0:
                            CPbrF=ensFluxF1[m].CP
                        else:
                            CPbrF=puissE1*ensFluxF1[m].CP/ensFluxF1[m].b
                        if ensFluxC1[p].div==0:
                            CPbrC=ensFluxC1[p].CP
                        else:#si il s'agit d'un flux placé avant déjà divisé, alors son b aura été calculé
                            CPbrC=puissE1*ensFluxC1[p].CP/ensFluxC1[p].b
                        bclDiv="oui"  
                        ech,CP=Fct.echE1(TpincementC,TpincementF,ensFluxC1,ensFluxF1,deltaTmin,puissE1,p,m,CPbrF,CPbrC,ech,bclDiv,CP,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)
            
            if a==0:#cela veut dire que aucun flux n'a pu échanger avec le flux divisé
                b=1
                print("Aucun flux n'a été trouvé pour échanger avec le flux divisé c"+str(ensFluxC[i].numero))
                annul="oui"
                ensFluxC[i].test=test
                annuldiv="oui"
                #verif=0
                return(b,annul,annuldiv,m,test,CP)

            print("test : "+str(test))
            print("a"+str(a))
            for k in range(len(ensFluxF)):
                print("ensFluxF[k].newTe : "+str(ensFluxF[k].newTe))
                print("ensFluxF[k].newTeNum : "+str(ensFluxF[k].newTeNum))

            #on travaille avec ensFluxC/F2 car c'est avec cette liste qu'on travaille en-dessous
            Fct.newTeSimuDown(ensFluxC2,ensFluxF2,ensFluxC,ensFluxF,i,j,test,TpincementC,TpincementF,deltaTmin,compt)#permet de connaître la température qu'auront les flux froids lorsqu'ils rencontreront le flux chaud en question
            #print("#-#")
            print()
            for k in range(len(ensFluxF)):
                print("ensFluxF[k].newTe : "+str(ensFluxF[k].newTe))
                print("ensFluxF[k].newTeNum : "+str(ensFluxF[k].newTeNum))
            for k in range(len(ensFluxF)):
                print(ensFluxF[k].numero,end='')
            print("Chaud: ")
            for k in range(len(ensFluxC)):
                print(ensFluxC[k].numero,end='')
            print()
            listeTeF=[]
            maxPuissEchF=0#représente la quantité maximale pouvant être absorbée par les flux froids
            condEch1=[]
            maxPuissEchF1=[]#récupére la puissance maximale échangeable par chaque flux froid
            maxListeTeF=0
            indexNewTeNum=0
            for k in range(len(ensFluxF2)):
                if ensFluxF2[k].numero in test:
                    """print("````")
                    print(ensFluxF2[k].nom)
                    print(k)
                    print(ensFluxF2[k].numero)
                    print(ensFluxC2[i].numero)
                    print(ensFluxF2[k].chargeThE)
                    print(ensFluxF[k].newTeNum)
                    print(ensFluxC2[i].numero)
                    print(ensFluxF[k].newTe)
                    print(ensFluxF[k].Te)
                    print(ensFluxF2[k].Te)
                    print((min(ensFluxC[i].Te,TpincementC))-deltaTmin)
                    print(ensFluxF2[k].Ts)
                    print(min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts))"""
                    for l in range(len(ensFluxC2)):#on cherche l'index du flux contenu ayant pour numéro newTeNum pour vérifier que le flux se trouve bien avant le flux chaud i 
                        if ensFluxC2[l].numero==ensFluxF[k].newTeNum:
                           indexNewTeNum=l 

                    if indexNewTeNum>=i or k==j:# and k==j # condition rempli s'il s'agit du flux froid et chaud appelant la fct divE ; test sur la liste ensFluxF car c'est elle qu'on modifie pour l'attribut newTenum et newTe
                        if min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts)>ensFluxF2[k].Te:#on vérifie que la puissance calculée ne sera pas négative
                            print("choix1")
                            maxPuissEchF+=min(ensFluxF[k].chargeThE,(min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts)-ensFluxF2[k].Te)*ensFluxF2[k].CP)#min(ensFluxC[i].Te,TpincementC) car si il a déjà échangé, sa température d'entrée sera inférieur à TpincemenC sinon elle sera supérieure ; min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts : si jamais la T de sortie du flux froid est inférieure à TeC-deltaTmin
                            maxPuissEchF1.append(min(ensFluxF[k].chargeThE,(min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts)-ensFluxF2[k].Te)*ensFluxF2[k].CP))#min(ensFluxC[i].Te,TpincementC) car si il a déjà échangé, sa température d'entrée sera inférieur à TpincemenC sinon elle sera supérieure ; min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts : si jamais la T de sortie du flux froid est inférieure à TeC-deltaTmin
                            listeTeF.append(ensFluxF2[k].Te)

                    else:
                        """print(ensFluxF2[k].nom)
                        print(ensFluxF[k].newTe)
                        print(ensFluxF2[k].Te)
                        print(max(ensFluxF2[k].Te,ensFluxF2[k].newTe))
                        print((min(ensFluxC[i].Te,TpincementC))-deltaTmin)
                        print(ensFluxF2[k].Ts)
                        print(min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts))"""
                        print("-")
                        print(ensFluxF[k].chargeThE)
                        print("ensFluxC[i].Te : "+str(ensFluxC[i].Te))
                        print("TpincementC : "+str(TpincementC))
                        print("ensFluxF2[k].Ts : "+str(ensFluxF2[k].Ts))
                        print("min(ensFluxC[i].Te,TpincementC)-deltaTmin) :"+str(min(ensFluxC[i].Te,TpincementC)-deltaTmin))
                        print(min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts))
                        print("ensFluxF[k].Te : "+str(ensFluxF[k].Te))
                        print("ensFluxF[k].newTe : "+str(ensFluxF[k].newTe))
                        print("ensFluxF[k].newTeNum : "+str(ensFluxF[k].newTeNum))
                        print(max(ensFluxF2[k].Te,ensFluxF[k].newTe))
                        print(ensFluxF2[k].CP)
                        print(min(ensFluxF[k].chargeThE,(min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts)-max(ensFluxF2[k].Te,ensFluxF[k].newTe))*ensFluxF2[k].CP))
                        if min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts)>max(ensFluxF2[k].Te,ensFluxF[k].newTe):#on vérifie que la puissance calculée ne sera pas négative
                            print("choix2")
                            maxPuissEchF+=min(ensFluxF[k].chargeThE,(min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts)-max(ensFluxF2[k].Te,ensFluxF[k].newTe))*ensFluxF2[k].CP) #max(,) car si le fluide a déjà échangé, sa newTe est égale à la température d'entrée de départ du flux froid
                            maxPuissEchF1.append(min(ensFluxF[k].chargeThE,(min((min(ensFluxC[i].Te,TpincementC)-deltaTmin),ensFluxF2[k].Ts)-max(ensFluxF2[k].Te,ensFluxF[k].newTe))*ensFluxF2[k].CP)) #max(,) car si le fluide a déjà échangé, sa newTe est égale à la température d'entrée de départ du flux froid
                            listeTeF.append(max(ensFluxF2[k].Te,ensFluxF[k].newTe))#max(,) car si le fluide a déjà échangé, sa newTe est égale à la température d'entrée de départ du flux froid
            if len(listeTeF)==0:#cela signifie que test=[] ou que le if au-dessus n'est pas respecté pour tous les flux
                test=[]
            else:
                maxListeTeF=max(listeTeF)#valeur max des Te des flux froids car même si le flux chaud peut par rapport aux chargeTh des flux froids être satisfait, il ne pourra pas l'être par rapport au respect du deltaTmin
            print(maxListeTeF)
            maxPuissEchC=(min(ensFluxC[i].Te,TpincementC)-max((maxListeTeF+deltaTmin),ensFluxC[i].Ts))*ensFluxC[i].CP#représente la quantité maximale pouvant être transmise par le flux chaud
            b=min(maxPuissEchC,maxPuissEchF,ensFluxC[i].chargeThE)
            b1=copy.deepcopy(b)
            print("maxPuissEchC"+str(maxPuissEchC))
            print("maxPuissEchF"+str(maxPuissEchF))
            print("b"+str(b))
            print("maxPuissEchF1 : "+str(maxPuissEchF1))

            if b!=0:
                for k in range(len(maxPuissEchF1)):
                    if maxPuissEchF1[k]<b1 or k==len(maxPuissEchF1)-1:#si tous les flux froids sont satisfait par l'échange avec le flux chaud sauf éventuellement le dernier alors on peut sortir du while. Car sinon les 1er flux froids vont absorber toute la chaleur disponible sur le flux chaud et les derniers flux ne recevront pas la quantité de chaleur prévue
                        condEch1.append("oui")
                        b1-=maxPuissEchF1[k]
                    else:
                        condEch1.append("non")
                        b1-=maxPuissEchF1[k]
                print("condEch1 : "+str(condEch1))
                comptCondEch=0
                for k in range(len(condEch1)):
                    if condEch1[k]=="oui":
                        comptCondEch+=1
                if comptCondEch==len(condEch1):
                    condEch="oui"
                print("condEch : "+str(condEch))  
                    


            if b==maxPuissEchF or b==maxPuissEchC or condEch=="oui":#si c'est le cas, alors on ne vas pas travailler avec ThE1 et non avec ThE (car on échangera moins que la charge Th du flux chaud)
                ensFluxC2[i].chargeThE1=b
                ensFluxC[i].verif+=1
                ensFluxC2[i].verif+=1

            ensFluxC2[i].b=b#on connait maitenant le dénominateur de CPbrF

            print("b :"+str(b))

            if len(maxPuissEchF1)!=0:
                if maxPuissEchF1[0]==maxPuissEchC:#si le premier flux est le flux limitant alors on annule les divisions et on échange avec lui (jeu de données boite grise MIDREX) => pq ?
                    if ensFluxF2[j].numero in test:
                        puissE1=min(ensFluxF2[j].chargeThE,ensFluxC2[i].chargeThE)
                        ech1=copy.deepcopy(ech)
                        if typeEch=="echE1" or typeEch=="echE1-divE1":
                            if ensFluxF1[m].div==0:
                                CPbrF=ensFluxF1[j].CP
                            else:
                                CPbrF=puissE1*ensFluxF1[j].CP/ensFluxF1[j].b
                            CPbrC=ensFluxC[i].CP#car si on arrive ici alors la division de ce flux a été totalement annulée
                            #print("echE1 avant")
                            bclDiv="oui"
                            ech,CP=Fct.echE1(TpincementC,TpincementF,ensFluxC2,ensFluxF2,deltaTmin,puissE1,i,j,CPbrF,CPbrC,ech,bclDiv,CP,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)
                            #print("echE1 après")
                        else:
                            print("echE avant là")
                            CPbrC=ensFluxC[i].CP#car si on arrive ici alors la division de ce flux a été totalement annulée
                            bclDiv="oui"
                            ech,CP=Fct.echE(TpincementC,TpincementF,ensFluxC2,ensFluxF2,deltaTmin,puissE1,i,j,CPbrC,ech,CP,bclDiv,Reseau,ensFluxCinit,ensFluxFinit,listeCouple)
                            #print("echE après")
                        if ech!=ech1:#permet de vérifier que l'échange a été possible lors de l'appel de la fct echE ou echE1
                            #ensFluxC[p].div-=0.5#une branche échange donc on l'a retire sans diviser un autre flux par la suite 
                            print("ech!=ech1")
                            ensFluxC[i].verif=0
                            annul="non"
                            annuldiv="oui"
                            return(b,annul,annuldiv,m,test,CP)  


            print("sup début : "+str(sup))

            nbFluxMax=0
            for h in range(len(ensFluxF2)):#permet de compter combien de flux ont la même température que la température max 
                if ensFluxF2[h].numero in sup and ensFluxF2[h].numero in test and (ensFluxF2[h].Te==maxListeTeF or ensFluxF[h].newTe==maxListeTeF):
                    nbFluxMax+=1

            comptNbFluxMax=0
            nbSup=0#permet de ne supprimer qu'un flux dans la liste sup
            supLong=len(sup)
            if b<maxPuissEchF and condEch=="non":#nous allons laisser dans le sup uniquement le flux avec la plus grande Te car c'est lui qui limite la valeur de b
                #print("len(ensFluxF2)"+str(len(ensFluxF2)))
                for h in range(len(ensFluxF2)): 
                    print(h)
                    if ensFluxF2[h].numero in sup and ensFluxF2[h].numero in test and nbSup<supLong-1:
                        if (ensFluxF2[h].Te!=maxListeTeF and ensFluxF[h].newTe!=maxListeTeF):
                            #on remet les valeurs à la valeur initiale pour recommencer la recherche de flux froid
                            ensFluxF1[h].chargeThE=ensFluxF[h].chargeThE
                            sup.remove(ensFluxF2[h].numero)
                            nbSup+=1
                            print("if")
                        else:
                            if comptNbFluxMax!=nbFluxMax-1:#s'il s'agit du dernier flux atteignant la Te max, on le laisse dans la liste sup
                                ensFluxF1[h].chargeThE=ensFluxF[h].chargeThE
                                sup.remove(ensFluxF2[h].numero)
                                nbSup+=1
                                comptNbFluxMax+=1
                                print("elseif")
                ensFluxC[i].test=[]
                test=[]

                ensFluxC1[i].chargeThE=ensFluxC[i].chargeThE#??
                ensFluxC1[i].div=ensFluxC[i].div#??

            if test!=[]:#car une des boucles au-dessus remet test à vide
                #print("test[(len(test)-1)"+str(test[len(test)-1]))
                for g in range(len(ensFluxF2)):#on vérifie que ce n'est pas le dernier flux froid de la liste test qui possède la plus grande Te
                    #print("ensFluxF2[g].numero : "+str(ensFluxF2[g].numero))
                    if ensFluxF2[g].numero==test[len(test)-1]:
                        print("stop1")
                        if ensFluxF[g].newTeNum==ensFluxC2[i].numero:
                            print("stop2")  
                            if ensFluxF2[g].Te==maxListeTeF and nbFluxMax==1:
                                condEch2="non"
                            else:#car si un autre flux avant le dernier atteint la Tmax, si le dernier flux n'atteint pas la température max cela n'aura pas d'impact sur le b
                                condEch2="oui"
                        else:
                            print("stop3")
                            print("nbFluxMax : "+str(nbFluxMax))
                            print(max(ensFluxF2[g].Te,ensFluxF[g].newTe))
                            print(maxListeTeF)
                            if max(ensFluxF2[g].Te,ensFluxF[g].newTe)==maxListeTeF and nbFluxMax==1:
                                condEch2="non"
                            else:#car si un autre flux avant le dernier atteint la Tmax, si le dernier flux n'atteint pas la température max cela n'aura pas d'impact sur le b
                                condEch2="oui"
                """print("condEch2 : "+str(condEch2))
                print("sup fin : "+str(sup))
                print(test)"""
                   


             





        print("test : " + str(test))
        print("b : " + str(b))
        print("ensFluxC2[i].chargeThE1 : "+str(ensFluxC2[i].chargeThE1))

        #print("i"+str(i))
        #print(sup)
        for p in range(len(ensFluxC2)):
            ensFluxC2[p].test1=[]#permet de connaître avec quel échange le flux chaud a pu échanger (valeur modifiée que pour p==i)
            ensFluxC2[p].puissE4=0#si le flux chaud échange avec qu'un flux alors on connaitra la puissance de cette échange
            ensFluxC2[p].puissE3=0#si le flux chaud échange avec qu'un flux alors on connaitra la puissance de cette échange
        for m in range(len(ensFluxF2)):
            for p in range(len(ensFluxC2)):
                #verif=0
                #print("m"+str(ensFluxF2[m].numero)+"-p"+str(ensFluxC2[p].numero))
                #if p==i:
                    #print("ensFluxC2[p].div : "+str(ensFluxC2[p].div))
                #print(ensFluxC2[p].div)
                #print("ensFluxC2[p].chargeThE1 : "+str(ensFluxC2[p].chargeThE1))
                if p==i and ensFluxC2[p].chargeThE1<10**(-10) and ensFluxC2[p].div>0:#and ensFluxC2[p].verif!=0 ; <10**(-10) : car parfois la chargeTh restante du flux chaud est de l'ordre de 10^(-14), cela entraine donc des delta de température négligeables et donc des échanges impossibles. 
                    if typeEch=="echE1" or typeEch=="echE":#car pour le cas où typeEch=="echE1-divE1", on n'a pas accés à ensFluxC mais à ensFluxC1
                        CPdiv=CP[p]#on ne va pas diviser le flux actuel alors qu'on cherche à annuler sa division
                        CP[p]=0
                        CPcompt=0
                        #print("boucle chargeThE1==0 -- div flux chaud : "+str(ensFluxC2[p].div))
                        if ensFluxC[p].div-ensFluxC2[p].div==0.5:#s'il n'y a eu qu'un échange alors on doit amener son div à 0
                            ensFluxC[p].div=0
                            ensFluxC[p].puissModif="oui"
                            ensFluxC[p].plusEch="non"#indique qu'il n'y a pas plusieurs échanges
                            plusEch="non"
                            if ensFluxC2[p].verif!=0:
                                ensFluxC[p].verif=0
                            if ensFluxC2[p].puissE3!=0:
                                b=ensFluxC2[p].puissE3#car sinon la valeur de b est égale à celle déterminé précédemment ; puissE3 est la puissance échangée dans la boucle qui permet d'échanger moins que la charge thermique des deux flux
                            else:
                                b=ensFluxC2[p].puissE4#puissE4 est la puissance échangée dans la boucle principale
                                print("b puissE4 : " + str(b))
                        else:
                            plusEch="oui"
                        while ensFluxC2[p].div>0:#boucle différente de celle lorsque annuldiv=="oui" car on ne supprimer les branches où l'échange n'aura pas lieu (et non toutes les branches)
                            print("1On annule la division du flux c"+str(ensFluxC2[p].numero))#car une des branches des flux échange toute sa chaleur
                            CPcompt+=1
                            ensFluxC2[p].div-=0.5
                            if plusEch=="oui":
                                ensFluxC[p].div-=0.5###### vérifier qu'il est correct de le laisser en sachant que : boucle différente de celle lorsque annuldiv=="oui" car on ne supprimer les branches où l'échange n'aura pas lieu (et non toutes les branches)
                            #print(test)
                            #if len(test)!=0:
                            #test.remove(test[len(test)-1])#retire les flux qui n'ont pas pu échanger avec le flux chaud car celui-ci était déjà satisfait. On commence par les flux 
                            #print(test)
                            ind=CP.index(max(CP))
                            print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
                            CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                            if ensFluxC[ind].div==0:
                                ensFluxC[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                            else:
                                ensFluxC[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                        ensFluxC[p].test=ensFluxC2[p].test1#normalement correct mais pas encore testé
                        CP[p]=CPdiv*2**CPcompt#on autorise à nouveau la disivion de ce flux - ** = puissance
                        annul="non"
                        annuldiv="non"
                        ensFluxC[p].b1=0
                        #print("stop")
                        #print(CP)
                        return(b,annul,annuldiv,m,test,CP)
                    else:
                        annul="non"
                        annuldiv="oui"
                        ensFluxC[p].b1=0
                        if ensFluxC2[p].div==ensFluxC[p].div-0.5:#car cela signifie que le flux a échangé qu'une seule fois et donc il n'y a pas d'intérêt d'avoir un verif >0
                            ensFluxC[p].verif=0
                        return(b,annul,annuldiv,m,test,CP)

                if compt==0:
                    cond="oui"
                    annul="non"
                    annuldiv="non"
                    ensFluxC[i].test=test
                    #if ensFluxF[j].numero==5:
                    #print("stop2")
                    return(b,annul,annuldiv,m,test,CP)
                """print(ensFluxF2[m].chargeThE)
                print(ensFluxC2[p].chargeThE)
                print(test)
                print("m : "+str(m))
                print("j : "+str(j))
                print("p : "+str(m))
                print("i : "+str(i))"""
                if ((m>=j and p==i)  or (m>j and p<i)) and ensFluxF2[m].chargeThE!=0 and ensFluxC2[p].chargeThE!=0 and ((p==i and ensFluxF2[m].numero in test) or p!=i) :#on vérifie la condition du deltaTmin uniquement avec les fluides sélectionnés dans la boucle précédente (car sinon entraine une erreur)
                    print("Entrée dans bouclle ")
                    
                    """print(ensFluxC2[p].chargeThE)
                    print(ensFluxF2[m].chargeThE)"""
                    """if ensFluxF2[m].numero==10:
                        print("2numero flux froid"+str(ensFluxF2[m].numero))
                        print("2numero flux chaud"+str(ensFluxC2[p].numero))"""
                    #print("ensFluxC2[p].chargeThE1 : "+str(ensFluxC2[p].chargeThE1))
                    """for l in range(len(ensFluxC2)):#on cherche l'index du flux contenu ayant pour numéro newTeNum pour vérifier que le flux se trouve bien avant le flux chaud i 
                        if ensFluxC2[l].numero==ensFluxF2[m].newTeNum:
                            indexNewTeNum=l 
                    if indexNewTeNum>=i or k==j:"""
                    print("ensFluxF2[m].newTeNum : "+str(ensFluxF2[m].newTeNum))
                    print("ensFluxF2[m].numero : "+str(ensFluxF2[m].numero))
                    if ensFluxF2[m].newTe==ensFluxF2[m].Te or ensFluxF2[m].newTeNum==ensFluxC2[p].numero:
                        """print("ensFluxF2[m].CP"+str(ensFluxF2[m].CP))
                        print("min(ensFluxF2[m].Ts,TpincementF) : "+str(min(ensFluxF2[m].Ts,TpincementF)))
                        print("ensFluxF2[m].newTe : "+str(ensFluxF2[m].newTe))
                        print("ensFluxF2[m].Te : "+str(ensFluxF2[m].Te))
                        print(ensFluxF[m].chargeThE)"""
                        ensFluxF2[m].chargeThE=min(ensFluxF[m].chargeThE,(min(ensFluxF2[m].Ts,TpincementF)-ensFluxF2[m].Te)*ensFluxF2[m].CP)
                    else:
                        """print("ensFluxF2[m].CP"+str(ensFluxF2[m].CP))
                        print("min(ensFluxF2[m].Ts,TpincementF) : "+str(min(ensFluxF2[m].Ts,TpincementF)))
                        print("ensFluxF2[m].Te : "+str(ensFluxF2[m].Te))
                        print(ensFluxF[m].chargeThE)"""
                        ensFluxF2[m].chargeThE=min(ensFluxF[m].chargeThE,(min(ensFluxF2[m].Ts,TpincementF)-ensFluxF2[m].newTe)*ensFluxF2[m].CP)
                    #print("puiss Fluide FROId : " +str(ensFluxF2[m].chargeThE))
                    if ensFluxC2[p].chargeThE1!=0:#alors ThE1 est égale à b
                        print("2 puissE")
                        puissE1=min(ensFluxC2[p].chargeThE1,ensFluxF2[m].chargeThE)
                    else:
                        print("1 puissE")
                        puissE1=min(ensFluxC2[p].chargeThE,ensFluxF2[m].chargeThE)
                    if ensFluxF2[m].div==0:
                        CPbrF=ensFluxF2[m].CP
                    else:
                        CPbrF=puissE1*ensFluxF2[m].CP/ensFluxF2[m].b
                    if ensFluxC2[p].div==0:
                        CPbrC=ensFluxC2[p].CP
                    else:#si il s'agit d'un flux placé avant déjà divisé, alors son b aura été calculé
                        if puissE1==ensFluxC2[p].b:#car sinon la valeur de CPbrC est légèrement différent du CP
                            CPbrC=ensFluxC2[p].CP
                        else:
                            CPbrC=puissE1*ensFluxC2[p].CP/ensFluxC2[p].b
                    TeC=min(TpincementC,ensFluxC2[p].Te)#le but est que les fluides froids atteignent la température de pincementF. Et que le refroidissement des fluides chauds se fasse à la température la plus faible. 
                    TsF=min(TpincementF,ensFluxF2[m].Ts)
                    TsC=TeC-puissE1/CPbrC
                    TeF=TsF-puissE1/CPbrF
                    if ensFluxC[i].numero==1:
                        print("/oui")
                        print(ensFluxF2[m].numero)
                        print(ensFluxC2[p].numero)
                        print(ensFluxC2[p].b)
                        print(puissE1)
                        print(ensFluxF2[m].chargeThE)
                        print(TeC)
                        print(TsC)
                        print(TeF)
                        print(TsF)
                        print(CPbrF)
                        print(CPbrC)
                    if TeC>=(TsF+deltaTmin) and TsC>=TeF+deltaTmin  and (CPbrF<=round(CPbrC,3) or ensFluxF2[m].Ts<TpincementF):#on n'a pas besoin de simuler les échanges ayant lieu avec les fluides froids positionnés après le fluide froid en question car ils n'auront pas d'impact sur les échanges du fluide froid en question.:
                        print("echange possible")
                        ensFluxC2[p].chargeThE-=puissE1
                        ensFluxC2[p].puissE4+=puissE1
                        if (ensFluxC[p].verif!=0 or ensFluxC2[p].chargeThE1!=0) and p==i:
                            ensFluxC2[p].chargeThE1-=puissE1
                        ensFluxF2[m].chargeThE-=puissE1
                        if p==i:#si le flux respecte les règles on le retire de la liste sup
                            print("flux validé")
                            sup.remove(ensFluxF2[m].numero)
                            compt-=0.5
                            ensFluxC2[p].test1.append(ensFluxF2[m].numero)
                        if ensFluxC2[p].div==0:#Le flux divisé (ou pas) ne possède plus de branche non utilisée donc il faut que la température d'entrée soit changée
                            ensFluxC2[p].Te=TsC
                        else:#le flux divisé possède encore une (ou des) branche(s) non utilisée(s)
                            if ensFluxC2[p].div==0.5:#s'il s'agit de la dernière branche d'un flux divisé, il faut que la température d'entrée soit changée
                                ensFluxC2[p].div-=0.5
                                ensFluxC2[p].Te=TsC
                            else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                                ensFluxC2[p].div-=0.5
                        if ensFluxF2[m].div==0:
                            ensFluxF2[m].Ts=TeF
                        else:#si le fluide a été divisé, sa température d'entrée doit rester la même pour les autres branches de la division
                            if ensFluxF2[m].div==0.5:
                                ensFluxF2[m].div-=0.5
                                ensFluxF2[m].Ts=TeF
                                ensFluxF2[m].pinc="oui"
                            else:
                                ensFluxF2[m].div-=0.5
        
                    else:#prend en compte que l'échange peut-être inférieure à la charge Th d'un des flux (car sinon la condition deltaTmin n'est pas respectée)
                        #print("else")
                        #print("verif flux chaud :" +str(ensFluxC2[p].verif))
                        if ensFluxF2[m].Te<ensFluxC2[p].Te:#and ensFluxC2[p].verif==0 #on vérifie que verif est nul car sinon cela signifie que les températures du flux chauds ont déjà été modifiés pour s'adapter un flux. Si on les modifie à nouveau, les températures ne seront plus adaptées pour le premier flux.
                            #print("stop")
                            """print(ensFluxF2[m].numero)
                            print(ensFluxC2[p].numero)
                            print(ensFluxC2[p].chargeThE1)"""
                            if TeC<=TeF+deltaTmin:
                                b=b#inutile (permet juste de ne pas afficher print("PB ..."))
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
                                    TeF1=copy.deepcopy(TeF)
                                    print("froid Te :"+str(ensFluxF2[m].Te))
                                    TeF=ensFluxF2[m].Te#car sinon TeF est égal à la valeur calculé dans la 1ère boucle ; si newTe n'a pas été modifé, il est égale à Te sinon il est égale à la Te qu'aura ce flux froid quand il rencontrera ce flux chaud
                                    if ensFluxC2[p].verif!=0:#car si le flux a déjà échangé sa temp de sortie est déjà déterminé
                                        print("stop2")
                                        """print(TeC)
                                        print(ensFluxC2[p].CP)
                                        print(ensFluxC2[p].b)"""
                                        TsC=TeC-ensFluxC2[p].b/ensFluxC2[p].CP
                                    else:
                                        print("stop3")
                                        TsC=TeF+deltaTmin#comme la puissance échangé sera inférieure à la charge Th du flux chaud, sa température de sortie sera différente. 
                                    if TsC<ensFluxC2[p].Ts:
                                        TeF=TeF1
                                        TsC=TeF+deltaTmin
                                    TsF=min(ensFluxF2[m].Ts,TeC-deltaTmin)
                                    ensFluxF2[m].chargeThE1=(TsF-TeF)*ensFluxF2[m].CP
                                    if typeEch!="echE":#new boite Midrex False/False
                                        ensFluxF[j].chargeThE1=(TsF-TeF)*ensFluxF[j].CP
                                    print(ensFluxC2[p].chargeThE1)
                                    print(ensFluxF2[m].chargeThE1)
                                    puissE=min(ensFluxC2[p].chargeThE1,ensFluxF2[m].chargeThE1)
                                    if puissE==ensFluxC2[p].chargeThE1:
                                        TsF=TeF+puissE/ensFluxF2[m].CP
                                    if ensFluxC[i].numero==1:
                                        print("$")
                                        print(puissE)
                                        print(TeC)
                                        print(TsC)
                                        print(TeF)
                                        print(TsF)
                                        print(CPbrC)
                                    if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                                        print("échange1")
                                        ensFluxC2[p].chargeThE1-=puissE
                                        ensFluxF2[m].chargeThE-=puissE
                                        ensFluxC2[p].puissE3=puissE
                                        #print(ensFluxC2[p].puissE3)
                                        #if ensFluxF2[m].numero==10:
                                            #print(puissE)
                                            #print(ensFluxC2[p].chargeThE1)
                                        #ensFluxF[m].Ts=TeF on retire cette ligne car elle n'a plus d'intérêt dans ce cas car on amené le fluide froid de sa température d'entrée en une température inférieure à deltaTmin la température d'entrée du flux chaud
                                        if p==i:#si le flux respecte les règles on le retire de la liste sup
                                            if ensFluxC2[p].verif==0:
                                                #ensFluxC2[p].chargeThE1=ensFluxC2[p].chargeThE
                                                b=(TeC-TsC)*ensFluxC2[p].CP
                                                ensFluxC[p].verif+=1
                                                ensFluxC2[p].verif+=1
                                                print("verif +1")
                                            sup.remove(ensFluxF2[m].numero)
                                            compt-=0.5
                                            ensFluxC2[p].puissE4+=puissE
                                            ensFluxC2[p].test1.append(ensFluxF2[m].numero)
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
                                                ensFluxF2[m].Te=TsF
                                                ensFluxF[m].newTe=TsF
                                                ensFluxF[m].newTeNum=ensFluxC2[p].numero
                                                #print("ensFluxF[m].newTe=TsF   ::: "+str(ensFluxF[m].newTe))
                                            else:
                                                ensFluxF2[m].div-=0.5 
                                        else:
                                            ensFluxF2[m].Te=TsF
                                            ensFluxF[m].newTe=TsF
                                            ensFluxF[m].newTeNum=ensFluxC2[p].numero
                                if TeC<(TsF+deltaTmin): #hypothèse : "la chargeTh minimale est celle du fluide froid". On va réduire la température de sortie du flux froid. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                                    #print("stop2")
                                    #TsF=TeC-deltaTmin
                                    if TeF<ensFluxF2[m].Te:
                                        TeF=ensFluxF2[m].Te
                                    if ensFluxC2[p].verif!=0:#car si le flux a déjà échangé sa temp de sortie est déjà déterminé
                                        TsC=TeC-ensFluxC2[p].b/ensFluxC2[p].CP
                                    else:
                                        TsC=TeF+deltaTmin#comme la puissance échangé sera inférieure à la charge Th du flux chaud, sa température de sortie sera différente.                                 
                                    TsF=min(ensFluxF2[m].Ts,TeC-deltaTmin)
                                    ensFluxF2[m].chargeThE1=(TsF-TeF)*ensFluxF2[m].CP
                                    if typeEch!="echE" and m==j:#new boite Midrex False/False
                                        ensFluxF[j].chargeThE1=(TsF-TeF)*ensFluxF[j].CP
                                    #print("ensFluxF[j].chargeThE1 : "+str(ensFluxF[j].chargeThE1))
                                    puissE=min(ensFluxC2[p].chargeThE1,ensFluxF2[m].chargeThE1)
                                    #ensFluxF2[m].chargeThE=(TsF-TeF)*ensFluxF2[m].CP
                                    #puissE=min(ensFluxC2[p].chargeThE1,ensFluxF2[m].chargeThE)#minimum entre les puissances que peuvent fournir les flux avec leurs nouvelles températures
                                    CPbrC=puissE*ensFluxC2[p].CP/ensFluxC2[p].b
                                    """print(ensFluxC2[p].numero)
                                    print(ensFluxF2[m].numero)
                                    print(ensFluxC2[p].b)
                                    print(CPbrC)
                                    print(puissE)
                                    print(TeC)
                                    print(TsC)
                                    print(TeF)
                                    print(TsF)"""
                                    #print(CPbrC)
                                    if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                                        print("échange2")
                                        ensFluxC2[p].chargeThE1-=puissE
                                        ensFluxF2[m].chargeThE-=puissE
                                        ensFluxC2[p].puissE3=puissE
                                        if p==i:#si le flux respecte les règles on le retire de la liste sup
                                            if ensFluxC2[p].verif==0:
                                                #ensFluxC2[p].chargeThE1=ensFluxC2[p].chargeThE
                                                b=(TeC-TsC)*ensFluxC2[p].CP
                                                print("verif +1")
                                                ensFluxC[p].verif+=1
                                                ensFluxC2[p].verif+=1
                                            sup.remove(ensFluxF2[m].numero)
                                            compt-=0.5
                                            ensFluxC2[p].puissE4+=puissE
                                            ensFluxC2[p].test1.append(ensFluxF2[m].numero)
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
                                                ensFluxF2[m].Te=TsF
                                                ensFluxF[m].newTe=TsF
                                                ensFluxF[m].newTeNum=ensFluxC2[p].numero
                                                ensFluxF2[m].pinc="oui"
                                            else:
                                                ensFluxF2[m].div-=0.5
                                        else:
                                            ensFluxF2[m].Te=TsF
                                            ensFluxF[m].newTe=TsF
                                            ensFluxF[m].newTeNum=ensFluxC2[p].numero

        if compt==0:#la même boucle que au-dessus mais permet de vérifier aussi cette condition à la fin des deux boucles
            cond="oui"
            annul="non"
            annuldiv="non"
            ensFluxC[i].test=test
            #if ensFluxF[j].numero==5:
            #print("stop2")
            return(b,annul,annuldiv,m,test,CP)                 

        """print(compt1)
        print(ensFluxC[i].div*2)"""
        if len(ensFluxF1)-len(sup)<ensFluxC[i].div*2 or compt1<ensFluxC[i].div*2:
            if len(ensFluxC2[i].test1)==0:
                b=1
                print("1 Aucun flux n'a été trouvé pour échanger avec le flux divisé c"+str(ensFluxC[i].numero))
                annul="oui"
                ensFluxC[i].test=test
                annuldiv="oui"
                return(b,annul,annuldiv,m,test,CP)
            else:#si toute les branches n'ont pas pu être satisfaite mais que le flux chaud peut quand même échanger avec un flux froid
                print("boucle TESSST")
                print(ensFluxC2[i].test1)
                print(ensFluxC2[i].puissE4)
                b=ensFluxC2[i].puissE4
                ensFluxC[i].test=ensFluxC2[i].test1
                if typeEch!="echE1":#car pour le cas contraire, on a pas accés à ensFluxC mais à ensFluxC1
                    print("if")
                    print("ensFluxC2[i].div : "+str(ensFluxC2[i].div))
                    CPdiv=CP[i]#on ne va pas diviser le flux actuel alors qu'on cherche à annuler sa division
                    CP[i]=0
                    CPcompt=0
                    #print("boucle chargeThE1==0 -- div flux chaud : "+str(ensFluxC2[p].div))
                    if ensFluxC[i].div-ensFluxC2[i].div==0.5:#s'il n'y a eu qu'un échange alors on doit amener son div à 0
                        ensFluxC[i].div=0
                        ensFluxC[i].verif=0
                        ensFluxC[i].puissModif="oui"
                        plusEch="non"
                    else:
                        plusEch="oui"
                    while ensFluxC2[i].div>0:#boucle différente de celle lorsque annuldiv=="oui" car on ne supprimer les branches où l'échange n'aura pas lieu (et non toutes les branches)
                        print("2On annule la division du flux c"+str(ensFluxC2[i].numero))#car une des branches des flux échange toute sa chaleur
                        CPcompt+=1
                        ensFluxC2[i].div-=0.5
                        if plusEch=="oui":
                            ensFluxC[i].div-=0.5###### vérifier qu'il est correct de le laisser en sachant que : boucle différente de celle lorsque annuldiv=="oui" car on ne supprimer les branches où l'échange n'aura pas lieu (et non toutes les branches)
                        #print(test)
                        #if len(test)!=0:
                        #test.remove(test[len(test)-1])#retire les flux qui n'ont pas pu échanger avec le flux chaud car celui-ci était déjà satisfait. On commence par les flux 
                        #print(test)
                        ind=CP.index(max(CP))
                        print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
                        CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                        if ensFluxC[ind].div==0:
                            ensFluxC[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                        else:
                            ensFluxC[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                    ensFluxC[i].test=ensFluxC2[i].test1#normalement correct mais pas encore testé
                    CP[i]=CPdiv*2**CPcompt#on autorise à nouveau la disivion de ce flux - ** = puissance
                    annul="non"
                    annuldiv="non"
                    ensFluxC[i].b1=0
                    #print("stop")
                    #print(CP)
                    return(b,annul,annuldiv,m,test,CP)
                else:#vérifier utilité de ce else
                    print("else")
                    annul="non"
                    annuldiv="oui"
                    ensFluxC[i].b1=0
                    if ensFluxC2[i].div==ensFluxC[i].div-0.5:#car cela signifie que le flux a échangé qu'une seule fois et donc il n'y a pas d'intérêt d'avoir un verif >0
                        ensFluxC[i].verif=0
                    return(b,annul,annuldiv,m,test,CP)


                







def divE1(ensFluxC3,ensFluxF,j,TpincementC,TpincementF,deltaTmin,CP1,Reseau,ensFluxCinit,ensFluxFinit,listeCouple):#division d'un fluide froid en-dessous du pincement    
    ensFluxC2=[]
    ensFluxC2=copy.deepcopy(ensFluxC3)
    ensFluxC=copy.deepcopy(ensFluxC3)
    cond="a"
    CP=copy.deepcopy(CP1)
    annul="non"#si le flux chaud divisé ne trouve pas de fluide froid, alors on ne le fait échanger avec aucun flux
    ech=0
    affich=0
    chargeThEfr=copy.deepcopy(ensFluxF[j].chargeThE)
    while cond!="ok":#la boucle s'arrête une fois qu'on a trouvé autant de flux que de branches pour échanger
        print("-----------")
        print("len(ensFluxC2) : "+str( len(ensFluxC2)))
        a=0
        b=1
        compt=0
        compt2=0
        sup=[]
        compt3=ensFluxF[j].div#donne le div du flux froid
        ensFluxF[j].chargeThE=chargeThEfr#car on modifie sa valeur à chaque boucle
        #nbBrF=compt3*2#donne le nb de branche du flux froid
        if ensFluxF[j].echChargeTh=="non":#on cherche les flux avec la plus grande Te pour pouvoir échanger un maximum avec le flux froid. On fait cela que quand echChargeTh="non" car sinon cela n'a pas d'intérêt comme on va tenter d'échanger toute la chargeTh du fluid froid
            ensFluxC4=[]
            maxTeTab1=[]
            maxTeTab2=[]
            chargeThCTab=[]
            ensFluxC4=copy.deepcopy(ensFluxC2)
            while compt2<compt3:
                maxTeTab=[]
                print("compt2 : "+str(compt2))
                for h in range(len(ensFluxC4)):
                    maxTeTab.append(min(ensFluxC4[h].Te,TpincementC))#liste qui rassemble les Te des flux chauds
                maxTe=maxTeTab.index(max(maxTeTab))
                maxTeTab2.append(max(maxTeTab))#permet de connaitre les Te max
                ensFluxC4[maxTe].Te=0
                chargeThCTab.append(ensFluxC4[h].chargeThE)
                maxTeTab1.append(ensFluxC4[maxTe].numero)#permettra de regarder en-dessous si le flux chaud en question fait partie des flux chauds avec la plus grande température max
                compt2+=0.5
            tempMin=min(maxTeTab2)-deltaTmin#permettra de calculer le b du flux froid
            print("tempMin : "+str(tempMin))
            print("maxTeTab2 : "+str(maxTeTab2))

        if ensFluxF[j].chargeThE==0:#car sinon on ne va pas rentrer dans la boucle while et cela va poser problème pour la suite de la fonction (car certaine liste et variables ne seront pas crées)
            print("ensFluxF[j].chargeThE==0")
            annul="oui"
            b=1#pour éviter le message d'erreur float division by zero
            return(b,annul)

        

        while a<ensFluxF[j].chargeThE:#implique que le b sera toujours égale à ensFluxF[j].chargeThE
            print("compt4: "+str(compt3))
            a=0
            compt=0
            ensFluxC1=[]
            puissA=[]
            fluxSelec=[]#contient le numéro des flux sélectionnés pour échanger avec le flux froid
            chargeThFluxSelec=[]#contient la charge Th des flux sélectionnés pour échanger avec le flux froid
            
            if ensFluxF[j].echChargeTh=="oui":#on supprime les flux qui ne peuvent pas satisfaire totalement le fluide froid (car le Te est trop basse)
                for n in range(len(ensFluxC)):
                    if ensFluxC[n].Te<min(TpincementF,ensFluxF[j].Ts)+deltaTmin: 
                        for l in range(len(ensFluxC2)):
                            if ensFluxC2[l].numero==ensFluxC[n].numero:
                                ensFluxC2.remove(ensFluxC2[l])
                                break
            
            ancienCP=0
            comptNb=0
            tempSortF=0
            if ensFluxF[j].echChargeTh=="non":#on vérifie que la charge qui sera échangée avec le flux chaud ne dépasse pas sa chargeThe car sinon cela veut dire que la valeur de b est trop grande
                for d in range(len(ensFluxC2)):
                    if ensFluxC2[d].numero in maxTeTab1:
                        print("ensFluxC2[d].numero : "+str(ensFluxC2[d].numero))
                        if comptNb!=len(maxTeTab1):
                            puissEch=ensFluxC2[d].CP*(tempMin - ensFluxF[j].Te)
                            ancienCP+=ensFluxC2[d].CP
                            comptNb+=1
                        else:
                            puissEch=(ensFluxF[j].CP-ancienCP)*(tempMin - ensFluxF[j].Te)
                        if puissEch>ensFluxC2[d].chargeThE:
                            if comptNb!=len(maxTeTab1):
                                print("stop1")
                                print(ensFluxF[j].Te)
                                print(puissEch)
                                print(ensFluxC2[d].chargeThE)
                                print(ensFluxC2[d].CP)
                                tempSortF=ensFluxF[j].Te+ensFluxC2[d].chargeThE/ensFluxC2[d].CP
                            else:
                                print("stop2")
                                tempSortF=ensFluxF[j].Te+ensFluxC2[d].chargeThE/(ensFluxF[j].CP-ancienCP)
                            ensFluxF[j].b=ensFluxF[j].CP*(tempSortF - ensFluxF[j].Te)
                if tempSortF!=0:
                    print("tempSortF : "+str(tempSortF))
                    tempMin=tempSortF
                ensFluxF[j].b=ensFluxF[j].CP*(tempMin - ensFluxF[j].Te)
                ensFluxF[j].tempMin=tempMin#servira dans la suite 
            
            print("ensFluxF[j].b : "+str(ensFluxF[j].b))







            ancienCP=0
            for m in range(len(ensFluxC2)):
                #print("ensFluxC2[m].numero"+str(ensFluxC2[m].numero))
                if (ensFluxF[j].echChargeTh=="oui" and compt<compt3 and ensFluxC2[m].chargeThE!=0 and ensFluxC2[m].numero not in sup) or (ensFluxF[j].echChargeTh=="non" and  ensFluxC2[m].numero in maxTeTab1 and compt<compt3 and ensFluxC2[m].chargeThE!=0 and ensFluxC2[m].numero not in sup) :#and (ensFluxC2[m].numero in maxTeTab1)#on choisit arbitrairement les 1er flux chauds de la liste
                    print("min(TpincementC,ensFluxC2[m].Te)-deltaTmin : "+str(min(TpincementC,ensFluxC2[m].Te)-deltaTmin))
                    puissA1=ensFluxC2[m].CP*(min(TpincementF,ensFluxF[j].Ts,min(TpincementC,ensFluxC2[m].Te)-deltaTmin)-ensFluxF[j].Te)#on égalise le CP du flux chaud et froid pour que l'échange soit possible
                    if ensFluxF[j].echChargeTh=="non":
                        if compt3-compt!=0.5:
                            CPbrF=ensFluxC2[m].CP
                            ancienCP+=CPbrF#permettra de connaître la valeur des autres branches lors de l'échange avec la dernière branche
                        else:
                            CPbrF=ensFluxF[j].CP-ancienCP
                        print(CPbrF)
                        print(min(TpincementF,ensFluxF[j].Ts,min(TpincementC,ensFluxC2[m].Te)-deltaTmin))
                        puissA1=CPbrF*(min(TpincementF,ensFluxF[j].Ts,min(TpincementC,ensFluxC2[m].Te)-deltaTmin,tempMin)-ensFluxF[j].Te)#on égalise le CP du flux chaud et froid pour que l'échange soit possible
                        print("puissA1 : "+str(puissA1))
                        #puissA2=ensFluxC2[m].CP*(min(TpincementC,ensFluxC2[m].Te)-puissA1/ensFluxC2[m].CP)# à revoir car si flux divisé, ce sera CPbrC ; et puissA1 n'est pas correct car il se base sur .CP du flux froid aulieu de CPbrF
                        #print("puissA2 : "+str(puissA2))
                    print("ensFluxC2[m].chargeThE : "+str(ensFluxC2[m].chargeThE))
                    print("ensFluxF[j].chargeThE : "+str(ensFluxF[j].chargeThE))
                    print("puissA1 : "+str(puissA1))
                    print(min(TpincementC,ensFluxC2[m].Te))
                    if ensFluxF[j].echChargeTh=="non":
                        print("Ajouté à a : "+str(min(ensFluxC2[m].chargeThE,ensFluxF[j].chargeThE,puissA1)))
                        puissA.append(min(ensFluxC2[m].chargeThE,ensFluxF[j].chargeThE,puissA1))#,puissA2
                        a+=min(ensFluxC2[m].chargeThE,ensFluxF[j].chargeThE,puissA1)#,puissA1,puissA2 ; on ajoute la valeur de la puissance échangée à "a"
                    else:
                        puissA.append(min(ensFluxC2[m].chargeThE,ensFluxF[j].chargeThE,puissA1))#,puissA1
                        a+=min(ensFluxC2[m].chargeThE,ensFluxF[j].chargeThE,puissA1)#,puissA1 ; on ajoute la valeur de la puissance échangée à "a"
                    print("a : "+str(a))
                    ensFluxC1.append(ensFluxC2[m])#comprend les flux qui vont échanger avec le flux divisé
                    print("Flux ajouté à ensFluxC1 : "+str(ensFluxC2[m].numero))
                    compt+=0.5
                    fluxSelec.append(ensFluxC2[m].numero)
                    chargeThFluxSelec.append(ensFluxC2[m].chargeThE)
                    #print("numéro flux chaud"+str(ensFluxC2[m].numero))

            if ensFluxF[j].echChargeTh=="oui":
                ensFluxF[j].b=min(a,ensFluxF[j].chargeThE)
            compt1=0

            if len(ensFluxC2)==0 or a<=0 or b<=0 or len(ensFluxC1)==0:
                print("len(ensFluxC2)==0 or a<=0 or b<=0 or len(ensFluxC1)==0")
                annul="oui"
                b=1#pour éviter le message d'erreur float division by zero
                return(b,annul)

            if ensFluxF[j].echChargeTh=="non":
                break


            """print("a : "+str(a))
            print("ensFluxF[j].chargeThE : "+str(ensFluxF[j].chargeThE))
            print("ensFluxF[j].b : "+str(ensFluxF[j].b))"""
            if a<ensFluxF[j].chargeThE:#nous allons supprimer le flux sélectionnés précédemment qui a la chargeThE la plus basse (valable que si on échange toute la chargeTh du fluide froid)
                indMin=chargeThFluxSelec.index(min(chargeThFluxSelec))#contient l'index du flux avec le minimum de chargeThE
                """print(chargeThFluxSelec)
                print(fluxSelec)
                print(indMin)
                print(fluxSelec[indMin])"""
                p=0
                for k in range(len(ensFluxC2)):
                    """print("k : "+str(k))
                    print("ensFluxC2[k].numero : "+str(ensFluxC2[k].numero))"""
                    if ensFluxC2[k].numero==fluxSelec[indMin]:
                        p=k
                ensFluxC2.remove(ensFluxC2[p])
            
        compt4=0
        ancienCP=0
        print("entrée dans boucle !:!:!")
        print("ensFluxF[j].Te : "+str(ensFluxF[j].Te))
        for p in range(len(ensFluxC1)):#on vérifie que les flux sélectionnés respectent le deltaTmin
            puissE=min(puissA[p],ensFluxF[j].chargeThE)#car pour le dernier échange, la puissance échangée doit permettre de finir de satisfaire le flux froid
            
            if ensFluxF[j].echChargeTh=="non":
                if compt3-compt4!=0.5:#permet de savoir s'il sagit de la dernière branche ou pas
                    CPbrF=ensFluxC1[p].CP
                    ancienCP+=CPbrF#permettra de connaître la valeur des autres branches lors de l'échange avec la dernière branche
                else:
                    CPbrF=ensFluxF[j].CP-ancienCP
            else:
                CPbrF=puissE*ensFluxF[j].CP/ensFluxF[j].b
            print(ensFluxC1[p].numero)
            print(ensFluxF[j].chargeThE)
            print(puissA[p])
            print(puissE)
            print(ensFluxF[j].b)
            print(CPbrF)
            print(ensFluxC1[p].CP)
            if CPbrF<=ensFluxC1[p].CP and ensFluxC1[p].chargeThE!=0 and ensFluxF[j].chargeThE!=0:
                for k in range(len(ensFluxC)):
                    if ensFluxC1[p].numero==ensFluxC[k].numero:#car les flux ne sont pas disposés de la même manière dans les deux listes
                        ensFluxC1[p].div=ensFluxC[k].div#car on modifie les div lorsqu'on annule des flux
                ensFluxC1[p].verif=0
                if ensFluxC1[p].chargeThE!=0 and ensFluxF[j].chargeThE!=0:#si les fluides ne sont pas satisfait et le fluide froid possède encore des branches non utilisées (on considère un échange par branche)
                    if ensFluxC1[p].div==0:#si toutes les branches ont été utilisées, on reprend le CP du fluide avant division
                        CPbrC=ensFluxC1[p].CP
                    else:#sinon on pondère le CP avec la puissance du flux complémentaire
                        if ensFluxC1[p].ech=="non":
                            div=[]
                            for h in range(len(ensFluxC1)):#on sauvegarde la valeur des div avant division
                                div.append(ensFluxC1[h].div)
                            print("--  Entrée divE dans divE1")
                            print("ensFluxC1[p].numero"+str(ensFluxC1[p].numero))
                            print("ensFluxF[j].chargeThE : "+str(ensFluxF[j].chargeThE))
                            ensFluxC1[p].b,annul,annuldiv,n,test,CP=Division.divE(ensFluxC,ensFluxF,p,j,TpincementC,TpincementF,deltaTmin,ech,CP,"echE1-divE1",Reseau,ensFluxCinit,ensFluxFinit,listeCouple)#le but est de simuler les prochains échanges avec le flux chaud divisé pour connaître la valeur de son b. Mais il ne faut pas modifier les attributs "test"... car on n'est pas dans la boucle principale ; on simule avec ensFluxC3 pour pouvoir connaître le b en prennant en compte tous les flux chauds présents sous le pincement
                            print("--  Sortie divE dans divE1")
                            print(CPbrF)
                            CPdiv=CP[p]#on ne va pas diviser le flux actuel alors qu'on cherche à annuler sa division
                            CPdiv1=[]
                            CPdiv1=copy.deepcopy(CP)
                            #if annul=="non":
                                #CP[p]=0#permet de ne pas diviser un flux dont toutes ses branches n'ont pas fini d'avoir échangé (sinon problème au niveau des .div)
                            if annuldiv=="oui":
                                CP[p]=0
                                CPcompt=0
                                div=[]
                                for h in range(len(ensFluxC)):#on sauvegarde la valeur des div avant division
                                    div.append(ensFluxC[h].div)
                                #print(div)
                                while ensFluxC1[p].div!=0:
                                    verif=0
                                    for h in range(len(CP)):
                                        verif+=CP[h]
                                    if verif==0:#si verif=0 alors tous les flux sont déjà satisfaits
                                        #print("3Tous les flux sont satisfaits. Division d'un flux chaud impossible")
                                        for h in range(len(ensFluxC)):#sur ensFluxC car ensFluxC1 et C2 n'ont pas la même taille que la liste div (puis on égalise les div entre ensFluxC1 et ensFluxC à chaque itération)
                                            ensFluxC[h].div=div[h]
                                        CP=CPdiv1
                                        #ensFluxC2.remove(ensFluxC1[p])
                                        break#permet de stopper la boucle while annul=="oui"
                                    CPcompt+=1
                                    if ensFluxC1[p].div==1:#on ne modifie pas C2 car l'annulation de la division de ce flux n'a pas d'importance pour la suite comme ce flux ne sera plus traité après (car on passe au k suivant)
                                        ensFluxC1[p].div=0
                                    else:
                                        ensFluxC1[p].div-=0.5
                                    #if ensFluxF[j].numero==5:
                                    #print("On annule la division du flux c"+str(ensFluxC1[p].numero))#car une des branches des flux échange toute sa chaleur
                                    #division d'un nouveau flux pour toujours respecter la règle des flux
                                    ind=CP.index(max(CP))
                                    #if ensFluxF[j].numero==5:
                                    #print("Le fluide chaud c"+str(ensFluxC[ind].numero)+" doit être divisé en deux.")
                                    CP[ind]=CP[ind]/2#on suppose que le CP est divisé en 2 lorsque le fluide est divisé en 2
                                    if ensFluxC[ind].div==0:#on utilise ensFluxC car sinon les indices de CP et ensFluxC2 ne correspondent pas toujours (car on supprime des flux de ensFluxC2)
                                        ensFluxC[ind].div+=1#on ajoute 1 branche (+0,5). En plus de la branche de départ(+0,5), cela fait deux branches, soit 0,5+0,5=1
                                    else:
                                        ensFluxC[ind].div+=0.5#on ajoute une branche en plus (+0,5), les autres branches ont déjà été comptabillisées
                                    for g in range(len(ensFluxC1)):#car sinon on modifie uniquement ensFluxC
                                        if ensFluxC1[g].numero==ensFluxC[ind].numero:
                                            ensFluxC1[g].div=ensFluxC[ind].div
                                if verif!=0:
                                    CP[p]=CPdiv*2**CPcompt#on lui réattribue sa valeur moins les branches retirées (annulées)
                                else:
                                    CP[p]=CPdiv
                                CPbrC=ensFluxC1[p].CP
                                div=[]
                                for h in range(len(ensFluxC)):
                                    div.append(ensFluxC[h].div)
                                """if ensFluxF[j].numero==5:
                                    print(CP)
                                    print(div)"""
                            else:
                                CPbrC=puissE*ensFluxC1[p].CP/ensFluxC1[p].b
                        else:
                            CPbrC=puissE*ensFluxC1[p].CP/ensFluxC1[p].b
                        
                TeC=min(TpincementC,ensFluxC1[p].Te)#le but est que les fluides froids atteignent la température de pincementF. Et que le refroidissement des fluides chauds se fasse à la température la plus faible. 
                TsC=TeC-puissE/CPbrC
                if ensFluxF[j].echChargeTh=="non":
                    TeF=ensFluxF[j].Te
                    TsF=TeF+puissE/CPbrF
                else:
                    TsF=min(TpincementF,ensFluxF[j].Ts)
                    TeF=TsF-puissE/CPbrF
                #print(ensFluxF[j].numero)
                #if ensFluxF[j].numero==5:
                affich+=1
                print("/")
                print(ensFluxC1[p].numero)
                print(puissE)
                print(ensFluxC1[p].b)
                print(ensFluxF[j].b)
                print(ensFluxF[j].CP)
                print(CPbrF)
                print(TeC)
                print(TsC)
                print(TeF)
                print(TsF)
                print(annul)
                print(CPbrC)
                print(CPbrF)
                print("/")
                if annul!="oui" and (CPbrC>=CPbrF or ensFluxF[j].Ts<TpincementF):
                    #print("hello1")
                    if TeC>=(TsF+deltaTmin) and TsC>=TeF+deltaTmin:
                        print("echange1")
                        #print("chargeThE-froid : "+str(ensFluxF[j].chargeThE))
                        ensFluxF[j].chargeThE-=puissE
                        ensFluxC1[p].chargeThE-=puissE
                        ensFluxC[p].chargeThE-=puissE#car c'est lui qu'on met dans l'appel de la fct divE
                        #print(puissE)
                        #print("chargeThE-froid : "+str(ensFluxF[j].chargeThE))
                        if ensFluxC1[p].chargeThE==0:
                            for i in range(len(ensFluxC)):
                                if ensFluxC1[p].numero==ensFluxC[i].numero:
                                    CP[i]=0
                        compt1+=1
                        compt4+=0.5
                    else:
                        #print("stop2")
                        if TeC<=TeF+deltaTmin:
                            print("TeC<=TeF+deltaTmin")
                            for f in range(len(ensFluxC2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
                                if ensFluxC2[f].numero==ensFluxC1[p].numero:
                                    ensFluxC2.remove(ensFluxC2[f])
                                    break
                        else:
                            if TeC<(TsF+deltaTmin):#hypothèse : "la chargeTh minimale est celle du fluide froid". On va réduire la température de sortie du flux froid. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                                """TsF=min(TeC-deltaTmin,ensFluxF[j].Ts,TpincementF)#présent avant
                                puissE=(TsF-TeF)*CPbrF#*ensFluxF[j].CP à la place de CPbrF
                                TsC=max(TeC-puissE/CPbrC,TeF+deltaTmin,ensFluxC1[p].Ts)"""
                                if ensFluxF[j].echChargeTh=="non":
                                    TsF=ensFluxF[j].tempMin
                                else:
                                    TsF=TeC-deltaTmin
                                print("ensFluxF[j].Te : "+str(ensFluxF[j].Te))
                                if TeF>ensFluxF[j].Te:
                                    TeF=ensFluxF[j].Te
                                
                                puissE=min(ensFluxC1[p].chargeThE,(TsF-TeF)*CPbrF)
                                print(ensFluxC1[p].chargeThE)
                                print(TsF)
                                print(TeF)
                                print(CPbrF)
                                print((TsF-TeF)*CPbrF)
                                TsC=TeC-puissE/CPbrC
                                if puissE==ensFluxC1[p].chargeThE and puissE!=(TsF-TeF)*CPbrF:#cela voudra dire qu'imposer une TsF à deltaTmin de l'entrée du fluide chaud implique que le fluide chaud ne peut pas fournir la chaleur demandé par le fluide froid. Ainsi, si le fluide chaud ne peut pas fournir plus, on recalcule quelle T va atteindre le fluide froid avec cette puissance ; puissE!=(TsF-TeF)*CPbrF : car si les puissE est égale à la charge Th du flux chaux mais aussi à (TsF-TeF)*CPbrF alors le fluide froid pourra absorber cette puissance et il ne sera pas nécessaire de modifier ces températures
                                    print("stop!!")
                                    if TeF>TsC-deltaTmin:#si la condition du deltaTmin n'est pas respectée
                                        TeF=TsC-deltaTmin
                                    TsF=TeF+puissE/CPbrF
                                print("stop2")
                                print(puissE)
                                print(TeC)
                                print(TsC)
                                print(TeF)
                                print(TsF)
                                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                                    print("echange2")
                                    ensFluxF[j].chargeThE-=puissE
                                    print("ensFluxC1[p].numero : "+str(ensFluxC1[p].numero))
                                    print("ensFluxC[p].numero : "+str(ensFluxC[p].numero))
                                    ensFluxC1[p].chargeThE-=puissE
                                    ensFluxC[p].chargeThE-=puissE#car c'est lui qu'on met dans l'appel de la fct divE
                                    if ensFluxC1[p].chargeThE==0:
                                        for i in range(len(ensFluxC)):
                                            if ensFluxC1[p].numero==ensFluxC[i].numero:
                                                CP[i]=0
                                    #print(puissE)
                                    #print("chargeThE-froid : "+str(ensFluxF[j].chargeThE))
                                    compt1+=1
                                    compt4+=0.5
                                else:
                                    for f in range(len(ensFluxC2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
                                        if ensFluxC2[f].numero==ensFluxC1[p].numero:
                                            ensFluxC2.remove(ensFluxC2[f])
                                            break
                            else:# / hypothèse : la chargeTh minimale est celle du fluide froid / on va augmenter la température de sortie du fluide chaud. Après échange, la température d'entrée du fluide sera modifié et non sa température de sortie (qui reste le min entre TpincementF et ensFluxF[j].Ts)
                                TsC=(max(TeF+deltaTmin,ensFluxC1[p].Ts))
                                puissE=(TeC-TsC)*CPbrC
                                TsF=min(TeF+puissE/ensFluxF[j].CP,TeC-deltaTmin,ensFluxF[j].Ts,TpincementF)
                                print("stop3")
                                if TeC>=(TsF+deltaTmin) and TsC>=(TeF+deltaTmin) and TsC<TeC and TsF>TeF:#on vérifie que la sortie du fluide froid est bien inférieure à l'entrée du fluide chaud et qu'il y a un écart de deltaTmin entre les deux ; et que la sortie du fluide chaud est bien supérieure à l'entrée du fluide froid et qu'il y a un écart de deltaTmin entre les deux
                                    print("echange3")
                                    ensFluxF[j].chargeThE-=puissE
                                    ensFluxC1[p].chargeThE-=puissE
                                    ensFluxC[p].chargeThE-=puissE#car c'est lui qu'on met dans l'appel de la fct divE
                                    #print("chargeThE-froid : "+str(ensFluxF[j].chargeThE))
                                    if ensFluxC1[p].chargeThE==0:
                                        for i in range(len(ensFluxC)):
                                            if ensFluxC1[p].numero==ensFluxC[i].numero:
                                                CP[i]=0
                                    compt1+=1
                                    compt4+=0.5
                                else:
                                    for f in range(len(ensFluxC2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
                                        if ensFluxC2[f].numero==ensFluxC1[p].numero:
                                            ensFluxC2.remove(ensFluxC2[f])
                                            break
                else:
                    for f in range(len(ensFluxC2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
                        if ensFluxC2[f].numero==ensFluxC1[p].numero:
                            ensFluxC2.remove(ensFluxC2[f])
                            break               
            else:
                for f in range(len(ensFluxC2)):#boucle nécessaire car dans le while au-dessus on a réduit la taille de ensFluxC2
                    if ensFluxC2[f].numero==ensFluxC1[p].numero:
                        ensFluxC2.remove(ensFluxC2[f])
                        break
        if compt1==compt3*2:#si le deltaTmin est respecté pour chaque flux on sort de la boucle
            cond="ok"
            ensFluxF[j].test=fluxSelec
            return(ensFluxF[j].b,annul)#on connait maitenant le dénominateur de CPbrF
        if len(ensFluxC2)<ensFluxF[j].div*2 or len(ensFluxC1)==0:
            if ensFluxF[j].numero!=10 and ensFluxF[j].numero!=11 and ensFluxF[j].numero!=7 and ensFluxF[j].numero!=8 and ensFluxF[j].numero!=9 and ensFluxF[j].numero!=3 and ensFluxF[j].numero!=5:
                print("Aucun flux n'a été trouvé pour échanger avec le flux divisé f"+str(ensFluxF[j].numero))
            #ensFluxF[j].div=0#pour annuler la division du flux (car aucun flux ne peux échanger avec)
            annul="oui"
            b=1#pour éviter le message d'erreur float division by zero
            return(b,annul)


                    



        
