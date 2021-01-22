# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 16:46:39 2018

@author: sbouaraba

Modified by abonicel
"""
import numpy as np

from predimensionnement import frottement


# class Pertes:
    
def perte_lin_qv(L,D,qv,k,rho,mu): 
    S=np.pi*(D**2)/4.;U=qv/S;Re=(rho*U*D)/mu
    dP=frottement.frottement.Ffrot(Re,k)*(L/D)*0.5*rho*(U**2) #Darcy Weisbach
    
    return (dP)


def Pertes_de_chaleur_linéaire(Debit,T_int,T_ext,D_1,D_2,D_3,L,Cp_int,rho_int,lamb_int,lamb_iso): 
    #Voir la note de calcul pour les explications
    def g(D_1,D_2,D_3,lamb_int,lamb_iso,q,rho,cp):
        hext=5
        #résistance à l'encrassement pas prise en compte car pas d'interet dans un premier temps
        #R_encrassement=2e-4
        #Rth=((D_1/2)**2*lamb_int*(1/lamb_iso*np.log(D_3/D_2)+1/(hext*D_3/2)+R_encrassement*(D_1/2)))
        Rth=((1/lamb_iso*np.log(D_3/D_2)+1/(hext*D_3/2)))
        m_dot=q*rho
        C1=m_dot*cp/(lamb_int*np.pi*(D_1/2)**2)
        C2=2/(lamb_int*np.pi*(D_1/2)**2*Rth)
        return 0.5*(C1-np.sqrt((C1)**2+4*C2))
#        print(g(D_1,D_2,D_3,lamb_int,lamb_iso,Debit,rho_int,Cp_int))
#        print(g(D_1,D_2,D_3,lamb_int,lamb_iso,Debit,rho_int,Cp_int)*L)
#        print(np.exp(g(D_1,D_2,D_3,lamb_int,lamb_iso,Debit,rho_int,Cp_int)*L))
    T_sortie_tube=(T_int-T_ext)*np.exp(g(D_1,D_2,D_3,lamb_int,lamb_iso,Debit,rho_int,Cp_int)*L)+T_ext-273.15 #température en K
#        Q=Pertes.chaleur(lamb_iso,(D_1+D_2)/2,T_int,T_ext,(D_3-(D_1+D_2))/2)
#        print(Q)
#        m=rho_int*Debit
    
    return T_sortie_tube # On garde que T_sortie_tube    