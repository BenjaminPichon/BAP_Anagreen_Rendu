# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 09:03:15 2018

@author: sbouaraba

Modified by abonicel
"""

# -*- coding: utf-8 -*-
#"""
#Éditeur de Spyder
#"
#Programme échangeur de chaleur
#Cas ou le fluide froid est à l'interieur et le fluide chaud à l'exterieur
#Valeurs issues du site

import numpy as np
import random

from predimensionnement import Fonctions as fct, Pertes, pertes_singulieres

class Echangeurs:
    
        def __init__(self,typee,surfEch,cout,perteChaud,perteFroid):
                self.typee=typee
                self.surfEch=surfEch
                self.cout=cout
                self.perteChaud=perteChaud
                self.perteFroid=perteFroid
                self.div=False
                # self.Qdiv=0
                self.pompeSplitChaud = 0
                self.pompeSplitFroid = 0


#Exemple pour des valeur prise dans des abaques AIR cependant c'est à Pression ambiante
# Or la pression sont bcp plus élevé dans le cas réel
def Coaxial(Dc,Df,Cp_c,Cp_f,Tc_e,Tc_s,Tf_e,Tf_s,D_1=1,D_2=1.2,D_3=1,mu_c=1,mu_f=1,rho_c=1,rho_f=1,L=1,k_pipe=380,k_c=1,k_f=1):
   
#Prandtl viscous diffusion rate/ thermal diffusion rate = Cp * dyanamic viscosity / thermal conductivity
#Pr << 1 means thermal diffusivity dominates
#Pr >> 1 means momentum diffusivity dominates
        #On suppose que le fluide intérieur est le froid et l'éxtérieur est le chaud
        Pr_int= fct.Fonctions.Prandtl(mu_f,Cp_f,k_f)
        Pr_ext= fct.Fonctions.Prandtl(mu_c,Cp_c,k_c)
#Calculs Reynolds échangeur simple coaxial
        U_int=(4*Df)/(np.pi*(D_1**2)) 
        U_ext=(4*Dc)/(np.pi*((D_3**2)))
        Re_int=fct.Fonctions.Reynolds(U_int,D_1,rho_f,mu_f)
        Re_ext=fct.Fonctions.Reynolds(U_ext,D_2,rho_c,mu_c)
        print("Reynolds ext :",Re_ext)
#A l'intérieur du/des tubes :
        Nu_int=fct.Fonctions.Nusselt_int(Re_int,Pr_int,D_1,L)
#A l'extérieur des tubes.
        Nu_ext=fct.Fonctions.Nusselt_ext(Re_ext,Pr_ext)
#Resultats pour h1 et h2
        h_int=fct.Fonctions.h_calculation(Nu_int,k_f,D_1)
        h_ext=fct.Fonctions.h_calculation(Nu_ext,k_c,D_2)
        R_encrass= 1e-5 #input("Resistance d'encrassement : ");
        R_int_conv=D_2/(h_int*D_1)
        R_pipe=np.log((D_2)/D_1)/(k_pipe*2*np.pi*L)
        R_ext_conv=1/(h_ext)
        R_tot=R_int_conv+R_pipe+R_ext_conv+R_encrass
        h_global=1/R_tot
        print("Coefficient d'échange global :",h_global,"\n")
#Cas Co-Courant
#        DT_m=fct.Fonctions.DT_Co_courant(Tc_e,Tc_s,Tf_e,Tf_s)
#Calculer S Co-courant
        Phi=Dc*Cp_c*(Tc_e-Tc_s)*rho_c
#        S1=1.3*Phi/(h_global*DT_m)
        S1=1
#        print("la surface de l'échangeur coaxial en co-courant est de ",S1 ,"m^2 \n")
        print("Puissance :",Phi,"\n")
#Cas contre-Courant
        DT_m=fct.Fonctions.DT_Contre_courant(Tc_e,Tc_s,Tf_e,Tf_s)
