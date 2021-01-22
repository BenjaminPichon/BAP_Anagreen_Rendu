# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 10:36:14 2018

@author: nicolamartin
"""
 
#from bokeh.models.sources import AjaxDataSource
from bokeh.plotting import figure, ColumnDataSource
from bokeh.palettes import Spectral6
import numpy as np

import calcul as cal
     
def plot(source, xLabel='x', yLabel='y', xSourceName=['x'], ySourceName=['y'], title='Graph title', pHeight=350, lc=['blue']):

    p = figure(sizing_mode="scale_width", plot_height=pHeight, title=title, x_axis_label=xLabel, y_axis_label=yLabel)
    if len(xSourceName) == len(ySourceName) == len(lc) :
        for line in range(len(xSourceName)) :
            p.line(xSourceName[line], ySourceName[line], source=source, line_width=2, color=lc[line], legend=ySourceName[line])
        else :
           print("Problem occured")
#    df = source.to_df()
#    mean = np.mean(df.ySourceName)
#    p.line([df.x.iloc[0],df.x.iloc[-1]],[mean,mean], line_dash="dashed", line_width=2, line_color="grey")
    return p 

#def plot() :
