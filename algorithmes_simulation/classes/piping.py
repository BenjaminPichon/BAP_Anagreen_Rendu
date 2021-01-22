# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 10:46:27 2019

@author: abonicel
"""
import numpy as np
from scipy.optimize import minimize

class piping:
    
    def __init__(self,Dt,et,ei,DN):
        # Attribut de l'objet piping : diametre tuyauterie, épaisseur tuyauterie, épaisseur calorifuge, coût tuyauterie, coût calorifuge, pertes de charge 
        self.diamTuy=Dt # diametre tuyauterie à définir dans le constructeur en m
        self.epTuy=et # epaisseur tuyauterie à définir dans le constructeur en m
        self.epIso=ei # epaisseur isolant à définir dans le constructeur en m
        self.DN=DN # DN de la tuyauterie
        self.coutTuy=1 # cout tuyauterie
        self.coutIso=2 # cout isolant
        self.pertes=0 # pertes de charge en Pa


    ####################Code concernant la tuyauterie########################
    
    def fitting(d):
        # calcul du cout d'achat de la tuyauterie
        return 2.8786*d+213.82

    def c_perte3(D,Q,rho):
        # calcul du cout des pertes de charge
        eta_pompe=0.7 # rendement de la pompe
        C_kwh=0.07 # prix du kWh d'électricité
        lamb=0.035 # facteur de friction
        facteur_utilisation=0.8 # pourcentage donnant l'utilisation de la pompe dans le process
        C_w=C_kwh*8760/1000*facteur_utilisation # prix du W électrique en considérant un fonctionnement
        V=4*Q/(np.pi*D**2) # vitesse du fluide
        t=4/100 # taux d'actualisation
        n=30 # nombre d'année d'investissement
        a=(1-(1+t)**(-n))/t # facteur d'actualisation
        return C_w/eta_pompe*1/8*rho*V**3*np.pi*D*lamb*a # cout des pertes de charge

    def c_tot3(D,Q,rho):
        # calcul du cout total pertes + tuyauterie
        return piping.c_perte3(D,Q,rho)+piping.fitting(D*10E2)

    def diametre_eco2(Q,rho):
        # calcul du diamètre économique à partir du débit
        def c_tot_deco(D):
            return np.abs(piping.c_tot3(D,Q,rho))
        # on cherche le minimum de la fonction
        d_eco=minimize(c_tot_deco,1).x
        # parfois ça prend la valeur négative du fait de la parité de la fonction
        if d_eco<0:
            d_eco=-d_eco
        # print('le diamètre éco est :',d_eco[0], "m")
        return d_eco[0] # diametre économique
    
    def section_droite(Q,P,rho): # Q en m3/s et P en Pa
        # Definitions des constantes
        sigma=300*10**6 # limite elastique acier
        Se=1.7 # coefficient de securite
        Z=1 # coefficient de controle
        C_corrosion = 0.001 # surépaisseur de corrosion
        C_tol=0.15 # pourcentage de tolerance

        sigma_max=sigma/Se # calcul contrainte max admissible
    
        D_int=piping.diametre_eco2(Q,rho) # calcul du diametre de tuyauterie

        P_calc=P*1 # la pression de calcul est égal à la pression dans la tuyauterie mais ça peut être différent 
        R_int=D_int/2 # calcul du rayon intérieur

        e=(P_calc*D_int/(2*sigma_max*Z+P_calc)+C_corrosion)*(1+C_tol) # calcul de l'épaisseur de tuyauterie dans le cas de tube mince
        if e/(R_int+e/2)>=0.1: #si le tube ne peut pas être considéré comme mince
            e=R_int*(np.sqrt((sigma_max+P)/(sigma_max-P))-1) #on calcule l'épaisseur de tuyauterie
#            print("le diamètre interieur vaut:",D_int*1E3, "mm")
#            print("l'épaisseur de la tuyauterie est ",e*1E3,"mm")
            return [D_int,e] # renvoie le diamètre intérieur et l'épaisseur
#        print("le diamètre interieur vaut:",D_int*1E3, "mm")
#        print("l'épaisseur de la tuyauterie est ",e*1E3, "mm")
        return [D_int,e] # renvoie le diamètre intérieur et l'épaisseur
        
        
    def section_coudee(Q,P,r,rho): # Q en m3/s, P en Pa et r le coefficient de courbure r*Dm
        [D_int,e_droit]=piping.section_droite(Q,P,rho) # calcul du diametre et de l'épaisseur
        K=(2*r-1/2)/(2*r-1) # coefficient pour le calcul de l'épaisseur du coude
        e=K*e_droit # epaisseur du coude
#        print("le diamètre interieur vaut:",D_int*1E3, "mm")
#        print("l'épaisseur de la tuyauterie est ",e*1E3, "mm")
        return [D_int,e] #renvoie le diametre intérieur et l'épaisseur du coude
                
    def choix_taille(L_c): # liste avec 2 valeurs le diametre et l'epaisseur
        # renvoie une liste avec le diametre, l'épaisseur et le DN
        L=[L_c[0]*1000,L_c[1]*1000] #on met les valeurs en mm
        # on effectue une serie de test pour trouver la valeur reglementée
        if L[0]<=10.2:
            if L[1]<=1.6:
                return [10.2E-3,1.6E-3,6]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>10.2 and L[0]<=13.5:
            if L[1]<=1.6:
                return [13.5E-3,1.6E-3,8]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>13.5 and L[0]<=17.2:
            if L[1]<=1.6:
                return [17.2E-3,1.6E-3,10]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>17.2 and L[0]<=21.3:
            if L[1]<=1.6:
                return [21.3E-3,1.6E-3,15]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>21.3 and L[0]<=26.9:
            if L[1]<=1.6:
                return [26.9E-3,1.6E-3,20]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>26.9 and L[0]<=33.7:
            if L[1]<=1.6:
                return [33.7E-3,1.6E-3,25]
            elif L[1]>1.6 and L[1]<=2.0:
                return [33.7E-3,2E-3,25]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>33.7 and L[0]<=42.4:
            if L[1]<=1.6:
                return [42.4E-3,1.6E-3,32]
            elif L[1]>1.6 and L[1]<=2.0:
                return [42.4E-3,2E-3,32]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>42.4 and L[0]<=48.3:
            if L[1]<=1.6:
                return [48.3E-3,1.6E-3,40]
            elif L[1]>1.6 and L[1]<=2.0:
                return [48.3E-3,2E-3,40]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>48.3 and L[0]<=60.3:
            if L[1]<=1.6:
                return [60.3E-3,1.6E-3,50]
            elif L[1]>1.6 and L[1]<=2.0:
                return [60.3E-3,2E-3,50]
            elif L[1]>2.0 and L[1]<=2.3:
                return [60.3E-3,2.3E-3,50]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>60.3 and L[0]<=76.1:
            if L[1]<=1.6:
                return [76.1E-3,1.6E-3,65]
            elif L[1]>1.6 and L[1]<=2.3:
                return [76.1E-3,2E-3,65]
            elif L[1]>2.3 and L[1]<=2.6:
                return [76.1E-3,2.6E-3,65]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>76.1 and L[0]<=88.9:
            if L[1]<=2.0:
                return [88.9E-3,2E-3,80]
            elif L[1]>2.0 and L[1]<=2.3:
                return [88.9E-3,2.3E-3,80]
            elif L[1]>2.3 and L[1]<=2.9:
                return [88.9E-3,2.9E-3,80]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>88.9 and L[0]<=114.3:
            if L[1]<=2.0:
                return [114.3E-3,2E-3,100]
            elif L[1]>2.0 and L[1]<=2.6:
                return [114.3E-3,2.6E-3,100]
            elif L[1]>2.6 and L[1]<=2.9:
                return [114.3E-3,2.9E-3,100]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>114.3 and L[0]<=139.7:
            if L[1]<=2.0:
                return [139.7E-3,2E-3,125]
            elif L[1]>2.0 and L[1]<=2.6:
                return [139.7E-3,2.6E-3,125]
            elif L[1]>2.6 and L[1]<=3.2:
                return [139.7E-3,3.2E-3,125]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>139.7 and L[0]<=168.3:
            if L[1]<=2.0:
                return [168.3E-3,2E-3,150]
            elif L[1]>2.0 and L[1]<=2.9:
                return [168.3E-3,2.9E-3,150]
            elif L[1]>2.9 and L[1]<=3.2:
                return [168.3E-3,3.2E-3,150]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>168.3 and L[0]<=219.1:
            if L[1]<=2.0:
                return [219.1E-3,2E-3,200]
            elif L[1]>2.0 and L[1]<=2.9:
                return [219.1E-3,2.9E-3,200]
            elif L[1]>2.9 and L[1]<=3.6:
                return [219.1E-3,3.6E-3,200]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>219.1 and L[0]<=273:
            if L[1]<=2.0:
                return [273E-3,2E-3,250]
            elif L[1]>2.0 and L[1]<=3.2:
                return [273E-3,3.2E-3,250]
            elif L[1]>3.2 and L[1]<=4.0:
                return [273E-3,4.0E-3,250]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>273 and L[0]<=323.9:
            if L[1]<=2.6:
                return [323.9E-3,2.6E-3,300]
            elif L[1]>2.6 and L[1]<=3.6:
                return [323.9E-3,3.6E-3,300]
            elif L[1]>3.6 and L[1]<=4.5:
                return [323.9E-3,4.5E-3,300]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>323.9 and L[0]<=355.6:
            if L[1]<=2.6:
                return [355.6E-3,2.6E-3,350]
            elif L[1]>2.6 and L[1]<=3.6:
                return [355.6E-3,3.6E-3,350]
            elif L[1]>3.6 and L[1]<=4.5:
                return [355.6E-3,4.5E-3,350]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>355.6 and L[0]<=406.4:
            if L[1]<=2.6:
                return [406.4E-3,2.6E-3,400]
            elif L[1]>2.6 and L[1]<=4.0:
                return [406.4E-3,4.0E-3,400]
            elif L[1]>4.0 and L[1]<=5.0:
                return [406.4E-3,5.0E-3,400]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>406.4 and L[0]<=457:
            if L[1]<=3.2:
                return [457E-3,3.2E-3,450]
            elif L[1]>3.2 and L[1]<=4.5:
                return [457E-3,4.5E-3,450]
            elif L[1]>4.5 and L[1]<=5.0:
                return [457E-3,5.0E-3,450]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>457 and L[0]<=508:
            if L[1]<=3.2:
                return [508E-3,3.2E-3,500]
            elif L[1]>3.2 and L[1]<=5.0:
                return [508E-3,5.0E-3,500]
            elif L[1]>5.0 and L[1]<=6.3:
                return [508E-3,6.3E-3,500]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>508 and L[0]<=610:
            if L[1]<=3.2:
                return [610E-3,3.2E-3,600]
            elif L[1]>3.2 and L[1]<=5.6:
                return [610E-3,5.6E-3,600]
            elif L[1]>5.6 and L[1]<=6.3:
                return [610E-3,6.3E-3,600]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>610 and L[0]<=711:
            if L[1]<=4.0:
                return [711E-3,4.0E-3,700]
            elif L[1]>4.0 and L[1]<=6.3:
                return [711E-3,6.3E-3,700]
            elif L[1]>6.3 and L[1]<=7.1:
                return [711E-3,7.1E-3,700]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>711 and L[0]<=813:
            if L[1]<=4.0:
                return [813E-3,4.0E-3,800]
            elif L[1]>4.0 and L[1]<=6.3:
                return [813E-3,6.3E-3,800]
            elif L[1]>6.3 and L[1]<=7.1:
                return [813E-3,7.1E-3,800]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>813 and L[0]<=914:
            if L[1]<=4.0:
                return [914E-3,4.0E-3,900]
            elif L[1]>4.0 and L[1]<=8.0:
                return [914E-3,8.0E-3,900]
            elif L[1]>8.0 and L[1]<=8.8:
                return [914E-3,8.8E-3,900]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        elif L[0]>914 and L[0]<=1016:
            if L[1]<=4.0:
                return [1016E-3,4.0E-3,1000]
            elif L[1]>4.0 and L[1]<=8.8:
                return [1016E-3,8.8E-3,1000]
            elif L[1]>8.8 and L[1]<=10.0:
                return [1016E-3,10E-3,1000]
            else:
                print("l'épaisseur n'est pas valide")
                return False
        else:
            # print("pas de taille standard connue, on conserve la valeur calculée")
            return [L[0]/1000,L[1]/1000,"Supérieur à 1000"]
    
    ####################Code concernant le calorifuge########################
    
    def chaleur(lamb,R_ext,T,Ta,e):
        # coefficient de convection extérieur
        h_ext=5 
        # résistance de conduction linéaire
        R_cond=1/lamb*np.log(1+e/R_ext) 
        # résistance de convection linéaire
        R_conv=1/(h_ext*(R_ext+e)) 
        # Chaleur perdue linéaire
        Q=2*np.pi*(T-Ta)/(R_cond+R_conv)
        return Q

    def cout_chaleur_ex(lamb,R_ext,T,Ta,e):
        # taux d'actualisation
        t=4/100
        # nombre d'année 
        n=30
        # facteur d'actualisation 
        a=(1-(1+t)**(-n))/t
        # prix du kWh de GN
        C_kwh=0.04378
        # prix du W de GN
        facteur_utilisation=0.8
        C_w=C_kwh*8760/1000*facteur_utilisation
        # fonction calculant un facteur exergétique
        def exergie(x):
            return 1-(293)/x
        # coefficient exergétique
        eta_ex=exergie(T)
        # cout exergétique du GN
        C_w=C_w*eta_ex/(1-eta_ex)
        # Chaleur perdue
        Q=piping.chaleur(lamb,R_ext,T,Ta,e)
        # Cout total de la chaleur linéaire
        return Q*a*C_w
    
    def cout_calo_V(R_ext,e): # rayon exterieur du de la tuyauterie, epaisseur calorifuge
        # Volume linéaire 
        V=(R_ext*1000+e*1000)**2-(R_ext*1000)**2
        # cout liénaire de la tuyauterie
        return 0.0022*V+10.176


    def cout_tot(lamb,R_ext,T,Ta,e): # cout total de la tuyauterie
        return piping.cout_chaleur_ex(lamb,R_ext,T,Ta,e)+piping.cout_calo_V(R_ext,e)

    def minimisation(f,a): # fonction de minimisation à améliorer
        # pas de recherche de min fixe
        delta_x=1E-5
        # recherche du min par changement de croissance de la courbe départ décroissant puis croissant
        while f(a)>f(a+delta_x):
            a=a+delta_x
        # renvoie la valeur pour laquelle la fonction f est minimale
        return a

    def epaisseur_eco(lamb,R_ext,T,Ta):
        # fonction à minimiser pour obtenir l'épaisseur économique
        def cout_tot_min(e):
            return piping.cout_tot(lamb,R_ext,T,Ta,e)
        # minimisation de la fonction
        res=piping.minimisation(cout_tot_min,10E-3)
#        print('l épaisseur éco est :',res*1000, "mm")
#        print('le cout du calorifugeage est :',piping.cout_calo_V(R_ext,res),'€/m')
        # renvoie l'épaisseur économique de calorifuge
        return res

    def temp_ext(lamb,R_ext,T,Ta,e): #calcul température à la paroi du tuyau
        # coefficient de transfert convection extérieure
        h_ext=5
        # résistance de conduction
        R_cond=1/lamb*np.log(1+e/R_ext)*1/(2*np.pi)
        # résistance de convection extérieure
        R_conv=1/(h_ext*(R_ext+e))*1/(2*np.pi)
        # calcule de la température à la paroi en K
        T_ext=T-(T-Ta)*R_cond/(R_cond+R_conv)
#        print("la température du tuyau ext est :", T_ext, "K")
        return T_ext

    def dichotomie(f,a,b): # algortihme de dichotomie classique avec une fonction et les deux bornes
        m=(a+b)/2
        while np.abs(b-a)>1E-5:
            m=(a+b)/2
            if f(a)*f(m)>=0:
                a=m
            else:
                b=m
        return m

    def epaisseur_min(lamb,R_ext,T,Ta): #fonction principale donnant l'épaisseur minimale en vérifiant la condition de température à la paroi
        # calcule de l'épaisseur économique
        e=piping.epaisseur_eco(lamb,R_ext,T,Ta)
        # calcule de la température à la paroi
        Te=piping.temp_ext(lamb,R_ext,T,Ta,e)
        # Verifie si la température est trop importante
        if (Te-273)>60:
            # Fonction dont on cherche le zéro pour trouver l'épaisseur de calorifuge pour arriver au 60°C à la paroi
            def fun(x):
                # coefficient de transfert convection extérieur
                h_ext=5
                # résistance de conduction
                R_cond=1/lamb*np.log(1+x/R_ext)*1/(2*np.pi)
                # résistance de convection
                R_conv=1/(h_ext*(R_ext+x))*1/(2*np.pi)
                # Renvoie la différence entre la température à la paroi et les 60°C
                return T-(T-Ta)*R_cond/(R_cond+R_conv)-(273+60)
            # Calcule de l'épaisseur minimale pour satisfaire la condition des 60°C
            e_min=piping.dichotomie(fun,10E-3,1)
#            piping.temp_ext(lamb,R_ext,T,Ta,e_min)
#            print("l épaisseur min est :", e_min*1000, "mm")
            return e_min
        else:
#            print("l épaisseur min est l épaisseur éco:", e*1000, "mm")
            return e
    