#Calculer S contre-courant
        S2=1.3*Phi/(h_global*DT_m)
        print("la surface de l'échangeur coaxial en contre-courant est de ",S2 ,"m^2 \n")
        
        price1=30*S1+500
        price2=30*S2+500
        
        return(Phi,h_global,S1,S2,L,price1,price2) #Phi deja dans couple pas besoin de le recalculer, h_global pas intéressant
  

def Plated_1986(Dc,Df,Cp_c,Cp_f,k_c,k_f,Tc_e,Tc_s,Tf_e,Tf_s,mu_f=1,mu_c=1,rho_c=1,rho_f=1,e_k=3e-5,DP_max=80):
    #Echangeur à plaques
    #Dc en kg/h
    #viscosité mu en Poiseuille
    #DP_max est la pertes de charge max en kPa
        Qc=Dc
        Qf=Df
        if Qc>Qf:
            DP_c=DP_max
            DP_f=DP_c*((Qf/Qc)**2)
#            DP_f=DP_f*0.6 #facteur de correction si ce n'est pas les memes fluides
        else:
            DP_f=DP_max
            DP_c=DP_f*((Qc/Qf)**2)
#            DP_c=DP_c*0.6 #facteur de correction si ce n'est pas les memes fluides

        Pr_f= ((mu_f/1000)*(Cp_f))/(k_f)
        Pr_c= ((mu_c/1000)*(Cp_c))/(k_c)


        DT_m=fct.Fonctions.DT_Contre_courant(Tc_e,Tc_s,Tf_e,Tf_s)

        Cs_f=(234*((rho_f*DP_f)/(mu_f**2))**0.3275)/(Pr_f**(-1/3))
        Cs_c=(234*((rho_c*DP_c)/(mu_c**2))**0.3275)/(Pr_c**(-1/3))

        h_f=Cs_f*k_f
        h_c=Cs_c*k_c
        R_encrass=10**-4
        h_global=1/((1/h_c)+(1/h_f)+e_k+R_encrass)
        Phi=Qc*rho_c*Cp_c*(Tc_e-Tc_s)/3600
        S=Phi/(h_global*DT_m)

#        print("la surface de l'échangeur à plaque en contre-courant est de ",S ,"m^2 \n")
#        print("la perte de charge coté chaud",DP_c*0.01,"bar et coté froid",DP_f*0.01,"bar\n")
#        print("la puissance de l'échangeur est",Phi/1000,"kW\n")
        return S,DP_c*1000,DP_f*1000,Phi

#    def Plated_1986(Dc,Df,Cp_c,Cp_f,k_c,k_f,Tc_e,Tc_s,Tf_e,Tf_s,mu_f=1,mu_c=1,rho_c=1,rho_f=1,e_k=10**-4,DP_max=100000):
##Echangeur à plaques
##Dc en kg/h
##viscosité mu en Poiseuille
##DP_max est la pertes de charge max en Pascal
#        Qc=Dc/rho_c
#        Qf=Df/rho_f
#        DP_c=DP_max
#        DP_f=DP_c*((Qf/Qc)**2)
#        DP_f=DP_f*0.6 #facteur de correction si ce n'est pas les memes fluides
#
#        Pr_f= ((mu_f/1000)*(Cp_f))/(k_f)
#        Pr_c= ((mu_c/1000)*(Cp_c))/(k_c)
#
#
#        DT_m=fct.Fonctions.DT_Contre_courant(Tc_e,Tc_s,Tf_e,Tf_s)
#
#        Cs_f=(234*((rho_f*DP_f)/(mu_f**2))**0.3275)/(Pr_f**(-1/3))
#        Cs_c=(234*((rho_c*DP_c)/(mu_c**2))**0.3275)/(Pr_c**(-1/3))
#
#        h_f=Cs_f*k_f
#        h_c=Cs_c*k_c
#        R_encrass=10**-5
#        h_global=1/(1/h_c)+(1/h_f)+e_k+R_encrass
#        Phi=Qc*rho_c*Cp_c*(Tc_e-Tc_s)
#        S=1.3*Phi/(h_global*DT_m)
#
#        print("la surface de l'échangeur à plaque en contre-courant est de ",S ,"m^2 \n")
#
#        return(Phi,h_global,S)

