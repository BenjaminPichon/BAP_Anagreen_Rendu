# -*- coding: utf-8 -*-
"""
Created on Tue May 28 10:33:34 2019

@author: abonicel
"""

import warnings
import numpy as np

from classes import utilite as uti, piping, Pompe
from couts import Cost

from predimensionnement import Fonctions as alg


#warnings.filterwarnings("ignore")

# Remarque importante les positions sont bonnes il y a des mofis à apporter sur la prise en 
# compte des utilités
# Pour les positions c'est normal que les xFinEch et yFinEch, dans le cas de sous flux qui ne
# sont pas utilités, ne correspondent pas au xFin et yFin du flux référence (calcul fait dans piping)
# On ne considère pas les limites de températures et autres pour le choix des échangeurs

def Predimensionnement(objReseau,r_echelle,m,n):
    # Fonction donnant l'entiereté du dimensionnement avec le calcul des KPI
    
    print("Bienvenue sur l'outil ANAGREEN, le calcul commence\n")
    
    # Démarrage du chronomètre
#    debut=time.time()
    
    # liste donnant seulement les sous flux chaud
    ssFluxChaud=alg.tri(alg.tmpchaud(objReseau.listeSsFlux))
    # liste donnant seulement les sous flux froid
    ssFluxFroid=alg.tri(alg.tmpfroid(objReseau.listeSsFlux))
        
    # on va travailler avec les sous flux chaud pour obtenir toutes les positions
    print("On calcule les positions des sous flux chaud + utilite froide et des sous flux froid...")
    # on parcourt la liste dans l'ordre pusiqu'elle est triée 
    for ssfluxchaud in ssFluxChaud:
        
        # on gère le fait que le sous flux peut ne peut échanger mais juste passer par une utilité dans ce cas on fait l'hypothèse que l'utilité est ponctuelle et induit aucune perte de charge
        if not ssfluxchaud.utilite:
            # on selectionne le couple correspondant au sous flux chaud
            couple=alg.selection_couple(objReseau.listeCouple,ssfluxchaud)
            # on trouve le ssflux froid du couple
            ssFluxF1=alg.selection(ssFluxFroid,couple.ssFluxF)
            
            # Dans le cas de la divison on veille à avoir le bon x et y de début pour le flux froid
            if ssFluxF1.estDivise:
                # on cherche alors le sous flux étant le premier à être diviser il sera la référence
                ssflux_base_froid=alg.basedivision(ssFluxFroid,ssFluxF1.refFlux)
                # si le sous flux de référence est différent du sous flux étudié
                if ssflux_base_froid.pas_egal(ssFluxF1):
                    # on actualise la valeur du début à celle du sous flux de base
                    ssFluxF1.x,ssFluxF1.y=ssflux_base_froid.x,ssflux_base_froid.y          
            
            # Dans le cas de la divison on veille à avoir le bon x et y de début pour le flux chaud
            if ssfluxchaud.estDivise:
                # on cherche alors le sous flux étant le premier à être diviser il sera la référence
                ssflux_base_chaud=alg.basedivision(ssFluxChaud,ssfluxchaud.refFlux)
                # si le sous flux de référence est différent du sous flux étudié
                if ssflux_base_chaud.pas_egal(ssFluxF1):
                    # on actualise la valeur du début à celle du sous flux de base
                    ssfluxchaud.x,ssfluxchaud.y=ssflux_base_chaud.x,ssflux_base_chaud.y

            # on calcul le piping et le chemin ce calcul sera refait plus tard
            alg.chemin_dimensionnement_piping(ssfluxchaud,ssFluxF1,r_echelle,m,n)
#            print("ref ssflux chaud :",ssfluxchaud.refFlux,"ref ssflux froid :",ssFluxF1.refFlux)
#            print("la ref du froid",ssFluxF1.refFlux,"| xFinEch froid:",ssFluxF1.xFinEch,"yFinEch froid:",ssFluxF1.yFinEch)
            
            # on teste voir si le flux froid est le dernier ou pas de la liste des sous flux le composant
            nbssfluxfroid=alg.nbssflux(ssFluxFroid,ssFluxF1.refFlux[0])
            if ssFluxF1.refFlux[1]!=nbssfluxfroid-1:
                # si ce n'est pas le dernier on actualise la position de début du sous flux suivant
                ssfluxfroidsuivant=alg.selection(ssFluxFroid,(ssFluxF1.refFlux[0],ssFluxF1.refFlux[1]+1))
                ssfluxfroidsuivant.x=ssFluxF1.xFinEch
                ssfluxfroidsuivant.y=ssFluxF1.yFinEch
#                print("changement fait")
            
            # on gère le fait que le flux froid puisse être divisé
            if ssFluxF1.estDivise:
                # on cherche alors le sous flux étant le premier à être diviser il sera la référence
                ssflux_base_froid=alg.basedivision(ssFluxFroid,ssFluxF1.refFlux)
                # si le sous flux de référence est différent du sous flux étudié
                if ssflux_base_froid.pas_egal(ssFluxF1):
                    # si le sous flux de base est différent alors on actualise la position de fin
                    ssFluxF1.xFin,ssFluxF1.yFin=ssflux_base_froid.xFinEch,ssflux_base_froid.yFinEch
                    # on actualise la valeur du début à celle du sous flux de base
                    ssFluxF1.x,ssFluxF1.y=ssflux_base_froid.x,ssflux_base_froid.y          
                else:
                    ssFluxF1.xFin,ssFluxF1.yFin=ssFluxF1.xFinEch,ssFluxF1.yFinEch
            
            # on actualise de la même manière pour les sous flux chaud
            nbssfluxchaud=alg.nbssflux(ssFluxChaud,ssfluxchaud.refFlux[0])
            if ssfluxchaud.refFlux[1]!=nbssfluxchaud-1:
                # si ce n'est pas le dernier on actualise la position de début du sous flux suivant
                ssfluxchaudsuivant=alg.selection(ssFluxChaud,(ssfluxchaud.refFlux[0],ssfluxchaud.refFlux[1]+1))
                ssfluxchaudsuivant.x=ssfluxchaud.xFinEch
                ssfluxchaudsuivant.y=ssfluxchaud.yFinEch
