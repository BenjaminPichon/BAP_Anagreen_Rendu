"""This module contains the view for the index page"""
import os
import config
import json
import importlib
import numpy as np
import flask
#from flask import session
from flask import Flask, session
import time
import datetime

from bokeh import events
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, tools, TableColumn, DataTable, PreText, CustomJS, ImageURL, \
	CDSView, GroupFilter, BoxEditTool, PointDrawTool
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from flask import Blueprint
from sqlalchemy import create_engine
from shutil import copyfile
from config import engine
from werkzeug.utils import secure_filename

id_study_case = 0
case = config.CaseConfig() #Create a new study case object 

setup_bp = Blueprint('setup_page', __name__)
  

# Route for handling the index page (Flux setup)
@setup_bp.route("/")
@setup_bp.route("/setup.html")

def setup_page():
	if 'idsc' in flask.request.args:
		id_study_case=flask.request.args["idsc"]
	else:
		if session.get('gl_id_study_case', None) != None:
			id_study_case=session.get('gl_id_study_case', None)
	if int(id_study_case) > 0 : #if we selected a study case in index
		case.setValues(int(id_study_case)) # set the study case value in fonction of the ID
		if case.path_to_map == "":

			html_upload = """<h1 style="text-align: center;">Importer le plan de masse</h1> 
				<div id="dropfile">
					<div id="drop_info">
						<i class="fas fa-file-import"></i>
						<text>Glissez le plan ici</text>
					</div>
					<text>Ou</text>
					<div id="select_info">
						<input id="file_picker" type="file" name="file" accept="image/*">
						<label for="file_picker" class="btn">
							<i class="fas fa-upload"></i>
							<text>Sélectionner un fichier</text>
						</label>
					</div>	
				</div>
				"""
					
			html = flask.render_template(
			'setup.html',
			resources=INLINE.render(),
			page_id=1,
			case_informations = case,
			div_flux_map=html_upload,
			)
			return encode_utf8(html)
		else:
			# Build bokeh models

			#De ce que j'ai compris, cette action sert à réinitialiser la variable data_flux
			#Si on ne le fait pas, la liste de flux ne fonctionne plus correctement.
			#Un gros travail d'optimisation et de réorganisation du code est de rigueur
			#case.data_flux = {
			#	"id": [],
			#	"name": [],
			#	"hotcold": [],
			#	"color": [],
			#	"media": [],
			#	"posX": [],
			#	"posY": [],
			#	"posXend": [],
            #	"posYend":[],
			#	"fclass": [],
			#	"active": [],
			#	"ID_Study_Case":[]
			#}
			print ("ID STUDY CASE HERE :"+str(id_study_case))
			case.select_flux(int(id_study_case)) #filling bokeh columndatasource 
			case.select_notouch_zones(int(id_study_case))

			flux_start = case.generate_ColumnDataSource_flux("start")
			flux_end = case.generate_ColumnDataSource_flux("end")
			flux_map = build_flux_map(id_study_case, flux_start, flux_end)

			# Setup callbacks when detecting change (flux/zones creation/modification)
			#if type(case.souce_flux) != type(None): #if souce_flux has been initialized with bokeh object
				#print ("case.souce_flux est initialisé")
				#case.souce_flux.js_on_change('data', save_flux_info_js_fn())

			if type(case.source_notouch_zones) != type(None): #if source_notouch_zones has been initialized with bokeh object
				case.source_notouch_zones.js_on_change('data', save_notouch_zones_js_fn())

			if type(flux_start) != type(None):
				print ("case.get_data_source_flux_start est initialisé")
				flux_start.js_on_change('data', save_flux_start_info_js_fn(flux_start))

			if type(flux_end) != type(None):
				print ("case.get_data_source_flux_end est initialisé")
				flux_end.js_on_change('data', save_flux_end_info_js_fn(flux_end))

			
			
			# Get JS and HTML code
			script, divs = components({"flux_map": flux_map})
			json_data = json.dumps({"data_flux": case.data_flux,
			"data_notouch_zones": case.data_notouch_zones,
			})

			# Render template
			html = flask.render_template(
			'setup.html',
			resources=INLINE.render(),
			page_id=1,
			config=config,
			script=script,
			json_data=json_data,
			div_flux_map=divs["flux_map"],
			case_informations = case,
			)
			return encode_utf8(html)

	else: #if user arrived to setup page without selecting a study case
		html = flask.render_template(
		'setup.html',
		resources=INLINE.render(),
		page_id=1,
		case_informations = case,
		div_flux_map="No study case was selected ! \n Please go to step 0 and do so !" ,
		)
		return encode_utf8(html)

