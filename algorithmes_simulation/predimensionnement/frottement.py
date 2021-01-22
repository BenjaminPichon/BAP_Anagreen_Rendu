# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 10:52:01 2018

@author: sbouaraba
"Toutes les données sont à rentrer en USI
"""


#pertes de charges linéaires par unité de longueur
#Reynolds,k: rugosité, nu:viscosité cinématique
import numpy as np
import matplotlib.pyplot as plt
import math
import copy

from predimensionnement import Fonctions

class frottement:  
  
    def Ffrot(Re,k):
            if Re<2000:
            	 F=64./Re
            elif (Re>=2000 and Re<1e5 and k<=1e-5):
                 F=Fonctions.Fonctions.Blasius(Re)
            elif (Re>=2000 and Re<1e5 and k>1e-5):
                 F=Fonctions.Fonctions.Colebrook(Re,k)
            elif (Re>1e5 and k<=1e-5):
                 F=Fonctions.Fonctions.Colebrook(Re,k)
            elif (Re>1e5 and k>1e-5):
                 F=Fonctions.Fonctions.Nikuradse(k)
            return F