#                print("x suivant:",ssfluxchaudsuivant.x,"y suivant",ssfluxchaudsuivant.y)
            
            # on gère le fait que le flux chaud puisse être divisé
            if ssfluxchaud.estDivise:
                # on cherche alors le sous flux étant le premier à être diviser il sera la référence
                ssflux_base_chaud=alg.basedivision(ssFluxChaud,ssfluxchaud.refFlux)
                # si le sous flux de référence est différent du sous flux étudié
                if ssflux_base_chaud.pas_egal(ssFluxF1):
                    # si le sous flux de base est différent alors on actualise la position de fin
                    ssfluxchaud.xFin,ssfluxchaud.yFin=ssflux_base_chaud.xFinEch,ssflux_base_chaud.yFinEch
                    # on actualise la valeur du début à celle du sous flux de base
                    ssfluxchaud.x,ssfluxchaud.y=ssflux_base_chaud.x,ssflux_base_chaud.y
                else:
                    ssfluxchaud.xFin,ssfluxchaud.yFin=ssfluxchaud.xFinEch,ssfluxchaud.yFinEch
        else:
            
            # dans le cas d'un sous flux lié à une utilité
            if ssfluxchaud.refFlux[1]!=0:
                
                # on regarde si c'est le dernier flux
                nbssfluxchaud=alg.nbssflux(ssFluxChaud,ssfluxchaud.refFlux[0])
                if ssfluxchaud.refFlux[1]==nbssfluxchaud-1:
                    ssfluxchaud.xFinEch,ssfluxchaud.yFinEch=ssfluxchaud.objFlux.xFin,ssfluxchaud.objFlux.yFin
#                    print("Eh j'ai changé la !")
                    # on regarde le flux précédent
                    ssflux_precedent=alg.selection(ssFluxChaud,(ssfluxchaud.refFlux[0],ssfluxchaud.refFlux[1]-1))
                    # on actualise la position du sous flux en un sous flux ponctuel avec les valeurs du flux précédent
                    ssfluxchaud.x,ssfluxchaud.y=ssflux_precedent.xFinEch,ssflux_precedent.yFinEch
                else:
                    # on regarde le flux précédent
                    ssflux_precedent=alg.selection(ssFluxChaud,(ssfluxchaud.refFlux[0],ssfluxchaud.refFlux[1]-1))
                    # on actualise la position du sous flux en un sous flux ponctuel avec les valeurs du flux précédent
                    ssfluxchaud.x,ssfluxchaud.y,ssfluxchaud.xFinEch,ssfluxchaud.yFinEch=ssflux_precedent.xFinEch,ssflux_precedent.yFinEch,ssflux_precedent.xFinEch,ssflux_precedent.yFinEch
                    # on doit mettre à jour le flux suivant aussi
                    ssfluxchaudsuivant=alg.selection(ssFluxChaud,(ssfluxchaud.refFlux[0],ssfluxchaud.refFlux[1]+1))
                    ssfluxchaudsuivant.x=ssfluxchaud.xFinEch
                    ssfluxchaudsuivant.y=ssfluxchaud.yFinEch
            else:
                
                nbssfluxchaud=alg.nbssflux(ssFluxChaud,ssfluxchaud.refFlux[0])
                if nbssfluxchaud!=1:
                    # dans le cas ou le sous flux est au début de la chaine on change que la position de fin
                    ssfluxchaud.xFinEch,ssfluxchaud.yFinEch=ssfluxchaud.x,ssfluxchaud.y
                else:
#                    print("il est tout seul")
                    ssfluxchaud.xFinEch,ssfluxchaud.yFinEch=ssfluxchaud.objFlux.xFin,ssfluxchaud.objFlux.yFin
    
    print("...on calcule les positions des utilites chaudes...")
    # on s'interesse au flux froid lié aux utilités
    for ssfluxfroid in ssFluxFroid:
        
        if ssfluxfroid.utilite:
            
            if ssfluxfroid.refFlux[1]!=0:
                
                # on vérifie si c'est le dernier
                nbssfluxfroid=alg.nbssflux(ssFluxFroid,ssfluxfroid.refFlux[0])
                if ssfluxfroid.refFlux[1]==nbssfluxfroid-1:
                    ssfluxfroid.xFinEch,ssfluxfroid.yFinEch=ssfluxfroid.objFlux.xFin,ssfluxfroid.objFlux.yFin
                    # on regarde le flux précédent
                    ssflux_precedent=alg.selection(ssFluxFroid,(ssfluxfroid.refFlux[0],ssfluxfroid.refFlux[1]-1))
                    # on actualise la position du sous flux en un sous flux ponctuel avec les valeurs du flux précédent
                    ssfluxfroid.x,ssfluxfroid.y=ssflux_precedent.xFinEch,ssflux_precedent.yFinEch
                    
                else:
                    
                    # on regarde le flux précédent
                    ssflux_precedent=alg.selection(ssFluxFroid,(ssfluxfroid.refFlux[0],ssfluxfroid.refFlux[1]-1))
                    # on actualise la position du sous flux en un sous flux ponctuel avec les valeurs du flux précédent
                    ssfluxfroid.x,ssfluxfroid.y,ssfluxfroid.xFinEch,ssfluxfroid.yFinEch=ssflux_precedent.xFinEch,ssflux_precedent.yFinEch,ssflux_precedent.xFinEch,ssflux_precedent.yFinEch
                    # on doit mettre à jour le flux suivant aussi
                    ssfluxfroidsuivant=alg.selection(ssFluxFroid,(ssfluxfroid.refFlux[0],ssfluxfroid.refFlux[1]+1))
                    ssfluxfroidsuivant.x=ssfluxfroid.xFinEch
                    ssfluxfroidsuivant.y=ssfluxfroid.yFinEch
            else:
                
                nbssfluxfroid=alg.nbssflux(ssFluxFroid,ssfluxfroid.refFlux[0])
                if nbssfluxfroid!=1:
                    
                    # dans le cas ou le sous flux est au début de la chaine on change que la position de fin
                    ssfluxfroid.xFinEch,ssfluxfroid.yFinEch=ssfluxfroid.x,ssfluxfroid.y
                    
                else:
                    
                    ssfluxfroid.xFinEch,ssfluxfroid.yFinEch=ssfluxfroid.objFlux.xFin,ssfluxfroid.objFlux.yFin
    
#    for i in range(len(objReseau.listeSsFlux)):
#        if objReseau.listeSsFlux[i].typeFlux=="f":
#            print("la ref est",objReseau.listeSsFlux[i].refFlux,"xFin froid",objReseau.listeSsFlux[i].xFinEch,"yFin",objReseau.listeSsFlux[i].yFinEch)
    
    print("...on calcule le piping et les possibles échangeurs pour chaque couple...")
    # on parcourt tous les couples du reseau une fois qu'on connait la position de tous les sous flux
    for couple in objReseau.listeCouple:
        
        # on selectionne les sous flux du couple
        ssFluxC1=alg.selection(ssFluxChaud,couple.ssFluxC)
        ssFluxF1=alg.selection(ssFluxFroid,couple.ssFluxF)
        # dimensionne le piping pour les deux sous flux impliqué dans le couple
        alg.chemin_dimensionnement_piping_position_done(ssFluxC1,ssFluxF1,r_echelle,m,n)
        # calcul des pertes de charge pour les sous flux 
        alg.pertes_de_charge_piping(ssFluxC1)
        alg.pertes_de_charge_piping(ssFluxF1)
        
    for ssflux in ssFluxChaud:
        
        # le cas de l'utilite entre plusieurs sous-flux ne pose pas de problème pour le sous flux chaud le cas en fin et traité plus tard
        if not ssflux.utilite:
            
            # on calcule la nouvelle température d'entrée
            alg.perte_temp(ssflux)
            
            # pour l'échangeur la température de sortie est fixée on doit recalculer la puissance échangée
            couple=alg.selection_couple(objReseau.listeCouple,ssflux)
            couple.puissE=ssflux.CP*np.abs(ssflux.Te-ssflux.Ts)/1000 # en kW
            print(couple.puissE,couple.ssFluxC)
            
            # si le sous flux est en fin de chaine on doit prendre en compte les pertes de chaleur due au dernier trajet
