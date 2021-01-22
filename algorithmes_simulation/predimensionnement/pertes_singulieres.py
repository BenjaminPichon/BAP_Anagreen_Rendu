# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 15:17:16 2018

@author: sbouaraba
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 10:52:01 2018

@author: sbouaraba
"Toutes les données sont à rentrer en USI

Modified by abonicel
"""


#pertes de charges singuliére
#K: coefficient de pertes de charge
import numpy as np

# class pertes_singulieres: 
#l'angle défini la pente de l'entree par rapport à l'horizontale
def Elargissement(D_entre,D_sortie,angle=np.pi/2): #l'angle défini la pente de l'entree
    Se=np.pi*(D_entre**2.)/4.                 # pi/2 si élargissement brusque
    Ss=np.pi*(D_sortie**2.)/4.
    K=((1.-(Se/Ss))**2.)*np.sin(angle)
    return K
#l'angle défini la pente de l'entree par rapport à l'horizontale
def Retrecissement(D_entre,D_sortie,angle=np.pi/2): #l'angle défini la pente de l'entree
    Se=np.pi*(D_entre**2.)/4.                 # pi/2 si rétrecissement brusque
    Ss=np.pi*(D_sortie**2.)/4.
    c=0.59+0.41*((Se/Ss)**3)
    K=(((1./c)-1.)**2.)*np.sin(angle)
    return K

def Coude_brusque(angle=np.pi/2):#l'angle défini l'angle du coude par rapport à l'horizontale
    return np.sin(angle)**2 + 2*np.sin(angle/2)**4.

def Coude_arrondi(angle,R_cambrure,D_entree):#l'angle défini l'angle du coude par rapport à l'horizontale
    K= (angle/90)*(0.131+1.847*(D_entree/(2*R_cambrure))**(7/2))
    return K

def perte_sin_qv(genre,D,qv,rho,mu,angle):
    if genre=="Coude_brusque":
        k=np.sin(angle)**2 + 2*np.sin(angle/2)**4.
    S=np.pi*(D**2)/4.
    U=qv/S
    dP=k*0.5*rho*(U**2)
    return dP