def Tubular(Dc,Df,Cp_c,Cp_f,Tc_e,Tc_s,Tf_e,Tf_s,D_1=0.016,D_2=0.02,D_3=0.9,mu_c=1,mu_f=1,rho_c=1,rho_f=1,L=1,k_pipe=50,k_c=1,k_f=1):
#     def Tubular(Dc,Df,Cp_c,Cp_f,Tc_e,Tc_s,Tf_e,Tf_s,D_1,D_2,D_3,mu_c,mu_f,rho_c,rho_f,L,k_pipe,k_c,k_f):
        Pr_int= fct.Fonctions.Prandtl(mu_f,Cp_f,k_f)
        Pr_ext= fct.Fonctions.Prandtl(mu_c,Cp_c,k_c)
#Calculs h1 et h2 échangeur simple coaxial
        U_int=(4*Df)/(np.pi*(D_1**2)) 
        U_ext=(4*Dc)/(np.pi*((D_3**2)))
        Re_int=fct.Fonctions.Reynolds(U_int,D_1,rho_f,mu_f)
        Re_ext=fct.Fonctions.Reynolds(U_ext,D_2,rho_c,mu_c)
        #print("Reynolds ext :",Re_ext)
#A l'intérieur du/des tubes :
        Nu_int=fct.Fonctions.Nusselt_int(Re_int,Pr_int,D_1,L)
#A l'extérieur des tubes.
        Nu_ext=fct.Fonctions.Nusselt_ext(Re_ext,Pr_ext)
#Resultats pour h1 et h2
        h_int=fct.Fonctions.h_calculation(Nu_int,k_f,D_1)
        h_ext=fct.Fonctions.h_calculation(Nu_ext,k_c,D_2)
        R_encrass= 1e-5 #input("Resistance d'encrassement : ");
        R_int_conv=D_2/(h_int*D_1)
        R_pipe=np.log((D_2)/D_1)/(k_pipe*2*np.pi*L)
        R_ext_conv=1/(h_ext)
        R_tot=R_int_conv+R_pipe+R_ext_conv+R_encrass
        h_global=1/R_tot
        #print("Coefficient d'échange global :",h_global,"\n")
#Cas contre-Courant
        DT_m=fct.Fonctions.DT_Contre_courant(Tc_e,Tc_s,Tf_e,Tf_s)
#Calculer S Co-courant
        Phi=Dc*Cp_c*(Tc_e-Tc_s)*rho_c
        #print("Puissance :",Phi,"\n")
#Calcul du facteur de correction
        F=fct.Fonctions.F_factor_1pC_2nT(Tc_e,Tc_s,Tf_e,Tf_s)
#Calculer S contre-courant
#        print("phi",Phi)
        # print('PHI NEGATIF ? : ' +str(Dc)+", "+str(Cp_c)+", "+str(Tc_e)+", "+str(Tc_s)+", "+str(rho_c)+", ")
        # print('TUBULAR S: '+str(Phi)+", "+str(F)+", "+str(h_global)+", "+str(DT_m)+", ")
        S=1.3*Phi/(F*h_global*DT_m)
        #print("la surface de l'échangeur tubulaire 1 passe Calandre 2n passes tubes en contre-courant est de ",S ,"m^2 \n")
        #Price en attendant juste pour indication
        A_shell_tuyau=np.pi*(D_3-4*D_2)**2/4
        A_tube_ext_pas=np.pi*(1.25*D_2)**2/4
        N_tuyau=np.floor(A_shell_tuyau/(2*A_tube_ext_pas))
#        print(N_tuyau)
        qv_f_tuy=Df/N_tuyau
#        v_t=qv_f_tuy*4/(np.pi*D_1**2)
#        print("vitesse dans le tuyau :",v_t,"m/s")
        L_tube=L
#        print("la longueur des tubes est :",L_tube,"m")
        L_droit=0.8465*L_tube
        k=0.15 # rugosité des tubes
        P_line_f=Pertes.perte_lin_qv(L_droit,D_1,qv_f_tuy,k,rho_f,mu_f)*2