#            if not ssflux.refEch:
#                
##                print("je passe dans cette boucle la",ssflux.refEch)
#                # on ajuste la puissance dans l'échangeur pour avoir la bonne température après le transport 
#                couple.puissE,ssflux.Ts=alg.perte_reso(ssflux) # le Ts est la température à la sortie de l'échangeur
    
    # pour le DEBUGGAGE
#    L=[21,23,25,27,29,31,33]
#    comp=0
    for ssflux in ssFluxFroid:
        
#        print("1ere ref",ssflux.refFlux)
        if ssflux.utilite==False:
            
#            print("2eme ref",ssflux.refFlux)
            # on calcule la nouvelle température d'entrée
            alg.perte_temp(ssflux)
            
            # la nouvelle puissance de l'échangeur a déjà été calculée
            couple=alg.selection_couple(objReseau.listeCouple,ssflux)
            
            # on garde en mémoire la température de sortie initiale
            Ts_ini=ssflux.Ts
            
            # on ajuste la température de sortie
            ssflux.Ts=ssflux.Te+couple.puissE*1000/ssflux.CP # la puissance est en kW initialement
#            print("je passe par la")
            
            # on actualise la valeur du sous flux suivant
            
            if ssflux.refEch:
                
#                print("je passe ici")
                ssflux_suivant=alg.selection(ssFluxFroid,(ssflux.refFlux[0],ssflux.refFlux[1]+1))
                ssflux_suivant.Te=ssflux.Ts
#                print("chgt dans ssflux_suivant",ssflux_suivant.Te,"°C")
#                print("dans le reseau directement",objReseau.listeSsFlux[L[comp]].Te,"°C | la ref",objReseau.listeSsFlux[L[comp]].refFlux)
                
#                if comp<len(L):
#                    print("j'ai fini",comp,L[comp])
            
            # sinon on vérifie si la température est égale à la température souhaitée initialement
            else:
#                comp+=1
#                print("ou la")
                alg.perte_temp_fin(ssflux)
                
#                if comp<len(L):
#                    print("dans le reseau directement",objReseau.listeSsFlux[L[comp]].Te,"°C | la ref",objReseau.listeSsFlux[L[comp]].refFlux)
                
                if Ts_ini!=ssflux.Ts:
                    
                    # on ajoute une utilité chaude
                    # print("ECART DE TEMPERATURE ", Ts_ini-ssflux.Ts)
                    # print("CP DU FLUX :", ssflux.CP)
                    objReseau.listeUtilite.append(uti.utilite(ssflux.refFlux,ssflux.CP*np.abs(Ts_ini-ssflux.Ts)/1000,"c"))
                    # print("PUISSANCE DE L'UTILITE RAJOUTEE ", objReseau.listeUtilite[-1].puissE)
                    
                    
                    # on réactualise le nombre d'utilité
                    objReseau.KPI.nbUti=objReseau.KPI.nbUti+1
        else:
            
            if ssflux.refEch:
                
                # on modifie la puissance de l'utilité
                utilite=alg.selection_utilite(objReseau.listeUtilite,ssflux.refFlux,ssflux.typeFlux)
                utilite.puissE=ssflux.CP*np.abs(ssflux.Te-ssflux.Ts)/1000 # en kW
                # on n'a pas besoin de modifier la température du sous flux suivant
                
    print("...on calcule le piping des utilites finissant le cycle de sous flux...")
    # on s'interesse à tous les sous flux qui se termine par une utilité
    for ssflux in objReseau.listeSsFlux:
        
        if ssflux.utilite:
            
            if not ssflux.refEch:
                
                # on dimensionne le piping et on calcule le cout
                alg.chemin_dimensionnement_piping_utilite(ssflux,r_echelle,m,n)
                # on calcule les pertes de charge de cette partie
                alg.pertes_de_charge_piping(ssflux)
                
                # on actualise la puissance de l'utilité pour satisfaire le besoin du process
                utilite=alg.selection_utilite(objReseau.listeUtilite,ssflux.refFlux,ssflux.typeFlux)
                
                # on calcule la température de sortie avec l'utilité en prenant en compte la nouvelle température d'entrée
                if ssflux.typeFlux=="c":
                    Ts_modif=ssflux.Te-utilite.puissE/ssflux.CP
                else:
                    Ts_modif=ssflux.Te+utilite.puissE/ssflux.CP
                    
                # on vérifie si la température de sortie est satisfaite
                if ssflux.Ts!=Ts_modif:
                    
                    # si c'est pas le cas on ajuste la puissance de l'utilité
                    utilite.puissE=ssflux.CP*np.abs(ssflux.Ts-ssflux.Te)/1000 # en kW
    
    print("...on sélectionne les échangeurs pour faire l'échange...")
    for couple in objReseau.listeCouple:
        
        # on selectionne les sous flux du couple
        ssFluxC1=alg.selection(ssFluxChaud,couple.ssFluxC)
        ssFluxF1=alg.selection(ssFluxFroid,couple.ssFluxF)
        # print("TE CHAUD : "+str(ssFluxC1.Te)+" --- TS CHAUD : "+str(ssFluxC1.Ts))
        if(ssFluxC1.Te <= ssFluxC1.Ts) :
            print("AAAAAAAAAAAAAAAAAAAH ENCORE UN PROBLEME AAAAAAAAAAAAAAAAAAAAAAAAAAAAAH")

        # choix des possibilités des échangeurs
        couple.classement=alg.classement_ech(ssFluxC1,ssFluxF1)
        print(couple.classement)