@setup_bp.route("/upload", methods=["POST"])
def upload():
	root_path = config.APP_ROOT
	target = os.path.join(root_path, 'static/')

	if not os.path.isdir(target):
		os.mkdir(target)

	file = flask.request.files["file2upload"]
	print (file)
	filename = secure_filename(file.filename)
	print (filename)
	destination = "/".join([target, filename])
	file.save(destination)

	query = "UPDATE study_case SET Path_to_plan = '"+str(filename)+"' WHERE ID_Study_Case = "+str(case.case_id)
	engine.execute(query)

	print ("salut")
	return "ok"

# Manage ajax requests
@setup_bp.route("/ajax_setup", methods=['GET', 'POST'])
def ajax():
	if flask.request.args['action'] == "get_flux_details":
		id = json.loads(flask.request.args["id"])
			   
		query="""SELECT raw_TS.id, tempIn, tempout, Cp, flow, timestamp
		FROM raw_TS
		LEFT JOIN time ON (raw_TS.time_id=time.id)
		WHERE flux_id=?"""
		result = engine.execute(query,(id))
		data=[]
		for row in result:
			rowtmp={}
			for (key, val) in row.items():
			
				if key=='timestamp':
					# https://docs.python.org/2/library/time.html#time.strftime
					rowtmp[key]=time.strftime("%Y/%m/%d_%H:%M:%S", time.localtime(int(val)))
				else:
					rowtmp[key]=val
			data.append(rowtmp)
		
		return json.dumps(data)
			
	
	if flask.request.args['action'] == "update_zones":
		data = json.loads(flask.request.form["data"])
		   
		# set minimum width/height for zones
		for i in range(0, len(data["color"])):
			if data["w"][i] < config.MIN_ZONE_SIZE_W:
				data["w"][i] =  config.MIN_ZONE_SIZE_W
			if data["h"][i] < config.MIN_ZONE_SIZE_H:
				data["h"][i] =  config.MIN_ZONE_SIZE_H
			
		# UPDATE table (the fast and dirty way with a truncate/insert
		# no need for now to use complex insert/update/delete like for flux
		# Color in RGBA form (reg green blue alpha), alpha is used to manage opacity/transparency
		engine.execute("DELETE FROM notouch_zone")
		engine.execute("VACUUM")
		engine.execute("DELETE FROM sqlite_sequence WHERE name='notouch_zone'")
		
		for i in range(0, len(data["color"])):
			to_add = (
				data["name"][i],
				data["color"][i],
				data["x"][i],
				data["y"][i],
				data["w"][i],
				data["h"][i],
				session['gl_id_study_case'],
			)
			engine.execute("INSERT INTO notouch_zone (name , color, x, y, w, h, ID_Study_Case) VALUES(?, ?, ?, ?, ?, ?, ?)", to_add)
		#importlib.reload(config)
		return "OK"

	if flask.request.args['action'] == "update_flux":
		
		# page_flux = flux get from the page that needs to be updated
		page_flux = json.loads(flask.request.form["data"])
		#print(page_flux)
		
		# db_flux = list of flux from DB (that needs to be compared against page_flux 
		query="SELECT id, name , hotcold, color,  media, posX, posY, posXend, posYend, fclass, active FROM flux WHERE ID_Study_Case ="+str(case.case_id)
		result = engine.execute(query)
		db_flux =  {
			"id":       [],
			"name":     [],
			"hotcold":  [],
			"color":    [],
			"media":    [],
			"posX":     [],
			"posY":     [],
			"posXend": 	[],
			"posYend": 	[],
			"fclass":     [],
			"active":     [],
			"check_present":[]
		}
		for row in result:
			for (key, val) in row.items():
				db_flux[key].append(val)
			db_flux["check_present"].append( 0 )
		result.close()
		print ("---PRINT 1---")
		# FOR ECH FLUX from page, we compare against what's in DB to know if we need insert/updte/delete
		for index, row in enumerate(page_flux["name"]):
			result = config.get_index_by_id(page_flux["id"][index], db_flux)
			
			# INSERT in DB record of new flux
			if result == -1:
				print ("---PRINT INSERT--- :"+str(page_flux["id"]))
				# print("MUST INSERT " + page_flux["name"][index] )
				to_add = (
					page_flux["name"][index],
					page_flux["hotcold"][index],
					page_flux["color"][index],
					page_flux["media"][index],
					page_flux["fclass"][index],
					page_flux["active"][index],
					page_flux["posX"][index],
					page_flux["posY"][index],
					page_flux["posXend"][index],
					page_flux["posYend"][index],
					session['gl_id_study_case'],
				)
				print ("to add ICI :"+str(page_flux["posX"][index]))
				engine.execute("INSERT INTO flux (name , hotcold, color,  media, fclass, active, posX, posY, posXend, posYend, ID_Study_Case) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", to_add)
				
			else:
				# UPDATE in DB records of flux where page_flux change
				print ("---PRINT 3---")
				print ("COMPARAISON ICI : "+str(page_flux["posXend"][index])+" - "+str(db_flux["posXend"][result]))
				db_flux["check_present"][result]=1
				if (page_flux["name"][index] != db_flux["name"][result] or
					page_flux["hotcold"][index] != db_flux["hotcold"][result] or
					page_flux["color"][index] != db_flux["color"][result] or
					page_flux["media"][index] != db_flux["media"][result] or
					page_flux["fclass"][index] != db_flux["fclass"][result] or
					page_flux["active"][index] != db_flux["active"][result] or
					page_flux["posX"][index] != db_flux["posX"][result] or
					page_flux["posY"][index] != db_flux["posY"][result]or
					page_flux["posXend"][index] != db_flux["posXend"][result] or
					page_flux["posYend"][index] != db_flux["posYend"][result]):
					# print("MUST UPDATE " + page_flux["name"][index] )
					to_update = (
						page_flux["name"][index],
						page_flux["hotcold"][index],
						page_flux["color"][index],
						page_flux["media"][index],
						page_flux["fclass"][index],
						page_flux["active"][index],
						page_flux["posX"][index],
						page_flux["posY"][index],
						page_flux["posXend"][index],
						page_flux["posYend"][index],
						page_flux["id"][index],
					)
					engine.execute("UPDATE flux SET name=?, hotcold=?, color=?, media=?, fclass=?, active=?, posX=?, posY=?, posXend=?, posYend=? WHERE id=?", to_update)

						
		# DELETE in DB records of flux that were removed (that have a check_present equal to 0)  
		for index, row in enumerate(db_flux["name"]):
			if db_flux["check_present"][index]==0:
				# print("MUST DELETE " + db_flux["name"][index] )
				to_delete = (db_flux["id"][index])
				engine.execute("DELETE FROM flux  WHERE id=?", to_delete)
				print ("---PRINT 4---")
		#importlib.reload(config)
		# engine.execute("UPDATE configuration SET value = 3 WHERE name = 'status' AND value=2")
		case.data_flux = {
			"id": [],
			"name": [],
			"hotcold": [],
			"color": [],
			"media": [],
			"posX": [],
			"posY": [],
			"posXend": [],
            "posYend":[],
			"fclass": [],
			"active": [],
			"ID_Study_Case":[]
		}
		case.select_flux(session['gl_id_study_case'])
		return "ok"

		
	if flask.request.args['action'] == "get_config":
		#importlib.reload(config)
		json_data = json.dumps({"data_flux": case.data_flux,
								"data_notouch_zones": case.data_notouch_zones,
		})
		return json_data
		
	if flask.request.args['action'] == "get_tempinout":
		id = flask.request.args['id']
		tempIn = []
		tempOut = []
		query="SELECT tempIn, tempOut  FROM raw_TS LEFT JOIN time ON (raw_TS.time_id=time.id) WHERE flux_id=? ORDER BY timestamp"
		result = engine.execute(query,(id))
		for row in result:
			tempIn.append(row[0])
			tempOut.append(row[0])
		json_data = json.dumps({"tempIn": tempIn,
							"tempOut": tempOut,
		})
		result.close()
		return json_data

		
	if flask.request.args['action'] == "update_fluxdata":
		id=int(flask.request.form['iddata'])
		data=str(flask.request.form['detaildata'])
		data=data.replace("\r\n","\n").replace("\r","\n").strip() # convert line endings to \n and trim added newlines
		
		# convert data to something more usable
		timestamps_list=[]
		lines=data.split("\n")
		firstline=lines.pop(0).split("\t") # get name of parameters of the list
		records=[]
		for line in lines:
			record_line={}
			cells = line.split("\t")
			i=0
			for cell in cells:
				if firstline[i]=="timestamp":
					cell=int(time.mktime(time.strptime(cell, "%Y/%m/%d_%H:%M:%S")))
					timestamps_list.append(str(cell))
				record_line[firstline[i]]=cell
				i+=1
			records.append(record_line)
		
		# insert timestamps
		timestamplist="),(".join(timestamps_list)
		timestamplist="("+timestamplist+")"
		#print(timestamplist)
		query="INSERT OR IGNORE INTO time(timestamp) VALUES {}".format(timestamplist)
		result = engine.execute(query)
		
		# get list of existing IDs
		query="SELECT id FROM raw_TS WHERE flux_id=?"
		result = engine.execute(query,(id))
		db_id_list=[]
		for row in result:
			db_id_list.append(row['id'])
		result.close()
		# get list of fields to delete
		for db_id in db_id_list:
			todelete=True
			for record in records:
				if int(record['id']) == db_id:
					todelete=False
			if todelete:
				print('TO DELETE : '+str(db_id))
				query="DELETE FROM raw_TS WHERE flux_id=? AND id=?"
				engine.execute(query,(id,db_id))
		
		# get list of new fields to add and update
		for record in records:
			if int(record['id']) == -1:
				# print('TO ADD : '+str(record))
				query="INSERT INTO raw_TS (flux_id, tempIn, tempOut, Cp, flow, time_id) SELECT ?, ?, ?, ?, ?, time.id FROM time WHERE timestamp=?"
				engine.execute(query,
				(id,
				record['tempIn'], 
				record['tempOut'], 
				record['Cp'],
				record['flow'], 
				record['timestamp']))
			else:
				# print('TO UPDATE : '+str(record))
				query="UPDATE raw_TS SET tempIn=?, tempOut=?, Cp=?, flow=?, time_id=(SELECT time.id FROM time WHERE timestamp=?) WHERE id=? AND flux_id=?"
				engine.execute(query,
				(record['tempIn'], 
				record['tempOut'], 
				record['Cp'],
				record['flow'], 
				record['timestamp'],
				record['id'],
				id))
		return "ok"
		
		
	if flask.request.args['action'] == "reset":

		copyfile("./anagreen_modele.sqlite", "./anagreen.sqlite")
		#importlib.reload(config)
		return "ok"

		
		
