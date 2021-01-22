from bokeh import events
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, tools, TableColumn, DataTable, PreText, CustomJS, ImageURL, \
    CDSView, GroupFilter, BoxEditTool, PointDrawTool, Label, Arrow, VeeHead
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
import flask

class flux_diag():

    def build_flux_diag(ssFlux, exc, util, config):
    
        # Build tuple containing all the tools to use
        flux_map_tools = (
            "pan",                # pan/drag tools
            "wheel_zoom",                       # scroll/pinch tools
            "zoom_in", "zoom_out", "reset",     # actions
        )
        
        # Build figure
        img_x = config.map_bottom_left_corner_location["x"]
        img_y = config.map_bottom_left_corner_location["y"]
        img_x2 = config.map_upper_right_corner_location["x"]
        img_y2 = config.map_upper_right_corner_location["y"]
        img_w = img_x2 - img_x
        img_h = img_y2 - img_y
        
        # scaled outer box
        box_w=img_w
        box_h=box_w-70
        bottom_padding_for_center=int( (box_h-img_h) / 2 )
        margin=3
        
        flux_diag = figure(plot_width=1200, plot_height=800, tools=flux_map_tools, border_fill_color = "#F8F9FA", aspect_scale=1, match_aspect=True, x_range=(img_x-margin, box_w+margin), y_range=(img_y-margin - bottom_padding_for_center, img_h+margin + bottom_padding_for_center), active_scroll="wheel_zoom")
        # flux_diag = figure(plot_width=694, plot_height=438, tools=flux_map_tools, border_fill_color = "#F8F9FA", aspect_scale=1, match_aspect=True, x_range=(img_x-margin, box_w+margin), y_range=(img_y-margin - bottom_padding_for_center, img_h+margin + bottom_padding_for_center), active_scroll="wheel_zoom")
        flux_diag.axis.visible = False
        flux_diag.xgrid.grid_line_color = None
        flux_diag.ygrid.grid_line_color = None


        # initialisation des tableaux de flux  
        exchangers = []
        utilities = []
        listeFlux = fd_listFlux()
        
        for i in range(len(ssFlux["numFlux"])): 
            if ssFlux["typeFlux"][i]=="f":
                sf = fd_ssFlux(True, ssFlux["numFlux"][i], ssFlux["numSsFlux"][i], 0, ssFlux["Te"][i],ssFlux["Ts"][i])
                listeFlux.setSsFlux(True, ssFlux["numFlux"][i], ssFlux["numSsFlux"][i], 0, sf, fluxName=ssFlux["name"][i])
                
            if ssFlux["typeFlux"][i]=="c":
                sf = fd_ssFlux(False, ssFlux["numFlux"][i], ssFlux["numSsFlux"][i], 0, ssFlux["Te"][i],ssFlux["Ts"][i])
                listeFlux.setSsFlux(False, ssFlux["numFlux"][i], ssFlux["numSsFlux"][i], 0, sf, fluxName=ssFlux["name"][i])
                


        for i in range(len(exc["numFluxF"])):
            sfF = listeFlux.getSsFlux(True, exc["numFluxF"][i], exc["numSsFluxF"][i], 0)
            sfC = listeFlux.getSsFlux(False, exc["numFluxC"][i], exc["numSsFluxC"][i], 0)
            e = fd_exchanger(exc["puissE"][i], sfF, sfC)
            sfF.exchanger = e
            sfC.exchanger = e
            exchangers.append(e)
        
        for i in range(len(util["numFlux"])):
            if util["type"][i] == "c":
                isCold = True
            else:
                isCold = False
            sf = listeFlux.getSsFlux(isCold, util["numFlux"][i], util["numSsFlux"][i], 0)
            u = fd_utility(util["puissE"][i], sf)
            sf.utility = u
            utilities.append(u)
    
        # RETRIER LES FLUX FROIDS

        for i in listeFlux.keysetFlux(True):
            tmp = []
            for j in listeFlux.keysetSsFluxAvParal(True, i):
                tmp.append(listeFlux.getSsFlux(True, i,j,0))
            tmp = sorted(tmp, key=fd_ssFlux.hash)
            listeFlux.removeSsFluxAvParal(True, i, j)
            for it in range(len(tmp)):
                tmp[it].numSsFlux = it
                listeFlux.setSsFlux(True, i,it,0,tmp[it])
 

        #calcul des ordonnees
        iterH  = 0 #compte le decalage vertical des sous flux
        previousParal = 0
        maxH = 0 #compte le decalage maximal pour le flux actuel
        
        soustraction = 0
        modifs = []

        # for i in hotFluxDict:
        for i in listeFlux.keysetFlux(False):
            prevTs = 9999999
            iterH = iterH - 1 - maxH
            maxH = 0
            soustraction = 0 #permet aux sous flux en parrallele de se "chevaucher", en decalant vers la gauche tous les sous flux suivants
            previousParal = 0
            for j in listeFlux.keysetSsFluxAvParal(False, i):
                
                sf = listeFlux.getSsFlux(False, i, j, 0)

                if prevTs < listeFlux.getSsFlux(False, i, j, 0).Te :
                    sf.numParal = previousParal + 1
                    soustraction += 1
                
                sf.numSsFlux -= soustraction

                if(maxH < sf.numParal):
                    maxH = sf.numParal

                sf.y = iterH - sf.numParal

                prevTs = sf.Ts
                previousParal = sf.numParal

                modifs.append((False, i,j,0, sf.numSsFlux, sf.numParal))


        for i in listeFlux.keysetFlux(True):
            prevTe = -9999999
            iterH = iterH - 1 - maxH
            maxH = 0
            soustraction = 0 #permet aux sous flux en parrallele de se "chevaucher", en decalant vers la gauche tous les sous flux suivants
            previousParal = 0
            
            for j in listeFlux.keysetSsFluxAvParal(True, i):
                
                sf = listeFlux.getSsFlux(True, i, j, 0)

                if prevTe > listeFlux.getSsFlux(True, i, j, 0).Ts + 1e-10:

                    sf.numParal = previousParal + 1
                    soustraction += 1
                
                sf.numSsFlux -= soustraction

                if(maxH < sf.numParal):
                    maxH = sf.numParal

                sf.y = iterH - sf.numParal

                prevTe = sf.Te
                previousParal = sf.numParal

                modifs.append((True, i,j,0, sf.numSsFlux, sf.numParal))


        for m in modifs:
            sf = listeFlux.getSsFlux(m[0], m[1], m[2], m[3])
            listeFlux.removeSsFlux(m[0], m[1], m[2], m[3])
            listeFlux.setSsFlux(m[0], m[1], m[4], m[5], sf)
            
        # calcul des abscisses des échangeurs

        exchangers = sorted(exchangers, key=fd_exchanger.hash)

        iterL = 1
        puissEMax = -1

        for i in range(len(exchangers)):
            exchangers[i].x = iterL - 0.5
            
            exchangers[i].ssFluxH.par.x2 = iterL
            exchangers[i].ssFluxC.par.x2 = iterL
            
            iterL += 1
            
            if exchangers[i].puissE > puissEMax :
                puissEMax = exchangers[i].puissE


        # calcul des abscisses des sous-flux

        for hc in {True, False}:
            for i in listeFlux.keysetFlux(hc):
                for j in listeFlux.keysetSsFluxAvParal(hc, i):

                    if j == 0:
                        listeFlux.getSsFluxAvParal(hc, i, j).x1 = 0
                    else:
                        listeFlux.getSsFluxAvParal(hc, i, j).x1 = listeFlux.getSsFluxAvParal(hc, i, j-1).x2
                        
                    if j+1 in listeFlux.keysetSsFluxAvParal(hc, i) and listeFlux.getSsFluxAvParal(hc, i, j).x2 == -1 and listeFlux.getSsFluxAvParal(hc, i, j+1).x1 == -1:
                        listeFlux.getSsFluxAvParal(hc, i, j).x2 = listeFlux.getSsFluxAvParal(hc, i, j).x1 + 1
                        
                        listeFlux.getSsFluxAvParal(hc, i, j+1).x1 = listeFlux.getSsFluxAvParal(hc, i, j).x1 + 1

                    if listeFlux.getSsFluxAvParal(hc, i, j).x2 == -1 or j == len(listeFlux.keysetSsFluxAvParal(hc, i)) -1:
                        listeFlux.getSsFluxAvParal(hc, i, j).x2 = 100000 
                   

        fluxUtil = {}                

        for i in utilities:
            i.y = i.ssFlux.y
            i.x = i.ssFlux.par.x2 - 0.5
            if i.ssFlux.isCold:
                if i.x not in fluxUtil:
                    fluxUtil[i.x] = []
                fluxUtil[i.x].append(-i.ssFlux.numFlux)
            else:
                if i.x not in fluxUtil:
                    fluxUtil[i.x] = []
                fluxUtil[i.x].append(i.ssFlux.numFlux)

        for i in listeFlux.keysetFlux(False):
            for j in listeFlux.keysetSsFluxAvParal(False, i):
                it = listeFlux.getSsFluxAvParal(False, i, j)
                for key in fluxUtil:
                    
                    if it.x1 > 0 and (it.x1+0.5 > key or (it.x1+0.5 == key and i not in fluxUtil[key])) :
                        it.x1 += 1

                    if it.x2 + 1 >= key:
                        it.x2 += 1
                        
                        if it.x2 < 100000 and it.x2 + 1 > iterL:
                            iterL = it.x2 + 1

                        for k in listeFlux.keysetSsFlux(False, i, j):
                            if listeFlux.getSsFlux(False, i, j, k).exchanger is not None:
                                listeFlux.getSsFlux(False, i, j, k).exchanger.x += 1          
                    
        for i in listeFlux.keysetFlux(True):
            for j in listeFlux.keysetSsFluxAvParal(True, i):
                it = listeFlux.getSsFluxAvParal(True, i, j)
                
                if it.x1 > 0 and (it.x1+0.5 > key or (it.x1+0.5 == key and i not in fluxUtil[key])) :
                    it.x1 += 1
                    
                    if it.x2 < 100000 and it.x2 + 1 > iterL:
                        iterL = it.x2 + 1
                        
                    for k in listeFlux.keysetSsFlux(True, i, j):
                        if listeFlux.getSsFlux(True, i, j, k).utility is not None:
                            listeFlux.getSsFlux(True, i, j, k).utility.x += 1
                            
                if it.x2 + 1 >= key:
                    it.x2 += 1
                
        for hc in {True, False}:
            for i in listeFlux.keysetFlux(hc):
                for j in listeFlux.keysetSsFluxAvParal(hc, i):
                    it = listeFlux.getSsFlux(hc, i, j, k)
                    if it.par.x2 >= 100000:
                        it.par.x2 = iterL
                        for k in listeFlux.keysetSsFlux(hc, i, j):
                            if listeFlux.getSsFlux(hc, i, j, k).utility is not None:
                                listeFlux.getSsFlux(hc, i, j, k).utility.x = iterL - 0.5

        # Affichage

        width = 100
        leftMargin = 25
        topMargin = 90
        FONT_SIZE = "12px"
        spacingH = 5
        spacingW = 5

        # hot fluxes

        for i in listeFlux.keysetFlux(False):
            for j in listeFlux.keysetSsFluxAvParal(False, i):
                for k in listeFlux.keysetSsFlux(False, i, j):
                    it = listeFlux.getSsFlux(False, i, j, k)
                    if k == 0:
                        flux_diag.line([leftMargin + it.par.x1*spacingW, leftMargin+it.par.x2*spacingW], [topMargin+it.y*spacingH, topMargin+it.y*spacingH], line_width=2, line_color='red')
                        if j == 0:
                            flux_diag.line([leftMargin -2, leftMargin+0.2], [topMargin+it.y*spacingH, topMargin+it.y*spacingH], line_width=2, line_color='red')
                            flux_diag.add_layout(Label(x=leftMargin-20, y=topMargin+it.y*spacingH-1.5,  text_color="red", text=listeFlux.listeFluxChaud[i].fluxName))
                    else:
                        flux_diag.line([leftMargin + it.par.x1*spacingW, leftMargin+(it.par.x2-0.1)*spacingW], [topMargin+it.y*spacingH, topMargin+it.y*spacingH], line_width=2, line_color='red')
                        flux_diag.line([leftMargin + it.par.x1*spacingW, leftMargin+it.par.x1*spacingW], [topMargin+it.y*spacingH, topMargin+(it.y + 1)*spacingH], line_width=2, line_color='red') 
                        flux_diag.line([leftMargin + (it.par.x2-0.1)*spacingW, leftMargin+(it.par.x2-0.1)*spacingW], [topMargin+it.y*spacingH, topMargin+(it.y + 1)*spacingH], line_width=2, line_color='red') 

                    flux_diag.add_layout(Label(x=leftMargin+ it.par.x1*spacingW, y=topMargin+it.y*spacingH-2, text_font_size=FONT_SIZE,  text=str(it.numSsFlux)+")"+str(round(it.Te))+"°Ce"))
                    flux_diag.add_layout(Label(x=leftMargin+ it.par.x2*spacingW, y=topMargin+it.y*spacingH-4, text_font_size=FONT_SIZE,  text=str(it.numSsFlux)+")"+str(round(it.Ts))+"°Cs"))
                    
        for i in listeFlux.keysetFlux(True):
            for j in listeFlux.keysetSsFluxAvParal(True, i):
                for k in listeFlux.keysetSsFlux(True, i, j):
                    it = listeFlux.getSsFlux(True, i, j, k)
                    
                    if k == 0:
                        flux_diag.line([leftMargin + it.par.x1*spacingW, leftMargin+it.par.x2*spacingW], [topMargin+it.y*spacingH, topMargin+it.y*spacingH], line_width=2, line_color='blue')
                        if j == 0: 
                            flux_diag.line([leftMargin -2, leftMargin+0.2], [topMargin+it.y*spacingH, topMargin+it.y*spacingH], line_width=2, line_color='blue')
                            flux_diag.add_layout(Label(x=leftMargin-20, y=topMargin+it.y*spacingH-1.5,  text_color="blue", text=listeFlux.listeFluxFroid[i].fluxName))
                    else:
                        flux_diag.line([leftMargin + it.par.x1*spacingW, leftMargin+(it.par.x2-0.1)*spacingW], [topMargin+it.y*spacingH, topMargin+it.y*spacingH], line_width=2, line_color='blue') 
                        flux_diag.line([leftMargin + it.par.x1*spacingW, leftMargin+it.par.x1*spacingW], [topMargin+it.y*spacingH, topMargin+(it.y + 1)*spacingH], line_width=2, line_color='blue') 
                        flux_diag.line([leftMargin + (it.par.x2-0.1)*spacingW, leftMargin+(it.par.x2-0.1)*spacingW], [topMargin+it.y*spacingH, topMargin+(it.y + 1)*spacingH], line_width=2, line_color='blue') 

                    flux_diag.add_layout(Label(x=leftMargin+ it.par.x1*spacingW, y=topMargin+it.y*spacingH-2, text_font_size=FONT_SIZE,  text=str(it.numSsFlux)+")"+str(round(it.Ts))+"°Cs"))
                    flux_diag.add_layout(Label(x=leftMargin+ it.par.x2*spacingW, y=topMargin+it.y*spacingH-4, text_font_size=FONT_SIZE,  text=str(it.numSsFlux)+")"+str(round(it.Te))+"°Ce"))
                    

        # exchangers
        for it in exchangers:
            excW = 10 * it.puissE / puissEMax 
            if excW < 1:
                excW = 1

            flux_diag.line([leftMargin + it.x*spacingW, leftMargin + it.x*spacingW], [topMargin+it.ssFluxH.y*spacingH, topMargin+it.ssFluxC.y*spacingH], line_width=excW, line_color='grey') 
            
            if round(it.puissE) == 0:
                flux_diag.add_layout(Label(x=leftMargin + it.x*spacingW - 2, y=topMargin+it.ssFluxH.y*spacingH , text_font_size=FONT_SIZE, text_color="black",text=str(round(it.puissE*1000))+"W"))
            else:
                flux_diag.add_layout(Label(x=leftMargin + it.x*spacingW - 2, y=topMargin+it.ssFluxH.y*spacingH , text_font_size=FONT_SIZE, text_color="black",text=str(round(it.puissE))+"kW"))
        
        #utilities
        for it in utilities:

            if it.ssFlux.isCold:
                adrs = "circled_c.png"
            else:
                adrs = "circled_r.png"


            r_img_source = ColumnDataSource(dict(
                url=[flask.url_for('static', filename=adrs)],
                x1=[leftMargin + (it.x)*spacingW-1.25],
                y1=[topMargin+it.y*spacingH-1.25],
                w1=[2.5],
                h1=[2.5]
            ))
            
            r_image = ImageURL(url="url", x="x1", y="y1", h="h1", w="w1", anchor="bottom_left")
            flux_diag.add_glyph(r_img_source, r_image)
            if round(it.puissE) == 0:
                flux_diag.add_layout(Label(x=leftMargin + it.x*spacingW - 2, y=topMargin+it.y*spacingH+1 , text_font_size=FONT_SIZE, text_color="black",text=str(it.ssFlux.numSsFlux)+") "+str(round(it.puissE*1000))+"W"))
            else:
                flux_diag.add_layout(Label(x=leftMargin + it.x*spacingW - 2, y=topMargin+it.y*spacingH+1 , text_font_size=FONT_SIZE, text_color="black",text=str(it.ssFlux.numSsFlux)+") "+str(round(it.puissE))+"kW"))
            
        

        return flux_diag