#        print("la ref du ss flux",ssFluxC1.refFlux,"| x",ssFluxC1.x,"y",ssFluxC1.y,"| xFinEch",ssFluxC1.xFinEch,"yFinEch",ssFluxC1.yFinEch,"| xFin",ssFluxC1.xFin,"yFin",ssFluxC1.yFin,"| long tuy",ssFluxC1.longTuy,"m")
        
        # on choisit l'échangeur le moins couteux
        if len(couple.classement) == 1 :
            
            couple.objEch = alg.dimensionnement_echangeur(ssFluxC1,ssFluxF1,couple.classement[0])
        else:
            # print(str(ssFluxC1)+ " " + str(ssFluxF1) )
            # ssFluxC1.hasNaN()
            # ssFluxF1.hasNaN()
            Ech = [alg.dimensionnement_echangeur(ssFluxC1,ssFluxF1,couple.classement[i]) for i in range(len(couple.classement))]
            Prix_ech = [Ech[i].cout for i in range(len(Ech))]
            prix_min = 1e9
            num_ech = 0
            print ("--------------------------------------- PRIX _ ECH"+str(Prix_ech))
            for i in range(len(Prix_ech)):
                
                if Prix_ech[i]<prix_min:
                    
                    prix_min = Prix_ech[i]
                    num_ech = i
                    
            couple.objEch = Ech[num_ech]
            
#    print("\nNouvelle longueur avant boucle\n")
#    for couple in objReseau.listeCouple:
#        
#        #on selectionne les sous flux du couple
#        ssFluxC1=alg.selection(ssFluxChaud,couple.ssFluxC)
#        ssFluxF1=alg.selection(ssFluxFroid,couple.ssFluxF)
#        print("la ref du ss flux",ssFluxC1.refFlux,"| x",ssFluxC1.x,"y",ssFluxC1.y,"| xFinEch",ssFluxC1.xFinEch,"yFinEch",ssFluxC1.yFinEch,"| xFin",ssFluxC1.xFin,"yFin",ssFluxC1.yFin,"| long tuy",ssFluxC1.longTuy,"m")
#        
#     SIMPLEMENT POUR DU DEBUGGAGE
    for ssflux in objReseau.listeSsFlux:
    
        print("la ref du ss flux",ssflux.refFlux,"| le type du ss flux",ssflux.typeFlux,"| type objPip",type(ssflux.objPip),"| utilite",ssflux.utilite)
#        
    
    print("...on dimensionne la pompe pour chaque flux...")
    # on parcourt les ssflux chaud dans l'ordre
    # variable contenant les pertes de charge tot d'un flux
    nbr_flux_chaud = alg.nbr_flux(ssFluxChaud)
#    dP_tot_c = [0 for k in range(nbr_flux_chaud)]
    P_tot_c = [0 for k in range(nbr_flux_chaud)]
    # on prend en compte les divisions pour le cout des pompes
    P_divise = []
    # compteur pour savoir à quel flux on est
    num_flux_c = 0
    for ssflux in ssFluxChaud :
        print("num_flux_c",num_flux_c)
        # s'il y a un échange on prend en compte les pertes dans l'échangeur
        if not ssflux.utilite :
            
            # s'il échange encore on ne termine pas le calcul
            if ssflux.refEch:
                # on cherche le couple impliqué dans l'échange
                couple=alg.selection_couple(objReseau.listeCouple,ssflux)
                
                if ssflux.estDivise :
                    if couple.objEch.div :
                        P_divise.append(couple.objEch.pompeSplitChaud)
                        ssfluxchaudsuivant = alg.selection(ssFluxChaud,(ssflux.refFlux[0],ssflux.refFlux[1]+1))
                        if not ssfluxchaudsuivant.estDivise :
#                                DP_ajout = max(dP_divise)
                            P_ajout = max(P_divise)
#                                print("perte de charge",DP_ajout*1e-5,"bar")
#                                dP_tot_c[num_flux_c] += DP_ajout
                            P_tot_c[num_flux_c] += P_ajout
                            P_divise = []
                    else:
                        P_divise.append(Pompe.puissance_fonctionnement_normal(ssflux.debVol,couple.objEch.perteChaud+ssflux.objPip.pertes))
                        # print("ICIIIIII POOOOOOMPES PERTES", ssflux.refFlux[0], couple.objEch.perteChaud+ssflux.objPip.pertes)
                        ssfluxchaudsuivant = alg.selection(ssFluxChaud,(ssflux.refFlux[0],ssflux.refFlux[1]+1))
                        if not ssfluxchaudsuivant.estDivise :
#                                DP_ajout = max(dP_divise)
                            P_ajout = max(P_divise)
#                                print("perte de charge",DP_ajout*1e-5,"bar")
#                                dP_tot_c[num_flux_c] += DP_ajout
                            P_tot_c[num_flux_c] += P_ajout
                            P_divise = []
                else:
                    if couple.objEch.div :
                        P_tot_c[num_flux_c] += couple.objEch.pompeSplitChaud
                    else:
                        P_tot_c[num_flux_c] += Pompe.puissance_fonctionnement_normal(ssflux.debVol,couple.objEch.perteChaud+ssflux.objPip.pertes)
            # s'il échange plus on doit terminer le calcul
            else:
                # on cherche le couple impliqué dans l'échange
                couple=alg.selection_couple(objReseau.listeCouple,ssflux)
                
                if ssflux.refFlux[1] != 0 :
                    ssfluxchaudprecedent = alg.selection(ssFluxChaud,(ssflux.refFlux[0],ssflux.refFlux[1]-1))
                    if ssfluxchaudprecedent.estDivise and ssflux.estDivise :
                        if couple.objEch.div :
                            P_divise.append(couple.objEch.pompeSplitChaud)
                        else:
#                                dP_divise.append(couple.objEch.perteChaud+ssflux.objPip.pertes)
                            P_divise.append(Pompe.puissance_fonctionnement_normal(ssflux.debVol,couple.objEch.perteChaud+ssflux.objPip.pertes))
#                                DP_ajout = max(dP_divise)
                        P_ajout = max(P_divise)
#                                print("perte de charge",DP_ajout*1e-5,"bar")
#                                dP_tot_c[num_flux_c] += DP_ajout
                        P_tot_c[num_flux_c] += P_ajout
                        P_divise = []
#                                dP_divise = []
                else:
                    if couple.objEch.div :
                        P_tot_c[num_flux_c] += couple.objEch.pompeSplitChaud
                    else:
                        P_tot_c[num_flux_c] += Pompe.puissance_fonctionnement_normal(ssflux.debVol,couple.objEch.perteChaud+ssflux.objPip.pertes)
                # on calcule ensuite les pertes de charge initiales
                dP_base=alg.chemin_perte_inital(ssflux,r_echelle,m,n)
                # on dimensionne la pompe correspondante
