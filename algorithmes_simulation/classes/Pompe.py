# -*- coding: utf-8 -*-
"""
Created on Mon May 27 14:13:09 2019

@author: abonicel
"""

class Pompe:
    
    def __init__(self,puissance,coutInves,coutFonc,coutFoncAnnuel):
        self.puissance=puissance # puissance de la pompe en W
        self.coutInves=coutInves # cout d'achat de la pompe en €
        self.coutFonc=coutFonc # cout du fonctionnement en €
        self.coutFoncAnnuel=coutFoncAnnuel # cout du fonctionnement en €
        self.energie = 0 # énergie en kWh
        self.coutFoncAnnuelDisc = 0 # cout fonc à partir de l'énergie
        
def coutFonc(P):
    # fonction donnant le cout de fonctionnement de la pompe sur les années
    if P!=0:
        # rendement de la pompe
        eta_pompe=0.7
        # cout du kWh electrique
        C_kwh=0.07
        # cout du W electrique en fonctionnement
        facteur_utilisation=1 # facteur donnant le pourcentage de fonctionnement dans l'année
        C_w=C_kwh*8760/1000*facteur_utilisation
        # taux d'actualisation
        t=4/100
        # nombre d'année de fonctionnement
        n=30
        # facteur d'actualisation
        a=(1-(1+t)**(-n))/t
        # cout de fonctionnement
        return C_w/eta_pompe*P*a
    else:
        return 0

def coutFonc_annuel(P):
    # fonction donnant le cout de fonctionnement annuel pour le calcul de l'opex
    if P!=0:
        # rendement de la pompe
        eta_pompe=0.7
        # cout du kWh electrique
        C_kwh=0.07
        # cout du W electrique en fonctionnement
        facteur_utilisation=1 # facteur donnant le pourcentage de fonctionnement dans l'année
        C_w=C_kwh*8760/1000*facteur_utilisation
        # cout de fonctionnement
        return C_w/eta_pompe*P
    else:
        return 0

def coutFonc_annuel_disc(E):
    # fonction donnant le cout de fonctionnement annuel pour le calcul de l'opex
    if E!=0:
        # rendement de la pompe
        eta_pompe=0.7
        # cout du kWh electrique
        C_kwh=0.07
        # cout du W electrique en fonctionnement
#            facteur_utilisation=1 # facteur donnant le pourcentage de fonctionnement dans l'année
#            C_w=C_kwh*8760/1000*facteur_utilisation
        # cout de fonctionnement
        return C_kwh/eta_pompe*E
    else:
        return 0

def puissance_fonctionnement_normal(Q,dP):
    return Q*dP

def puissance_regu_pdc(Q,dP,dP_base):
    # fonction donnant la puissance de pompe nécessaire pour arriver aux pertes de charges avant modification
    P_pompe=Q*dP_base-Q*dP
    return max(-P_pompe,0)

def puissance_regu_p(Q,P,dP_base):
    # fonction donnant la puissance de pompe nécessaire pour arriver aux pertes de charges avant modification
    P_pompe=Q*dP_base-P
    return max(-P_pompe,0)

def coutInves(P):
    # P en W
    P_kW=P/1000
    if P!=0:
        return 144.28*P_kW+518.12
    else:
        return 0