class fd_listFlux():



    def __init__(self):
        self.listeFluxChaud = {}
        self.listeFluxFroid = {}

    def keysetFlux(self, isCold):
        if isCold:
            return range(1,len(self.listeFluxFroid.keys())+1)
        else:   
            return range(1,len(self.listeFluxChaud.keys())+1)
            
    def keysetSsFluxAvParal(self, isCold, numFlux):
        if isCold:
            return range(len(self.listeFluxFroid[numFlux].listeSsFluxAvParal.keys()))
        else:   
            return range(len(self.listeFluxChaud[numFlux].listeSsFluxAvParal.keys()))
            
    def keysetSsFlux(self, isCold, numFlux, numSsFlux):
        if isCold:
            return range(len(self.listeFluxFroid[numFlux].listeSsFluxAvParal[numSsFlux].listeSsFlux.keys()))
        else:   
            return range(len(self.listeFluxChaud[numFlux].listeSsFluxAvParal[numSsFlux].listeSsFlux.keys()))

 

    def getSsFlux(self, isCold, numFlux, numSsFlux, numParal):
        if isCold:
            return self.listeFluxFroid[numFlux].listeSsFluxAvParal[numSsFlux].listeSsFlux[numParal] 
        else:   
            return self.listeFluxChaud[numFlux].listeSsFluxAvParal[numSsFlux].listeSsFlux[numParal]  

    def getSsFluxAvParal(self, isCold, numFlux, numSsFlux):
        if isCold:
            return self.listeFluxFroid[numFlux].listeSsFluxAvParal[numSsFlux]
        else:   
            return self.listeFluxChaud[numFlux].listeSsFluxAvParal[numSsFlux] 

    def setSsFlux(self, isCold, numFlux, numSsFlux, numParal, value,  fluxName="null"):
        if isCold: 
            if numFlux not in self.listeFluxFroid:
                self.listeFluxFroid[numFlux] = fd_flux(numFlux, isCold, fluxName)

            if numSsFlux not in self.listeFluxFroid[numFlux].listeSsFluxAvParal:
                self.listeFluxFroid[numFlux].listeSsFluxAvParal[numSsFlux] = fd_ssFluxAvParal(numSsFlux)
            
            self.listeFluxFroid[numFlux].listeSsFluxAvParal[numSsFlux].listeSsFlux[numParal] = value
            value.par = self.listeFluxFroid[numFlux].listeSsFluxAvParal[numSsFlux]

        else:   
            if numFlux not in self.listeFluxChaud:
                self.listeFluxChaud[numFlux] = fd_flux(numFlux, isCold, fluxName)

            if numSsFlux not in self.listeFluxChaud[numFlux].listeSsFluxAvParal:
                self.listeFluxChaud[numFlux].listeSsFluxAvParal[numSsFlux] = fd_ssFluxAvParal(numSsFlux)
            
            self.listeFluxChaud[numFlux].listeSsFluxAvParal[numSsFlux].listeSsFlux[numParal] = value
            value.par = self.listeFluxChaud[numFlux].listeSsFluxAvParal[numSsFlux]
            

    def removeSsFlux(self, isCold, numFlux, numSsFlux, numParal):
        if isCold: 
            self.listeFluxFroid[numFlux].listeSsFluxAvParal[numSsFlux].listeSsFlux.pop(numParal)
            if len(self.listeFluxFroid[numFlux].listeSsFluxAvParal[numSsFlux].listeSsFlux) == 0:
                self.listeFluxFroid[numFlux].listeSsFluxAvParal.pop(numSsFlux)
                if len(self.listeFluxFroid[numFlux].listeSsFluxAvParal) == 0:
                    self.listeFluxFroid.pop(numFlux)

        else:   
            self.listeFluxChaud[numFlux].listeSsFluxAvParal[numSsFlux].listeSsFlux.pop(numParal)
            if len(self.listeFluxChaud[numFlux].listeSsFluxAvParal[numSsFlux].listeSsFlux) == 0:
                self.listeFluxChaud[numFlux].listeSsFluxAvParal.pop(numSsFlux)
                if len(self.listeFluxChaud[numFlux].listeSsFluxAvParal) == 0:
                    self.listeFluxChaud.pop(numFlux)

    def removeSsFluxAvParal(self, isCold, numFlux, numSsFlux):
        if isCold: 
            self.listeFluxFroid[numFlux].listeSsFluxAvParal.pop(numSsFlux)
            if len(self.listeFluxFroid[numFlux].listeSsFluxAvParal) == 0:
                self.listeFluxFroid.pop(numFlux)
        else:   
            self.listeFluxChaud[numFlux].listeSsFluxAvParal.pop(numSsFlux)
            if len(self.listeFluxChaud[numFlux].listeSsFluxAvParal) == 0:
                self.listeFluxChaud.pop(numFlux)