#                ssflux.objPomp = pompe(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_c[num_flux_c],dP_base),Pompe.coutInves(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_c[num_flux_c],dP_base)),Pompe.coutFonc(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_c[num_flux_c],dP_base)),Pompe.coutFonc_annuel(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_c[num_flux_c],dP_base)))
                ssflux.objPomp = Pompe.Pompe(Pompe.puissance_regu_p(ssflux.debVol,P_tot_c[num_flux_c],dP_base),Pompe.coutInves(Pompe.puissance_regu_p(ssflux.debVol,P_tot_c[num_flux_c],dP_base)),Pompe.coutFonc(Pompe.puissance_regu_p(ssflux.debVol,P_tot_c[num_flux_c],dP_base)),Pompe.coutFonc_annuel(Pompe.puissance_regu_p(ssflux.debVol,P_tot_c[num_flux_c],dP_base)))
                # print("ICIIIIII POOOOOOMPES PERTES l444", ssflux.refFlux[0], couple.objEch.perteChaud+ssflux.objPip.pertes)
                # on actualise le flux que l'on va traiter
                num_flux_c += 1
        
        # dans le cas d'une utilité on a que le cas final a traiter
        else:
            
            if not ssflux.refEch:
                # on calcule les pertes de charges coté du fluide chaud
#                dP_tot_c[num_flux_c] += ssflux.objPip.pertes
                P_tot_c[num_flux_c] += Pompe.puissance_fonctionnement_normal(ssflux.debVol,ssflux.objPip.pertes)
                # on calcule les pertes de charge du tracé initial
                dP_base=alg.chemin_perte_inital(ssflux,r_echelle,m,n)
                # on dimensionne la pompe correspondante
#                ssflux.objPomp = pompe(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_c[num_flux_c],dP_base),Pompe.coutInves(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_c[num_flux_c],dP_base)),Pompe.coutFonc(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_c[num_flux_c],dP_base)),Pompe.coutFonc_annuel(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_c[num_flux_c],dP_base)))
                ssflux.objPomp = Pompe.Pompe(Pompe.puissance_regu_p(ssflux.debVol,P_tot_c[num_flux_c],dP_base),Pompe.coutInves(Pompe.puissance_regu_p(ssflux.debVol,P_tot_c[num_flux_c],dP_base)),Pompe.coutFonc(Pompe.puissance_regu_p(ssflux.debVol,P_tot_c[num_flux_c],dP_base)),Pompe.coutFonc_annuel(Pompe.puissance_regu_p(ssflux.debVol,P_tot_c[num_flux_c],dP_base)))
                # print("données pour puissance pompe", ssflux.debVol, P_tot_c[num_flux_c], dP_base)
                # print("puissance pompe", ssflux.objPomp.puissance)
                # print("ICIIIIII POOOOOOMPES PERTES l460", ssflux.refFlux[0], couple.objEch.perteChaud+ssflux.objPip.pertes)
                # on actualise le flux que l'on va traiter
                num_flux_c += 1
    
    # on parcourt les ssflux froid dans l'ordre
    # variable contenant les pertes de charge tot d'un flux
    nbr_flux_froid= alg.nbr_flux(ssFluxFroid)
#    dP_tot_f = [0 for k in range(nbr_flux_froid)]
    P_tot_f = [0 for k in range(nbr_flux_froid)]
    # compteur pour savoir à quel flux on est
    num_flux_f = 0
    
    P_divise = []
    for ssflux in ssFluxFroid :
        print("num_flux_f",num_flux_f)
        # s'il y a un échange on prend en compte les pertes dans l'échangeur
        if not ssflux.utilite :
            
            # s'il échange encore on ne termine pas le calcul
            if ssflux.refEch:
                # on cherche le couple impliqué dans l'échange
                couple=alg.selection_couple(objReseau.listeCouple,ssflux)
                if ssflux.estDivise :
                    if couple.objEch.div :
                        P_divise.append(couple.objEch.pompeSplitFroid)
                    else:
#                            dP_divise.append(couple.objEch.perteFroid+ssflux.objPip.pertes)
                        P_divise.append(Pompe.puissance_fonctionnement_normal(ssflux.debVol,couple.objEch.perteFroid+ssflux.objPip.pertes))
                    ssfluxfroidsuivant = alg.selection(ssFluxFroid,(ssflux.refFlux[0],ssflux.refFlux[1]+1))
                    if not ssfluxfroidsuivant.estDivise :
#                                DP_ajout = max(dP_divise)
                        P_ajout=max(P_divise)
#                                print("perte de charge",DP_ajout*1e-5,"bar")
#                                dP_tot_f[num_flux_f] += DP_ajout
                        P_tot_f[num_flux_f] += P_ajout
                        P_divise = []
                else:
                    if couple.objEch.div :
                        P_tot_f[num_flux_f] += couple.objEch.pompeSplitFroid
                    else:
                        P_tot_f[num_flux_f] += Pompe.puissance_fonctionnement_normal(ssflux.debVol,couple.objEch.perteFroid+ssflux.objPip.pertes)
            # s'il échange plus on doit terminer le calcul
            else:
                # on cherche le couple impliqué dans l'échange
                couple=alg.selection_couple(objReseau.listeCouple,ssflux)
                
                if ssflux.refFlux[1] != 0 :
                    ssfluxfroidprecedent = alg.selection(ssFluxFroid,(ssflux.refFlux[0],ssflux.refFlux[1]-1))
                    if ssfluxfroidprecedent.estDivise and ssflux.estDivise :
                        if couple.objEch.div:
                            P_divise.append(couple.objEch.pompeSplitFroid)
                        else:
#                                    dP_divise.append(couple.objEch.perteFroid+ssflux.objPip.pertes)
                            P_divise.append(Pompe.puissance_fonctionnement_normal(ssflux.debVol,couple.objEch.perteFroid+ssflux.objPip.pertes))
#                                    DP_ajout = max(dP_divise)
                        P_ajout = max(P_divise)
#                                    print("perte de charge",DP_ajout*1e-5,"bar")
#                                    dP_tot_f[num_flux_f] += DP_ajout
                        P_tot_f[num_flux_f] += P_ajout
                        P_divise = []
                else:
                    if couple.objEch.div:
                        P_tot_f[num_flux_f] += couple.objEch.pompeSplitFroid
                    else:
#                                dP_tot_f[num_flux_f] += couple.objEch.perteFroid+ssflux.objPip.pertes
                        P_tot_f[num_flux_f] += Pompe.puissance_fonctionnement_normal(ssflux.debVol,couple.objEch.perteFroid+ssflux.objPip.pertes)
                # on calcule les perte de charge coté du fluide chaud
#                dP_tot_f[num_flux_f] += couple.objEch.perteFroid+ssflux.objPip.pertes
#                P_tot_f[num_flux_f] += Pompe.puissance_fonctionnement_normal(ssflux.debVol,couple.objEch.perteFroid+ssflux.objPip.pertes)
                # on calcule ensuite les pertes de charge initiales
                dP_base=alg.chemin_perte_inital(ssflux,r_echelle,m,n)
                # on dimensionne la pompe correspondante
