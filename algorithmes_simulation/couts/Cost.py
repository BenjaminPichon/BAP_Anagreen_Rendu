# -*- coding: utf-8 -*-
import math
"""
Created on Wed Nov  7 14:46:50 2018

@author: sbouaraba

Modified by abonicel
"""

# class Cost:

def Cout(S,type_ech,ssfluxC,ssfluxF):
    # fonction donnant le cout d'un échangeur tubulaire ou à plaque
    
    # on cherche la température max de fonctionnement
    T_max = max(ssfluxC.Te,ssfluxF.Ts)
    # on cherche la pression max de service
    P_max = max(ssfluxC.press,ssfluxF.press)*1e-5
    
    # on détermine un facteur prennant en compte la température dans l'échangeur
    if T_max <= 100:
        f_T = 1
    elif T_max <= 300 and T_max > 100 :
        f_T = 1.6
    elif T_max > 300 and T_max < 500 :
        f_T = 2.1
    else:
        f_T = 1 # on ne connait pas de valeurs exactes
    
    # on détermine un facteur prennant en compte la pression de service
    if P_max <= 0.01 :
        f_P = 2
    elif P_max <= 0.1 and P_max > 0.01 :
        f_P = 1.3
    elif P_max <= 7 and P_max > 0.1 :
        f_P = 1
    elif P_max <= 50 and P_max > 7 :
        f_P = 1.5
    elif P_max > 50 :
        f_P = 1.9
    
    if type_ech=="Tubular":
        Cs=2134*S**0.514*0.91
    if type_ech=="Plated":
        Cs=6670*(S/37.8)**0.28
    
    if math.isnan(Cs*f_P*f_T):
        print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa')
        print(str(Cs)+" "+str(f_P)+" "+str(f_T))

    print("COOOOOOST :", ssfluxC.refFlux[0], ssfluxF.refFlux[0], S, Cs*f_P*f_T)
    return Cs*f_P*f_T

def Capex(Cout_invest):
    # fonction donnant le CAPEX 
    
    # Définition de coefficient pour le calcul du CAPEX
    Coeff_etude=0.6
    Coeff_instal=0.77
    Coeff_reglage=0.43
    Coeff_admin=0.04
    
    # on met tout dans une liste pour ajouter plus facilement
    Coeff=[1, Coeff_etude,Coeff_instal,Coeff_reglage,Coeff_admin]
    
    # on définit la liste des couts
    Cout=[]
    
    for coeff in Coeff:
        Cout.append(coeff*Cout_invest)
    
    # calcul du CAPEX
    CAPEX=sum(Cout)
    
    return CAPEX,Cout

def Opex(CAPEX):
    # fonction donnant l'Opex du système mis en place
    
    # Définition des coefficients pour le calcul
    Coeff_maint=0.06
#        Coeff_entretien=0.15
#        Coeff_taxe=0.03
#        Coeff_assurance=0.01
#        Coeff_frais=0.6
    Coeff_operating_supplies=0.1*Coeff_maint
    # on met tout dans une liste pour ajouter plus facilement
    Coeff=[Coeff_maint,Coeff_operating_supplies]
    
    # on définit la liste des couts
    Cout=[]
    
    for coeff in Coeff:
        Cout.append(coeff*CAPEX)
    
    OPEX=sum(Cout)
    
    return OPEX,Cout
    