class fd_flux():
    def __init__(self, numFlux, isCold, fluxName):
        self.numFlux = numFlux
        self.isCold = isCold
        self.fluxName = fluxName
        self.listeSsFluxAvParal = {}

class fd_ssFluxAvParal():
    def __init__(self, numSsFlux):
        self.numSsFlux = numSsFlux
        self.listeSsFlux = {}
        self.x1 = -1
        self.x2 = -1


# Class used by build_flux_diag to sort flux parts
class fd_ssFlux():
    def __init__(self, isCold, numFlux, numSsFlux, numParal, Te, Ts):
        self.isCold = isCold
        self.numFlux = numFlux
        self.numSsFlux = numSsFlux
        self.numParal = numParal
        self.Te = Te
        self.Ts = Ts
        self.y = -1
        self.exchanger = None
        self.utility = None
        self.par = None
    
    #Returns a value for sorting purposes
    def hash(a):
        if a.isCold:
            return - (a.Ts + a.Te)/2 
        else:
            return (a.Ts + a.Te)/2 
            

# Class used by build_flux_diag to sort exchangers
class fd_exchanger():
    def __init__(self, puissE, ssFluxC, ssFluxH):
        self.puissE = puissE
        self.x = -1
        self.y1 = -1
        self.y2 = -1
        self.ssFluxH = ssFluxH
        self.ssFluxC = ssFluxC

    #Returns a value for sorting purposes
    def hash(a):
        return -a.ssFluxH.Te  

# Class used by build_flux_diag to sort exchangers
class fd_utility():
    def __init__(self, puissE, ssFlux):
        self.puissE = puissE
        self.x = -1
        self.y = -1
        self.ssFlux = ssFlux