#                ssflux.objPomp = pompe(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_f[num_flux_f],dP_base),Pompe.coutInves(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_f[num_flux_f],dP_base)),Pompe.coutFonc(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_f[num_flux_f],dP_base)),Pompe.coutFonc_annuel(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_f[num_flux_f],dP_base)))
                ssflux.objPomp = Pompe.Pompe(Pompe.puissance_regu_p(ssflux.debVol,P_tot_f[num_flux_f],dP_base),Pompe.coutInves(Pompe.puissance_regu_p(ssflux.debVol,P_tot_f[num_flux_f],dP_base)),Pompe.coutFonc(Pompe.puissance_regu_p(ssflux.debVol,P_tot_f[num_flux_f],dP_base)),Pompe.coutFonc_annuel(Pompe.puissance_regu_p(ssflux.debVol,P_tot_f[num_flux_f],dP_base)))
                # print("données pour puissance pompe", ssflux.debVol, P_tot_f[num_flux_f], dP_base)
                # print("puissance pompe", ssflux.objPomp.puissance)
                # print("ICIIIIII POOOOOOMPES PERTES l534", ssflux.refFlux[0], couple.objEch.perteChaud+ssflux.objPip.pertes)
                # on actualise le flux que l'on va traiter
                # print("ligne 541", ssflux.refFlux, num_flux_f)
                # num_flux_f += 1
        
        # dans le cas d'une utilité on a que le cas final a traiter
        else:
            if ssflux.objPip is not None :
                # on calcule les pertes de charges coté du fluide chaud
    #           dP_tot_f[num_flux_f] += ssflux.objPip.pertes
                P_tot_f[num_flux_f] += Pompe.puissance_fonctionnement_normal(ssflux.debVol,ssflux.objPip.pertes)
                # on calcule les pertes de charge du tracé initial
                dP_base=alg.chemin_perte_inital(ssflux,r_echelle,m,n)
            else :
                P_tot_f[num_flux_f] += 0
                dP_base = 0
            # on dimensionne la pompe correspondante
#            ssflux.objPomp = pompe(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_f[num_flux_f],dP_base),Pompe.coutInves(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_f[num_flux_f],dP_base)),Pompe.coutFonc(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_f[num_flux_f],dP_base)),Pompe.coutFonc_annuel(Pompe.puissance_regu_pdc(ssflux.debVol,dP_tot_f[num_flux_f],dP_base)))
            ssflux.objPomp = Pompe.Pompe(Pompe.puissance_regu_p(ssflux.debVol,P_tot_f[num_flux_f],dP_base),Pompe.coutInves(Pompe.puissance_regu_p(ssflux.debVol,P_tot_f[num_flux_f],dP_base)),Pompe.coutFonc(Pompe.puissance_regu_p(ssflux.debVol,P_tot_f[num_flux_f],dP_base)),Pompe.coutFonc_annuel(Pompe.puissance_regu_p(ssflux.debVol,P_tot_f[num_flux_f],dP_base)))
            # print("données pour puissance pompe", ssflux.debVol, P_tot_f[num_flux_f], dP_base)
            # print("puissance pompe", ssflux.objPomp.puissance)
            # print("ICIIIIII POOOOOOMPES PERTES l549", ssflux.refFlux[0], couple.objEch.perteChaud+ssflux.objPip.pertes)
            # on actualise le flux que l'on va traiter
            # print("ligne 562", ssflux.refFlux, num_flux_f)
            num_flux_f += 1
            
    for couple in objReseau.listeCouple:
        print("type echangeur",couple.objEch.typee,"| surface echange",couple.objEch.surfEch,"m² | ref chaud et froid",couple.ssFluxC,couple.ssFluxF)
    
    print("...on calcule les kpis nécessaires à la prise de décision...")
    # on calcule le cout d'investissement total
    Cout_invest=0
    cout_pompe_invest = 0
    cout_ech = 0
    puiss_ech = 0
    
    surf_min = 1e9
    surf_max = 0
    puiss_min = 1e9
    puiss_max = 0
    
    # on calcule le cout d'investissement des échangeurs et les autres kpi relevant des echangeurs
    for couple in objReseau.listeCouple : 
        Cout_invest+=couple.objEch.cout
        # print("cout objech", couple.objEch.cout)
        cout_ech += couple.objEch.cout
        puiss_ech += couple.puissE
        
        if couple.puissE < puiss_min :
            puiss_min = couple.puissE
        
        if couple.puissE > puiss_max :
            puiss_max = couple.puissE
        
        if couple.objEch.surfEch < surf_min :
            surf_min = couple.objEch.surfEch
        
        if couple.objEch.surfEch > surf_max :
            surf_max = couple.objEch.surfEch
    
    # on actualise les KPI sur les échangeurs
    objReseau.KPI.puissanceminech = puiss_min
    objReseau.KPI.puissancemaxech = puiss_max
    objReseau.KPI.surfaceminech = surf_min
    objReseau.KPI.surfacemaxech = surf_max
    objReseau.KPI.coutEch = cout_ech
    
    cout_tuy = 0
    long_tuy = 0
    # on calcule le cout d'investissement du piping et des pompes
    for ssflux in objReseau.listeSsFlux:
        
        # on doit traiter différement le cas des utilites
        if not ssflux.utilite:
            # si ce n'est pas une utilité il y aura une pompe en plus du piping
            Cout_invest+=ssflux.objPip.coutTuy+ssflux.objPip.coutIso#+ssflux.objPomp.coutInves
            # print("Cout tuy : ", ssflux.objPip.coutTuy)
            # print("Cout iso : ", ssflux.objPip.coutIso)
            #cout_pompe_invest += ssflux.objPomp.coutInves
            cout_tuy += ssflux.objPip.coutTuy+ssflux.objPip.coutIso
            long_tuy += ssflux.longTuy
            # if not ssflux.refEch :
                # Cout_invest += ssflux.objPomp.coutInves
                # print("CoutInves : ", ssflux.objPomp.coutInves)
                # cout_pompe_invest += ssflux.objPomp.coutInves
                # print("ligne 624 - objPomp.coutInves", ssflux.objPomp.coutInves)
            # print("ligne 502",Cout_invest)
        
        else:
