# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 11:57:49 2018

@author: sbouaraba

Modified by abonicel
"""

# MAIN
from __future__ import division
import numpy as np
import pygame

from predimensionnement import A_algorithm
#
#def get_indexes(my_list, s):
#    start = 0
#    while True:
#        try:
#            index = my_list.index(s, start)
#            start = index+1
#            yield index
#        except ValueError:
#            break

class Chemin:
    
    def chemin(xC,yC,xF,yF,r_echelle,m,n): #r_echelle le rapport d'échelle 1 pixel=X mètre, m la hauteur du plan en pixel et n la largeur du plan en pixel
        # Hypothèse 1 carreau=1 pixel sur le plan de l'application
        # On doit alors définir un rapport d'échelle 1 pixel=X mètres
        # Hypothèse que l'échangeur se trouve à 2 mètres du flux chaud

        if xC==xF and yC==yF:
            x_ech,y_ech=xC,yC
            distanceC=distanceF=nbCoudeC=nbCoudeF=0
            return distanceC,nbCoudeC,distanceF,nbCoudeF,x_ech,y_ech
        grid = []
        for row in range(m):
        #    # Add an empty array that will hold each cell
        #    # in this row
            grid.append([])
            for column in range(n):
                grid[row].append(0)  # Append a cell
        
        # Set row 1, cell 5 to one. (Remember rows and
        # column numbers start at zero.)
        dirs = 4 # number of possible directions to move on the map
        if dirs == 4:
            dx = [1, 0, -1, 0]
            dy = [0, 1, 0, -1]
        elif dirs == 8:
            dx = [1, 1, 0, -1, -1, -1, 0, 1]
            dy = [0, 1, 1, 1, 0, -1, -1, -1]
        
        
        # fillout the map with the obstacles
#        grid[0][2] = 1
#        grid[1][2] = 1
#        grid[2][2] = 1
#        grid[3][2] = 1
#        grid[4][2] = 1
#        grid[5][2] = 1
#        grid[6][2] = 1
#        grid[7][2] = 1
        
        # Select start & finish points
        
        (xA, yA, xB, yB) =(xC,yC,xF,yF)
#        grid[yA][xA]=2
        #grid[xB][yB]=3
#        print ('Map size (X,Y): ', n, m)
#        print ('Start: ', xA, yA)
#        print ('Finish: ', xB, yB)
#        t = time.time()
        route = A_algorithm.pathFind(grid, n, m, dirs, dx, dy, xA, yA, xB, yB)
#        print ('Time to generate the route (seconds): ', time.time() - t)
#        print ('Route:')
#        print(len(route))
        if len(route) > 0:
            x = xA
            y = yA
#            grid[y][x] = 2
            ech=False #variable disant si l'échangeur est placé ou pas
            distanceF=0 # Longueur de tuyauterie pour le flux froid
            nbCoudeC=0 # Nombre de coude pour le flux chaud
            nbCoudeF=0 # Nombre de coude pour le flux froid
            ini=int(route[0])
            Done=False #paramètre disant si l'échangeur a été placé à 2 m du flux chaud
            for i in range(len(route)):
                j = int(route[i])
                x += dx[j]
                y += dy[j]
#                grid[y][x] = 4
                if ech==False: # on place l'échangeur à au moins deux mètres du flux chaud on en déduit la longueur de tuyauterie pour le flux chaud
                    if (i+1)*r_echelle>2 and i*r_echelle<=2:
                        ech=True
#                        grid[y][x] = 5
                        x_ech,y_ech=x,y
                        distanceC=max(r_echelle*i,r_echelle) # Prise en compte du cas ou l'échangeur est sur le pixel juste après le flux chaud
                        Done=True
                        if j!=ini:
                            nbCoudeC+=1
                            ini=j
                else:
                    if i!=len(route)-1:
                        distanceF+=r_echelle
                    if j!=ini:
                            nbCoudeF+=1
                            ini=j
            if Done==False:
                #on vérifie si le flux froid est a coté du flux chaud
                if ((xC+1==xF or xC-1==xF) and yC==yF) or ((yC-1==yF or yC+1==yF) and xC==xF):
                    x_ech,y_ech=xC,yC
                    distanceC,distanceF=r_echelle,r_echelle
                    nbCoudeC=nbCoudeF=0
                else:
                    for i in range(len(route)):
                        j = int(route[i])
                        x += dx[j]
                        y += dy[j]
#                        grid[y][x] = 4
                        if ech==False:
                            ech=True
                            #on place l'échangeur juste après le flux chaud (arbitraire)
                            x_ech,y_ech=x,y
                            distanceC=r_echelle # Prise en compte du cas ou l'échangeur est sur le pixel juste après le flux chaud
                            if j!=ini:
                                nbCoudeC+=1
                                ini=j
                        else:
                            if i!=len(route)-1:
                                distanceF+=r_echelle
                            if j!=ini:
                                    nbCoudeF+=1
                                    ini=j
#            grid[y][x] = 3
        
#        print('la distance du parcours du flux chaud est de : ',distanceC,'m')
#        print('la distance du parcours du flux froid est de : ',distanceF,'m')
#        print('le nombre de coude du flux chaud est de : ',nbCoudeC)
#        print('la nombre de coude du flux froid est de : ',nbCoudeF)
#        else:
        else:
            distanceC=nbCoudeC=distanceF=nbCoudeF=0
            x_ech,y_ech=xC,yC
        # Renvoie la longueur de tuyauterie du flux chaud, le nombre de coude du flux chaud, la longueur de la tuyauterie du flux froid, le nombre de coude du flux froid
        return distanceC,nbCoudeC,distanceF,nbCoudeF,x_ech,y_ech
    
    def chemin_obstacle(xC,yC,xF,yF,r_echelle,m,n,listeObstacleC,listeObstacleF): #r_echelle le rapport d'échelle 1 pixel=X mètre, m la hauteur du plan en pixel et n la largeur du plan en pixel
        # Hypothèse 1 carreau=1 pixel sur le plan de l'application
        # On doit alors définir un rapport d'échelle 1 pixel=X mètres
        # Hypothèse que l'échangeur se trouve à 2 mètres du flux chaud
        # la liste est une simple liste

        if xC==xF and yC==yF:
            x_ech,y_ech=xC,yC
            distanceC=distanceF=nbCoudeC=nbCoudeF=0
            return distanceC,nbCoudeC,distanceF,nbCoudeF,x_ech,y_ech
        grid = []
        for row in range(m):
        #    # Add an empty array that will hold each cell
        #    # in this row
            grid.append([])
            for column in range(n):
                grid[row].append(0)  # Append a cell
        
        # Set row 1, cell 5 to one. (Remember rows and
        # column numbers start at zero.)
        dirs = 4 # number of possible directions to move on the map
        if dirs == 4:
            dx = [1, 0, -1, 0]
            dy = [0, 1, 0, -1]
        elif dirs == 8:
            dx = [1, 1, 0, -1, -1, -1, 0, 1]
            dy = [0, 1, 1, 1, 0, -1, -1, -1]
        
        
        # fillout the map with the obstacles
        for pos in listeObstacleC :
            grid[pos[1]][pos[0]] = 1
            
        for pos in listeObstacleF :
            grid[pos[1]][pos[0]] = 1
        
        # Select start & finish points
        
        (xA, yA, xB, yB) =(xC,yC,xF,yF)
        grid[yA][xA]=2
        grid[xB][yB]=3
#        print ('Map size (X,Y): ', n, m)
#        print ('Start: ', xA, yA)
#        print ('Finish: ', xB, yB)
#        t = time.time()
        route = A_algorithm.pathFind(grid, n, m, dirs, dx, dy, xA, yA, xB, yB)
#        print ('Time to generate the route (seconds): ', time.time() - t)
#        print ('Route:')
#        print(len(route))
        if len(route) > 0:
            x = xA
            y = yA
#            grid[y][x] = 2
            ech=False #variable disant si l'échangeur est placé ou pas
            distanceF=0 # Longueur de tuyauterie pour le flux froid
            nbCoudeC=0 # Nombre de coude pour le flux chaud
            nbCoudeF=0 # Nombre de coude pour le flux froid
            ini=int(route[0])
            Done=False #paramètre disant si l'échangeur a été placé à 2 m du flux chaud
            for i in range(len(route)):
                j = int(route[i])
                x += dx[j]
                y += dy[j]
#                grid[y][x] = 4
                if ech==False: # on place l'échangeur à au moins deux mètres du flux chaud on en déduit la longueur de tuyauterie pour le flux chaud
                    if (i+1)*r_echelle>2 and i*r_echelle<=2:
                        ech=True
#                        grid[y][x] = 5
                        x_ech,y_ech=x,y
                        distanceC=max(r_echelle*i,r_echelle) # Prise en compte du cas ou l'échangeur est sur le pixel juste après le flux chaud
                        Done=True
                        if j!=ini:
                            nbCoudeC+=1
                            ini=j
                else:
                    if i!=len(route)-1:
                        distanceF+=r_echelle
                    if j!=ini:
                            nbCoudeF+=1
                            ini=j
            if Done==False:
                #on vérifie si le flux froid est a coté du flux chaud
                if ((xC+1==xF or xC-1==xF) and yC==yF) or ((yC-1==yF or yC+1==yF) and xC==xF):
                    x_ech,y_ech=xC,yC
                    distanceC,distanceF=r_echelle,r_echelle
                    nbCoudeC=nbCoudeF=0
                else:
                    for i in range(len(route)):
                        j = int(route[i])
                        x += dx[j]
                        y += dy[j]
#                        grid[y][x] = 4
                        if ech==False:
                            ech=True
                            #on place l'échangeur juste après le flux chaud (arbitraire)
                            x_ech,y_ech=x,y
                            distanceC=r_echelle # Prise en compte du cas ou l'échangeur est sur le pixel juste après le flux chaud
                            if j!=ini:
                                nbCoudeC+=1
                                ini=j
                        else:
                            if i!=len(route)-1:
                                distanceF+=r_echelle
                            if j!=ini:
                                    nbCoudeF+=1
                                    ini=j
#            grid[y][x] = 3
        
#        print('la distance du parcours du flux chaud est de : ',distanceC,'m')
#        print('la distance du parcours du flux froid est de : ',distanceF,'m')
#        print('le nombre de coude du flux chaud est de : ',nbCoudeC)
#        print('la nombre de coude du flux froid est de : ',nbCoudeF)
#        else:
        else:
            distanceC=nbCoudeC=distanceF=nbCoudeF=0
            x_ech,y_ech=xC,yC
        # Renvoie la longueur de tuyauterie du flux chaud, le nombre de coude du flux chaud, la longueur de la tuyauterie du flux froid, le nombre de coude du flux froid
        return distanceC,nbCoudeC,distanceF,nbCoudeF,x_ech,y_ech
    
    def chemin_ssflux(xC,yC,xF,yF,r_echelle,m,n): #r_echelle le rapport d'échelle 1 pixel=X mètre, m la hauteur du plan en pixel et n la largeur du plan en pixel
        # Hypothèse 1 carreau=1 pixel sur le plan de l'application
        # On doit alors définir un rapport d'échelle 1 pixel=X mètres
        # Hypothèse que l'échangeur se trouve à 2 mètres du flux chaud

        grid = []
        for row in range(m):
        #    # Add an empty array that will hold each cell
        #    # in this row
            grid.append([])
            for column in range(n):
                grid[row].append(0)  # Append a cell
        
        # Set row 1, cell 5 to one. (Remember rows and
        # column numbers start at zero.)
        dirs = 4 # number of possible directions to move on the map
        if dirs == 4:
            dx = [1, 0, -1, 0]
            dy = [0, 1, 0, -1]
        elif dirs == 8:
            dx = [1, 1, 0, -1, -1, -1, 0, 1]
            dy = [0, 1, 1, 1, 0, -1, -1, -1]
        
        
        # fillout the map with the obstacles
#        grid[0][2] = 1
#        grid[1][2] = 1
#        grid[2][2] = 1
#        grid[3][2] = 1
#        grid[4][2] = 1
#        grid[5][2] = 1
#        grid[6][2] = 1
#        grid[7][2] = 1
        
        # Select start & finish points
        
        (xA, yA, xB, yB) =(xC,yC,xF,yF)
#        grid[yA][xA]=2
        #grid[xB][yB]=3
#        print ('Map size (X,Y): ', n, m)
#        print ('Start: ', xA, yA)
#        print ('Finish: ', xB, yB)
#        t = time.time()
        route = A_algorithm.pathFind(grid, n, m, dirs, dx, dy, xA, yA, xB, yB)
#        print ('Time to generate the route (seconds): ', time.time() - t)
#        print ('Route:')
#        print (route)
        
        if len(route) > 0:
            x = xA
            y = yA
#            grid[y][x] = 2
            distanceC=0
            nbCoudeC=0 # Nombre de coude pour le flux chaud
            ini=int(route[0])
            for i in range(len(route)):
                j = int(route[i])
                x += dx[j]
                y += dy[j]
#                grid[y][x] = 4
                if i!=len(route)-1:
                    distanceC+=r_echelle
                if j!=ini:
                        nbCoudeC+=1
                        ini=j
                        
#            grid[y][x] = 3
        
#        print('la distance du parcours du flux chaud est de : ',distanceC,'m')
#        print('la distance du parcours du flux froid est de : ',distanceF,'m')
#        print('le nombre de coude du flux chaud est de : ',nbCoudeC)
#        print('la nombre de coude du flux froid est de : ',nbCoudeF)
        
        else:
            distanceC,nbCoudeC=0,0
        
        # Renvoie la longueur de tuyauterie du flux chaud, le nombre de coude du flux chaud, la longueur de la tuyauterie du flux froid, le nombre de coude du flux froid
        return distanceC,nbCoudeC
    
    def chemin_estdivise(xC,yC,xF,yF,r_echelle,m,n): #r_echelle le rapport d'échelle 1 pixel=X mètre, m la hauteur du plan en pixel et n la largeur du plan en pixel
        # Hypothèse 1 carreau=1 pixel sur le plan de l'application
        # On doit alors définir un rapport d'échelle 1 pixel=X mètres
        # Hypothèse que l'échangeur se trouve à 2 mètres du flux chaud

        grid = []
        for row in range(m):
        #    # Add an empty array that will hold each cell
        #    # in this row
            grid.append([])
            for column in range(n):
                grid[row].append(0)  # Append a cell
        
        # Set row 1, cell 5 to one. (Remember rows and
        # column numbers start at zero.)
        dirs = 4 # number of possible directions to move on the map
        if dirs == 4:
            dx = [1, 0, -1, 0]
            dy = [0, 1, 0, -1]
        elif dirs == 8:
            dx = [1, 1, 0, -1, -1, -1, 0, 1]
            dy = [0, 1, 1, 1, 0, -1, -1, -1]
        
        
        # fillout the map with the obstacles
#        grid[0][2] = 1
#        grid[1][2] = 1
#        grid[2][2] = 1
#        grid[3][2] = 1
#        grid[4][2] = 1
#        grid[5][2] = 1
#        grid[6][2] = 1
#        grid[7][2] = 1
        
        # Select start & finish points
        
        (xA, yA, xB, yB) =(xC,yC,xF,yF)
#        grid[yA][xA]=2
        #grid[xB][yB]=3
#        print ('Map size (X,Y): ', n, m)
#        print ('Start: ', xA, yA)
#        print ('Finish: ', xB, yB)
#        t = time.time()
        route = A_algorithm.pathFind(grid, n, m, dirs, dx, dy, xA, yA, xB, yB)
#        print ('Time to generate the route (seconds): ', time.time() - t)
#        print ('Route:')
#        print (route)
        
        if len(route) > 0:
            x = xA
            y = yA
            grid[y][x] = 2
            distanceC=0
            nbCoudeC=0 # Nombre de coude pour le flux chaud
            ini=int(route[0])
            for i in range(len(route)):
                j = int(route[i])
                x += dx[j]
                y += dy[j]
                grid[y][x] = 4
                if i!=len(route)-1:
                    distanceC+=r_echelle
                if j!=ini:
                        nbCoudeC+=1
                        ini=j
                        
#            grid[y][x] = 3
        
#        print('la distance du parcours du flux chaud est de : ',distanceC,'m')
#        print('la distance du parcours du flux froid est de : ',distanceF,'m')
#        print('le nombre de coude du flux chaud est de : ',nbCoudeC)
#        print('la nombre de coude du flux froid est de : ',nbCoudeF)
        else:
            distanceC,nbCoudeC=0,0
        # Renvoie la longueur de tuyauterie du flux chaud, le nombre de coude du flux chaud, la longueur de la tuyauterie du flux froid, le nombre de coude du flux froid
        return distanceC,nbCoudeC
    
    def affichage_chemin(xC,yC,xF,yF,r_echelle,m,n): #r_echelle le rapport d'échelle 1 pixel=X mètre, m la hauteur du plan en pixel et n la largeur du plan en pixel
        # Hypothèse 1 carreau=1 pixel sur le plan de l'application
        # On doit alors définir un rapport d'échelle 1 pixel=X mètres
        # Hypothèse que l'échangeur se trouve à 2 mètres du flux chaud
        
        # Define some colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GREEN = (0, 255, 0)
        RED = (255, 0, 0)
        BLUE=(0,0,255)
        VIOLET=(186,85,211)
        YELLOW=(255,255,0)

        # This sets the WIDTH and HEIGHT of each grid location
        WIDTH = 20 # vertical size of each cell on the map
        HEIGHT = 20 # horizontal size of each cell on the map
#        m=9 # nombre de ligne (=pixel) (hauteur du plan)
#        n=5 # nombre de colonne (=pixel) (largeur du plan)
        # This sets the margin between each cell
        MARGIN = 2
         
        # Create a 2 dimensional array. A two dimensional
        # array is simply a list of lists.
        pygame.display.set_caption(" ")
        grid = []
        for row in range(m):
        #    # Add an empty array that will hold each cell
        #    # in this row
            grid.append([])
            for column in range(n):
                grid[row].append(0)  # Append a cell
        
        # Set row 1, cell 5 to one. (Remember rows and
        # column numbers start at zero.)
        dirs = 4 # number of possible directions to move on the map
        if dirs == 4:
            dx = [1, 0, -1, 0]
            dy = [0, 1, 0, -1]
        elif dirs == 8:
            dx = [1, 1, 0, -1, -1, -1, 0, 1]
            dy = [0, 1, 1, 1, 0, -1, -1, -1]
        
        
        # fillout the map with the obstacles
#        grid[0][2] = 1
#        grid[1][2] = 1
#        grid[2][2] = 1
#        grid[3][2] = 1
#        grid[4][2] = 1
#        grid[5][2] = 1
#        grid[6][2] = 1
#        grid[7][2] = 1
        
        # Select start & finish points
        
        (xA, yA, xB, yB) =(xC,yC,xF,yF)
        grid[yA][xA]=2
        #grid[xB][yB]=3
#        print ('Map size (X,Y): ', n, m)
#        print ('Start: ', xA, yA)
#        print ('Finish: ', xB, yB)
#        t = time.time()
        route = A_algorithm.pathFind(grid, n, m, dirs, dx, dy, xA, yA, xB, yB)
#        print ('Time to generate the route (seconds): ', time.time() - t)
#        print ('Route:')
#        print (route)
        
        if len(route) > 0:
            x = xA
            y = yA
            grid[y][x] = 2
            ech=False #variable disant si l'échangeur est placé ou pas
            distanceF=0 # Longueur de tuyauterie pour le flux froid
            nbCoudeC=0 # Nombre de coude pour le flux chaud
            nbCoudeF=0 # Nombre de coude pour le flux froid
            ini=int(route[0])
            for i in range(len(route)):
                j = int(route[i])
                x += dx[j]
                y += dy[j]
                grid[y][x] = 4
                if ech==False: # on place l'échangeur à au moins deux mètres du flux chaud on en déduit la longueur de tuyauterie pour le flux chaud
                    if (i+1)*r_echelle>2 and i*r_echelle<=2:
                        ech=True
                        grid[y][x] = 5
                        x_ech,y_ech=x,y
                        distanceC=max(r_echelle*i,r_echelle) # Prise en compte du cas ou l'échangeur est sur le pixel juste après le flux chaud
                        if j!=ini:
                            nbCoudeC+=1
                            ini=j
                else:
                    if i!=len(route)-1:
                        distanceF+=r_echelle
                    if j!=ini:
                            nbCoudeF+=1
                            ini=j
                        
            grid[y][x] = 3
        
#        print('la distance du parcours du flux chaud est de : ',distanceC,'m')
#        print('la distance du parcours du flux froid est de : ',distanceF,'m')
#        print('le nombre de coude du flux chaud est de : ',nbCoudeC)
#        print('la nombre de coude du flux froid est de : ',nbCoudeF)
        
        # Initialize pygame
        pygame.init()
         	
        # Set the HEIGHT and WIDTH of the screen
        WINDOW_SIZE = [WIDTH*n+(n+1)*MARGIN,HEIGHT*m+(m+1)*MARGIN ] #nombre de pixel du plan (largeur x hauteur)
        screen = pygame.display.set_mode(WINDOW_SIZE)

        # Set title of screen
        pygame.display.set_caption("Array Backed Grid")
         
        # Loop until the user clicks the close button.
        done = False
         
        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()
       
        # -------- Main Program Loop -----------
        while not done:
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True  # Flag that we are done so we exit this loop
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # User clicks the mouse. Get the position
                    pos = pygame.mouse.get_pos()
                    # Change the x/y screen coordinates to grid coordinates
                    column = pos[0] // (WIDTH + MARGIN)
                    row = pos[1] // (HEIGHT + MARGIN)
                    # Set that location to one
                    grid[row][column] = 1
                    print("Click ", pos, "Grid coordinates: ", row, column)
         
            # Set the screen background
            screen.fill(BLACK)
         
            # Draw the grid
            for row in range(m):
                for column in range(n):
                    color = WHITE
                    if grid[row][column] == 1:
                        color = GREEN
                    pygame.draw.rect(screen,
                                     color,
                                     [(MARGIN + WIDTH) * column + MARGIN,
                                      (MARGIN + HEIGHT) * row + MARGIN,
                                      WIDTH,
                                      HEIGHT])
        ##Flux chaud           
                    if grid[row][column] == 2:
                        color = RED
                    
                    pygame.draw.rect(screen,
                                     color,
                                     [(MARGIN + WIDTH) * column + MARGIN,
                                      (MARGIN + HEIGHT) * row + MARGIN,
                                      WIDTH,
                                      HEIGHT])
                    
                
        ##Tuyauterie           
                    if grid[row][column] == 4:
                        color = VIOLET
                    pygame.draw.rect(screen,
                                     color,
                                     [(MARGIN + WIDTH) * column + MARGIN,
                                      (MARGIN + HEIGHT) * row + MARGIN,
                                      WIDTH,
                                      HEIGHT])
        ##Flux froid                
                    if grid[row][column] == 3:
                        color = BLUE
                    
                    pygame.draw.rect(screen,
                                     color,
                                     [(MARGIN + WIDTH) * column + MARGIN,
                                      (MARGIN + HEIGHT) * row + MARGIN,
                                      WIDTH,
                                      HEIGHT])
        ##Obstacles
                    if grid[row][column] == 5:                    
                        color = YELLOW
                    pygame.draw.rect(screen,
                    color,
                    [(MARGIN + WIDTH) * column + MARGIN,
                    (MARGIN + HEIGHT) * row + MARGIN,
                    WIDTH,
                    HEIGHT])
            
            nmap=grid
        #    nmap[S_c[0]][S_c[1]]=0
        #    nmap[S_f[0]][S_f[1]]=0
            nmap=np.asarray(nmap)
            # Limit to 60 frames per second
            clock.tick(60)
        
            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()
#            pause.milliseconds(5000)
#            pygame.quit()
        
            
        
        
        # Be IDLE friendly. If you forget this line, the program will 'hang'
        # on exit.
       
        # Renvoie la longueur de tuyauterie du flux chaud, le nombre de coude du flux chaud, la longueur de la tuyauterie du flux froid, le nombre de coude du flux froid
        return distanceC,nbCoudeC,distanceF,nbCoudeF,x_ech,y_ech