#        print("perte dans les tuyaux linéaire :",P_line_f,"Pa")
        A_tube_int=np.pi*D_1**2/4
        P_coude_f=pertes_singulieres.Coude_arrondi(np.pi,0.1635*L_tube/(np.pi),D_2)*rho_f*qv_f_tuy**2/(2*A_tube_int**2)
#        print("perte singulière dans les tuyaux :",P_coude_f,"Pa")
#        P_in_out=4*2*(rho_f*v_t**2/2)
        P_in=pertes_singulieres.Elargissement(168.3e-3,D_3/2)*rho_f*(Df/(np.pi*168.3e-3**2/4))**2/2
        P_out=pertes_singulieres.Retrecissement(D_3/2,168.3e-3)*rho_f*(Df/(np.pi*168.3e-3**2/4))**2/2
        #print(pertes_singulieres.Coude_arrondi(np.pi,0.25*L/(np.pi),D_2))
#        dP_tuy=(P_line_f+P_coude_f+P_in_out)
        dP_tuy=(P_line_f+P_coude_f+P_in+P_out)
        
        #Calcul de la perte de charge dans la calandre avec le fluide chaud y circulant
        m_dot_c=Dc*rho_c
        pas=1.25*D_2
        #D_shell=np.sqrt(2)*((2*N_tuyau+1)*(pas-D_2)+2*N_tuyau*D_2)
        #print("Diamètre calandre calcul:",D_shell,"m")
        B_spacing=1/5*D_3
        N_chicane=np.floor(L_droit/B_spacing)-1
        L_chicane=B_spacing
        S_shell=D_3*L_chicane*(pas-D_2)/pas
        G_shell=m_dot_c/S_shell
        #Si configuration carré
        Coeff=1
        #Si configuration triangle
        #Coeff=0.86
        D_eq_shell=4*(Coeff*pas**2-np.pi*D_2**2/4)/(np.pi*D_2)
        Re=rho_c*Dc*D_eq_shell/(mu_c*S_shell)
        #k_shell=0.03E-3
        f=0.24*Re**(-0.2)
        dP_shell=2*f*G_shell**2*D_3*(N_chicane+1)/(rho_c*D_eq_shell)
        # le calcul dans la calandre n'est pas vraiment bon on limite la perte de charge max à 5 bars
#        dp_random = random.randint(1e3,1e5)
#        if dP_shell>dp_random:
#            dP_shell=dp_random
        dP_shell = 8e4
        
        # print("ECH.TUBULAR: "+str(S)+", "+str(L)+", "+str(dP_tuy)+", "+str(dP_shell)+", ")
        return S,L,dP_tuy,dP_shell
          
def Plated(Dc,Df,Cp_c,Cp_f,k_c,k_f,Tc_e,Tc_s,Tf_e,Tf_s,mu_f,mu_c,rho_c,rho_f,e_k,e,plis,l,L,alpha,Dp_c,Dp_f):
#Echangeur à plaques
#Dc en m^3/s
#viscosité mu en Pa.s

            
        Uc=Dc/(e*plis)
        Uf=Df/(e*plis)
        Re_f=(rho_f*Uf*l*np.cos(alpha))/mu_f
        Re_c=(rho_c*Uc*l*np.cos(alpha))/mu_c
#            print("Re froid :",Re_f)
#            print("Re_chaud :",Re_c)
#            fc=fct.Fonctions.f_factor(Re_c,alpha)
#            ff=fct.Fonctions.f_factor(Re_f,alpha)
#            DP_c=4*fc*rho_c*(Uc**2)*L/(2*plis +2*e) 
#            DP_f=4*ff*rho_f*(Uf**2)*L/(2*plis +2*e)
        Pr_f=fct.Fonctions.Prandtl(mu_f,Cp_f,k_f)
        Pr_c=fct.Fonctions.Prandtl(mu_c,Cp_c,k_c)

        Nu_c=fct.Fonctions.Nusselt_plated(Re_c,Pr_c,alpha)
        Nu_f=fct.Fonctions.Nusselt_plated(Re_f,Pr_f,alpha)
        DT_m=fct.Fonctions.DT_Contre_courant(Tc_e,Tc_s,Tf_e,Tf_s)
        h_int=fct.Fonctions.h_calculation(Nu_f,k_f,2*plis+2*e) #not sure
        h_ext=fct.Fonctions.h_calculation(Nu_c,k_c,2*plis+2*e) #not sure
        R_encrass=10**-5
        h_global=1/((1/h_int)+(1/h_ext)+e_k+R_encrass)
        Phi=Dc*rho_c*Cp_c*(Tc_e-Tc_s)
        S=1.3*Phi/(h_global*DT_m)