#            print("le type",ssflux.typeFlux,"la ref",ssflux.refFlux)
            
            # pour les utilités on doit vérifier qu'elle n'est pas milieu de cycle
            if ssflux.typeFlux=="f":
                nbssFlux=alg.nbssflux(ssFluxFroid,ssflux.refFlux[0])
            else:
                nbssFlux=alg.nbssflux(ssFluxChaud,ssflux.refFlux[0])
                
            if ssflux.refFlux[1]==nbssFlux:
                if nbssFlux!=1:
                    Cout_invest+=ssflux.objPip.coutTuy+ssflux.objPip.coutIso#+ssflux.objPomp.coutInves
                    cout_tuy += ssflux.objPip.coutTuy+ssflux.objPip.coutIso
                    long_tuy += ssflux.longTuy
                    # cout_pompe_invest += ssflux.objPomp.coutInves
                    print("ligne 516",Cout_invest)
                    # print("ligne 643 - objPomp.coutInves", ssflux.objPomp.coutInves)
                else:
                    Cout_invest+=ssflux.objPip.coutTuy+ssflux.objPip.coutIso
                    cout_tuy += ssflux.objPip.coutTuy+ssflux.objPip.coutIso
                    long_tuy += ssflux.longTuy
                    print("ligne 519",Cout_invest)
    
    # on calcule les KPI relatifs aux pompes
    Cout_fonc=0
    puiss_pompe=0
    nb_pompe=0
    listepuisspompe = []
    for ssflux in objReseau.listeSsFlux:
        if ssflux.refEch and ssflux.utilite:
            puiss_pompe+=0
        else:
            if not ssflux.refEch :
                nb_pompe +=1
                cout_pompe_invest += ssflux.objPomp.coutInves
                # print("coutInves", ssflux.objPomp.coutInves, ssflux.objFlux.nom)
                listepuisspompe.append(ssflux.objPomp.puissance)
                puiss_pompe+=ssflux.objPomp.puissance
                Cout_fonc+=ssflux.objPomp.coutFoncAnnuel
                # print("COUTFONC DES POOOOOOOOOOOOOOOOOOMPES", ssflux.objPomp.coutFoncAnnuel)
                # print("pertes compensées par la pompe", couple.objEch.perteChaud+ssflux.objPip.pertes)
                # print("puissance de la pompe au-dessus", ssflux.objPomp.puissance)
                # print("flux de la pompe au-dessus", ssflux.refFlux[0])
                # print("longueur tuyauterie associée", ssflux.longTuy)
    
    ##### Recherche des différentes puissances des pompes #####  
    print("-----Puissances des pompes : ", listepuisspompe)
    print("-----Puissance totale des pompes : ", sum(listepuisspompe)/1000)


    # print("le cout d'investissement est de :",Cout_invest,"€")
    Cout_invest += cout_pompe_invest
    print(Cout_invest)
    
    # on calcule le CAPEX
    objReseau.KPI.cap,autre=Cost.Capex(Cout_invest)
    print(objReseau.KPI.cap, autre)
    
    # on calcule l'opex en prenant en compte le cout de fonctionnement des pompes et les utilités
    Cout_utilite=0
    for ssflux in objReseau.listeSsFlux:
        
        # on doit traiter différement le cas des utilites
        if ssflux.utilite:
            # si ce n'est pas une utilité il y aura une pompe en plus du piping
#            if not ssflux.refEch:
#                Cout_fonc+=ssflux.objPomp.coutFoncAnnuel
        
        #else:
            
            # pour les utilités on doit vérifier qu'elle n'est pas milieu de cycle
            if ssflux.typeFlux=="f":
                # on calcule le cout de l'utilité chaude
                Cout_utilite+=alg.opex_utilite_chaude(alg.selection_utilite(objReseau.listeUtilite,ssflux.refFlux,"f").puissE)
                nbssFlux=alg.nbssflux(ssFluxFroid,ssflux.refFlux[0])
            else:
                # on calcule le cout de l'utilité froide
                Cout_utilite+=alg.opex_utilite_froide(alg.selection_utilite(objReseau.listeUtilite,ssflux.refFlux,"c").puissE)
                nbssFlux=alg.nbssflux(ssFluxChaud,ssflux.refFlux[0])
                