def build_flux_map(idStudyCase, flux_start, flux_end):
	"""Build and return the flux_map model, which allows to display the map of factory, the position of the fluxes, and
	the zones that are not allowed to touch when running the optimization algorithm (notouch zones)"""
		

	
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
	box_h=box_w-50
	bottom_padding_for_center=int( (box_h-img_h) / 2 )
	margin=3
	
	flux_map = figure(plot_width=900, plot_height=585, tools=flux_map_tools, aspect_scale=1, border_fill_color = "#F8F9FA", match_aspect=True, x_range=(img_x-margin, box_w+margin), y_range=(img_y-margin - bottom_padding_for_center, img_h+margin + bottom_padding_for_center), active_scroll="wheel_zoom")

	# Build background image Bokeh's way of loading an image onto a graph is the following: you need to create a
	# source where each row contains  the information of one image : url, coordinates where to anchor the image,
	# height and width the picture should be displayed with. (coordinates are expressed in relation to the graph's
	# axes.) Then, you have to build a ImageURL object by passing the source and the names of the column containing
	# required infos. Only then you shall call the add_glyph method on the figure.

	bg_img_source = ColumnDataSource(dict(
		url=[flask.url_for('static', filename=case.path_to_map)],
		x1=[img_x],
		y1=[img_y],
		w1=[img_w],
		h1=[img_h]
	))
	# x="x1", y="y1", anchor="bottom_left" means "The bottom left corner of the picture will be sticked to (x, y)"
	bg_image = ImageURL(url="url", x="x1", y="y1", h="h1", w="w1", anchor="bottom_left")
	flux_map.add_glyph(bg_img_source, bg_image)

	# Add BoxEditTool
	# This is how we implement letting the user add forbidden zones (notouch zones) : We use a bokeh BoxEditTool to
	# let  the user input boxes. Bokeh automatically updates the source_notouch_zones datasource with coordinates of
	# the boxes.
	my_renderer = flux_map.rect('x', 'y', 'w', 'h', source=case.source_notouch_zones, color='color')
	notouch_zones_tool = BoxEditTool(renderers=[my_renderer], empty_value='init')
	flux_map.add_tools(notouch_zones_tool)

	# Add PointDrawTool
	# Plot fluxes


	view1 = CDSView(source=flux_start, filters=[GroupFilter(column_name='active', group='yes')])
	view2 = CDSView(source=flux_end, filters=[GroupFilter(column_name='active', group='yes')])

	#print (case.souce_flux.data['x'].data_flux)
	renderer2 = flux_map.scatter(x='posX', y='posY', source=flux_start, view=view1, color='color', size=15, name="scratter_dots", marker="triangle")
	renderer3 = flux_map.scatter(x='posXend', y='posYend', source=flux_end, view=view2, color='color', size=15, name="scratter_square", marker="inverted_triangle")
	point_tool = PointDrawTool(renderers=[renderer2,renderer3], empty_value='hot') 

	flux_map.add_tools(point_tool)
	flux_map.toolbar.active_tap = point_tool


	return flux_map

	
def save_notouch_zones_js_fn():
	"""Build and return the CustomJS object containing the JS code for saving notouch zones into localStorage. """
	return CustomJS(args={"source_notouch_zones2": case.source_notouch_zones}, code="update_zones(source_notouch_zones2.data);")


def save_flux_info_js_fn():
	"""Build and return the CustomJS object containing the JS code for saving flux into localStorage. """
	return CustomJS(args={"souce_flux2": case.souce_flux}, code="update_flux(souce_flux2.data);")


def save_flux_start_info_js_fn(flux_start):
	"""Build and return the CustomJS object containing the JS code for saving flux into localStorage. """
	return CustomJS(args={"souce_flux_start": flux_start}, code="update_flux(souce_flux_start.data);")

def save_flux_end_info_js_fn(flux_end):
	"""Build and return the CustomJS object containing the JS code for saving flux into localStorage. """
	return CustomJS(args={"souce_flux_end": flux_end}, code="update_flux(souce_flux_end.data);")




 