#        Dh=2*plis
#        Nplaque=np.ceil(S/(L*l))
#        #print(Nplaque)
#        #calcule du nombre de canaux
#        if Nplaque%2==1:
#            Npasse=int((Nplaque-1)/2)
#        else:
#            Npasse=int(Nplaque/2)
#        #print(Npasse)
#        #calcul du débit dans les canaux pour le fluide chaud
#        Q_canal_c=Dc/(Npasse*Nplaque)
#        #calcul du débit dans les canaux pour le fluide froid
#        Q_canal_f=Df/(Npasse*Nplaque)
#        v_c=4*Q_canal_c/(np.pi*Dh**2)
#        v_f=4*Q_canal_f/(np.pi*Dh**2)
##        v_c=Q_canal_c/(h_canal*l_canal)
##        v_f=Q_canal_f/(h_canal*l_canal)
#        #calcul du Reynolds
#        Re_c=rho_c*Dh*v_c/mu_c
#        #print(Re_c)
#        Re_f=rho_f*Dh*v_f/mu_f
#        
#        f_c=2*Nu_c/(Re_c*Pr_c**(1/3))
#        #f_c=fct.Fonctions.f_factor(Re_c,alpha)
#        #f_c=0.0791*Re_c**(-0.25)
#        #f_c=f_f=0.035/4
##        print("friction factor chaud:",f_c)
#        
##        print(L_canal_moy)
#        L_canal_moy=0.8*l/np.sin(alpha*np.pi/180)
##        print("la longueur du canal est :",L_canal_moy)
##        print("le diametre hydro est:",Dh)
#        dP_canal_c=2*f_c*v_c**2*L_canal_moy/Dh*rho_c
#        #print("perte de charge c canal:",dP_canal_c,"Pa")
#        dP_c=dP_canal_c*1.2 #on considère les pertes dans les canaux menant à la plaque 
#        
#        #On calcule les pertes de charges dans les ports 
#        Gp_c=Dc*rho_c/(np.pi*Dp_c**2/4)
#        dP_p_c=1.3*Gp_c**2/(2*rho_c)
##        print("perte de charge c ports:",dP_p_c,"Pa")
#        #Perte de charge total du fluide chaud
#        dP_c=dP_p_c+dP_c
#        
#        #On calcule les pertes de charge pour le fluide froid
#        f_f=2*Nu_f/(Re_f*Pr_f**(1/3))
#        #f_f=fct.Fonctions.f_factor(Re_f,alpha)
#        #f_f=0.0791*Re_f**(-0.25)
##        print("friction factor froid:",f_f)
#        dP_canal_f=2*f_f*v_f**2*L_canal_moy/Dh*rho_f
##        print("perte de charge f canal:",dP_canal_f,"Pa")
#        dP_f=dP_canal_f*1.4
#        #On calcule les perte de charge dans les ports
#        Gp_f=Df*rho_f/(np.pi*Dp_f**2/4)
#        dP_p_f=1.3*Gp_f**2/(2*rho_f)
##        print("perte de charge f ports:",dP_p_f,"Pa")
#        #Perte de charge total du fluide chaud
#        dP_f=dP_p_f+dP_f
        
        #Pas sur de la formulation des pertes de charges on prend des valeurs arbitraires
        if S>15:
            dP_c=dP_f=8e4
        else:
            dP_c=dP_f=8e3
#        dP_c=dP_f=random.randint(1e3,1e5)
        
        return S,dP_c,dP_f    