#            if ssflux.refFlux[1]==nbssFlux and nbssFlux!=1:
#                Cout_fonc+=ssflux.objPomp.coutFoncAnnuel
    

    # print("Cout de fonctionnement des pompes",Cout_fonc,"€")
    # print("Cout de fonctionnement des utilités",Cout_utilite,"€")

    objReseau.KPI.puissancepompe = puiss_pompe
    objReseau.KPI.nbpompe = nb_pompe
    objReseau.KPI.coutfoncpompe = Cout_fonc
    objReseau.KPI.coutPompe = cout_pompe_invest
    objReseau.KPI.couttuyauterie = cout_tuy
    objReseau.KPI.longueurtuyauterie = long_tuy
    
    # KPI pour les utilités
    objReseau.KPI.coutfoncuti = Cout_utilite
    
    # Puissance et énergie échangée
    objReseau.KPI.puissEch=puiss_ech
    # facteur donnant le pourcentage du temps d'utilisation dans l'année
    facteur_utilisation=0.8
    # on actualise la valeur du KPI donnant l'énergie échangée en kWh
    objReseau.KPI.enEch=puiss_ech*8760*facteur_utilisation
    
    # on ajuste l'énergie sauvée en enlevant ce qui est consommé par les nouvelles pompes
    # print("Puissance des pompes",puiss_pompe/1000,"kW")
    
    # on calcul le CO2 sauvé
    
    # on attribut des valeurs aux rendements combustion et thermique/élec
    rendement=[0.8,0.5]
    
    # on attribut des pourcentage sur les différentes source de production d'électricité en fonction du site indus elec,gn,gpl,essence,diesel,charbon
    pourcentage=[0.4,0.6,0,0,0,0]
    
    # on calcule le CO2 avec une énergie en kWh
    objReseau.KPI.co2=Cost.CO2(pourcentage,rendement,puiss_ech*8760*0.8)
    
    # on calcule les économies réalisées
    # dans le cas là on considère que les flux chauds ne sont pas refroidis dans la réalité donc l'énergie des sous flux froids est la seule intéressante
    objReseau.KPI.ecoElec,objReseau.KPI.ecoGaz,objReseau.KPI.ecoFioul=Cost.economie(puiss_ech)
    
    objReseau.KPI.ecoTot = Cost.economie_tot(puiss_ech,0.4,0.6,0)
    
    OPEX,autre2 = Cost.Opex(objReseau.KPI.cap)

    # print(objReseau.KPI.ecoTot)
    # print(OPEX, autre2)

    # on finit le calcul de l'OPEX
    objReseau.KPI.op = Cout_fonc+Cout_utilite+OPEX
    # print(objReseau.KPI.op)

    # on calcule le TRI
    objReseau.KPI.TRI = objReseau.KPI.cap/(objReseau.KPI.ecoTot-objReseau.KPI.op)

    for util in objReseau.listeUtilite :
        if util.typeUtil == "c":
            objReseau.KPI.puissanceutilitechaude += util.puissE
        else:
            objReseau.KPI.puissanceutilitefroide += util.puissE


    #######################################################################################
    ########## On calcule la VAN et l'IP au bout de la durée de la vie du réseau ##########
    #######################################################################################

    act  = 0.01 #taux d'actualisation de 1% (A CHANGER SI BESOIN)
    annee = 10 #durée de vie en année (A CHANGER SI BESOIN)

    print("Le taux d'actualisation choisi pour les calculs de VAN et d'IP est de ", act*100, "%")
    print("La durée de vie choisie pour les équipements de récupération de chaleur est de ", annee, "ans")

    vantemp = (-1)*objReseau.KPI.cap
    for k in range (1, (annee+1)) :
        vantemp += (objReseau.KPI.ecoTot - objReseau.KPI.op) / ((1+act)**k)
    objReseau.KPI.van = vantemp
    # print(vantemp)

    objReseau.KPI.ip = (objReseau.KPI.cap + objReseau.KPI.van) / objReseau.KPI.cap
    # print(objReseau.KPI.ip)
    
    ###############################################################################################
    ##### On calcule les indicateurs pour chaque échangeur (nouveaux attributs classe couple) #####
    ###############################################################################################

    rendement = [0.8, 0.5] #valeurs des rendements de combustion et thermique/élec (tiré de algopiping)
    pourcentage = [0.4, 0.6, 0, 0, 0, 0] #pourcentages des différentes sources de production d'électricité du site industriel : élec, gaz naturel, GPL, essence, diesel, charbon (tiré de algopiping)
    # act  = 0.01 #taux d'actualisation de 1% (A CHANGER SI BESOIN)
    # annee = 10 #durée de vie en année (A CHANGER SI BESOIN)

    # Tiré de Cost.py --> Economie et Economie_tot
    h_annee = 8760 #nombre d'h en un an
    # C_elec = 0.0715 # en kWh
    # C_gaz = 0.075 # en kWh
    # C_fioul = 0.0917 # en kWh

    # C'était mal fait pour récupérer les infos : création d'un dictionnaire
    # L'appel à ssFlux renvoyait le tuple (a,b) et pas l'objet ssFlux
    # Le dictionnaire permet à partir du tuple d'aller chercher l'objet ssFlux qui correspond
    ssFluxDictC = {}
    ssFluxDictF = {}
    for i in objReseau.listeSsFlux :
        if i.typeFlux == 'c':
            if i.refFlux[0] not in ssFluxDictC :
                ssFluxDictC[i.refFlux[0]] = {}
            ssFluxDictC[i.refFlux[0]][i.refFlux[1]] = i
        else :
            if i.refFlux[0] not in ssFluxDictF :
                ssFluxDictF[i.refFlux[0]] = {}
            ssFluxDictF[i.refFlux[0]][i.refFlux[1]] = i

    # On parcourt la listeCouple et on attribut les valeurs aux attributs de la classe couple
    for cple in objReseau.listeCouple :

        couttot = cple.objEch.cout
        couttot += ssFluxDictC[cple.ssFluxC[0]][cple.ssFluxC[1]].objPip.coutTuy + ssFluxDictC[cple.ssFluxC[0]][cple.ssFluxC[1]].objPip.coutIso
        couttot += ssFluxDictF[cple.ssFluxF[0]][cple.ssFluxF[1]].objPip.coutTuy + ssFluxDictF[cple.ssFluxF[0]][cple.ssFluxF[1]].objPip.coutIso

        lontuy = 0
        lontuy += ssFluxDictC[cple.ssFluxC[0]][cple.ssFluxC[1]].longTuy
        lontuy += ssFluxDictF[cple.ssFluxF[0]][cple.ssFluxF[1]].longTuy

        cple.couttot = couttot
        cple.lontuy = lontuy 

        cple.capexech = Cost.Capex(cple.couttot)[0]
        cple.opexech = Cost.Opex(cple.capexech)[0]
        cple.co2ech = Cost.CO2(pourcentage, rendement, cple.puissE*h_annee*0.8)
        cple.ecototech = Cost.economie_tot(cple.puissE, pourcentage[0], pourcentage[1], pourcentage[2])

        cple.triech = cple.capexech / (cple.ecototech - cple.opexech)

        tempvan = (-1)*cple.capexech
        for l in range(1, (annee+1)) :
            tempvan += (cple.ecototech - cple.opexech) / ((1+act)**l)
        cple.vanech = tempvan

        cple.ipech = (cple.capexech + cple.vanech) / cple.capexech


    ########## Valeurs à retourner sur le plateforme : partie CAPEX ##########
    # Capex échangeurs uniquement
    objReseau.KPI.capex_ech = Cost.Capex(cout_ech)[0]
    print("capex_ech", objReseau.KPI.capex_ech)
    # Capex tuyauterie uniquement
    objReseau.KPI.capex_tuy = Cost.Capex(cout_tuy)[0]
    print("capex_tuy", objReseau.KPI.capex_tuy)
    # Capex pompes uniquement
    objReseau.KPI.capex_pompes = Cost.Capex(cout_pompe_invest)[0]
    print("capex_pompe", objReseau.KPI.capex_pompes)

    # Etude, install, réglage et admin du Capex
    objReseau.KPI.capex_piece = autre[0]
    print("cout_piece", objReseau.KPI.capex_piece)
    objReseau.KPI.capex_etude = autre[1]
    print("capex_etude", objReseau.KPI.capex_etude)
    objReseau.KPI.capex_install = autre[2]
    print("capex_install", objReseau.KPI.capex_install)
    objReseau.KPI.capex_reglage = autre[3]
    print("capex_reglage", objReseau.KPI.capex_reglage)
    objReseau.KPI.capex_admin = autre[4]
    print("capex_admin", objReseau.KPI.capex_admin)

    ########## Valeurs à retourner sur le plateforme : partie OPEX ##########
    objReseau.KPI.opex_pompes = Cout_fonc
    print(objReseau.KPI.opex_pompes)
    objReseau.KPI.opex_utilites = Cout_utilite
    print(objReseau.KPI.opex_utilites)
    objReseau.KPI.opex_maint = autre2[0]
    print(objReseau.KPI.opex_maint)
    objReseau.KPI.opex_entretien = autre2[1]
    print(objReseau.KPI.opex_entretien)

    # # Vérification des valeurs
    # sumcouttot = 0
    # sumtuy = 0
    # sumco2 = 0
    # sumcap = 0
    # sumop = 0
    # sumecotot = 0
    # listetri = []
    # listevan = []
    # listeip = []

    # for cp in objReseau.listeCouple :
    #     sumcouttot += cp.couttot
    #     sumtuy += cp.lontuy
    #     sumco2 += cp.co2ech
    #     sumcap += cp.capexech
    #     sumop += cp.opexech
    #     sumecotot += cp.ecototech
    #     listetri.append(cp.triech)
    #     listevan.append(cp.vanech)
    #     listeip.append(cp.ipech)
    
    # print("sumcouttot", sumcouttot)
    # print("sumtuy", sumtuy)
    # print("sumco2", sumco2)
    # print("sumcap", sumcap)
    # print("sumop", sumop)
    # print("sumecotot", sumecotot)
    # print(listetri)
    # print(listevan)
    # print(listeip)

    #   On termine le chronomètre
    #   fin=time.time()
    #   print("...l'algorithme a tourné pendant :",fin-debut,"s")
    
    print("\nFin d'ANAGREEN, merci d'avoir fait confiance à ALTRAN et surtout à Paulo")
    
    return None