def CO2(percentage,rendements,P):
    # percentage: (elec, gaz naturel,gpl,essence,diesel,charbon)
    # Prise en compte de la chaleur latente, si c'est sans, 10% d'écart environs
    PCI_gaz=1.111
    EF_comb_gaz=204
    EF_amont_gaz=37
    EF_total_gaz=EF_comb_gaz+EF_amont_gaz
    PCI_gpl=1.087
    EF_comb_gpl=204
    EF_amont_gpl=49
    EF_total_gpl=EF_comb_gpl+EF_amont_gpl
    PCI_essence=1.08
    EF_comb_essence=268.2
    EF_amont_essence=51.12
    EF_total_essence=EF_comb_essence+EF_amont_essence
    PCI_diesel=1.075
    EF_comb_diesel=272.524
    EF_amont_diesel=57.24
    EF_total_diesel=EF_comb_diesel+EF_amont_diesel
    PCI_charbon=1.052
    EF_comb_charbon=345.24
    EF_amont_charbon=28.5
    EF_total_charbon=EF_comb_charbon+EF_amont_charbon
    
    EF_elec=66.06  
    
    per_elec,per_comb_gaz,per_comb_gpl,per_comb_essence,per_comb_diesel,per_comb_charbon=percentage
    rend_therm,rend_elec=rendements
    
    CO2_red_elec=P*((1/rend_elec)*EF_elec*per_elec)
    CO2_red_gaz=P*(((1/rend_therm)*EF_total_gaz*(1/PCI_gaz)*per_comb_gaz))
    CO2_red_gpl=P*(((1/rend_therm)*EF_total_gpl*(1/PCI_gpl)*per_comb_gpl))
    CO2_red_essence=P*(((1/rend_therm)*EF_total_essence*(1/PCI_essence)*per_comb_essence))
    CO2_red_diesel=P*(((1/rend_therm)*EF_total_diesel*(1/PCI_diesel)*per_comb_diesel))
    CO2_red_charbon=P*(((1/rend_therm)*EF_total_charbon*(1/PCI_charbon)*per_comb_charbon))
    
    CO2=[CO2_red_elec,CO2_red_gaz,CO2_red_gpl,CO2_red_essence,CO2_red_diesel,CO2_red_charbon]
    
    CO2_red=sum(CO2)
    
    # valeur en gramme
    return CO2_red/1e9 # en kt
    
def economie(P):
    # ATTENTION P en kW
    
    # Cout Economisé
    h_annee=8760
    C_elec=0.0715 # en kWh
    C_gaz=0.075 # en kWh
    C_fioul=0.0917 # en kWh
#        C_chaleur=0.11
    facteur_utilisation = 1
    
    Econom_ele=h_annee*P*C_elec*facteur_utilisation
    Econom_gaz=h_annee*P*C_gaz*facteur_utilisation
    Econom_fioul=h_annee*P*C_fioul*facteur_utilisation
#        Econom_chaleur=h_annee*P*C_chaleur*(1/1000)
    
    return Econom_ele,Econom_gaz,Econom_fioul

def economie_tot(P,xElec,yGaz,zFioul):
    # ATTENTION P en kW
    
    # Cout Economisé
    h_annee=8760
    C_elec=0.0715 # en kWh
    C_gaz=0.075 # en kWh
    C_fioul=0.0917 # en kWh
#        C_chaleur=0.11
    facteur_utilisation = 1
    
    Econom_ele=h_annee*P*C_elec*xElec*facteur_utilisation
    Econom_gaz=h_annee*P*C_gaz*yGaz*facteur_utilisation
    Econom_fioul=h_annee*P*C_fioul*zFioul*facteur_utilisation
#        Econom_chaleur=h_annee*P*C_chaleur*(1/1000)
    
    return Econom_ele+Econom_gaz+Econom_fioul

def economie_disc(E):
    # ATTENTION P en kW
    
    # Cout Economisé
    C_elec=0.715 # en kWh
    C_gaz=0.075 # en kWh
    C_fioul=0.0917 # en kWh
#        C_chaleur=0.11
    
    Econom_ele=E*C_elec
    Econom_gaz=E*C_gaz
    Econom_fioul=E*C_fioul
#        Econom_chaleur=h_annee*P*C_chaleur*(1/1000)
    
    return Econom_ele,Econom_gaz,Econom_fioul

def economie_disc_tot(E,xElec,yGaz,zFioul):
    # ATTENTION E en kWh
    
    # Cout Economisé
    C_elec=0.0715 # en kWh
    C_gaz=0.075 # en kWh
    C_fioul=0.0917 # en kWh
#        C_chaleur=0.11
    
    Econom_ele=E*C_elec*xElec
    Econom_gaz=E*C_gaz*yGaz
    Econom_fioul=E*C_fioul*zFioul
#        Econom_chaleur=h_annee*P*C_chaleur*(1/1000)
    
    return Econom_ele+Econom_fioul+Econom_gaz