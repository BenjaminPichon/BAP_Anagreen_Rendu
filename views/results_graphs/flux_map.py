
import flask
from bokeh import events
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, tools, TableColumn, DataTable, PreText, CustomJS, ImageURL, \
    CDSView, GroupFilter, BoxEditTool, PointDrawTool, Label, Arrow, VeeHead
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from config import engine

class flux_map():
        
    def build_flux_map(list_lines, config, mapconfig):
        """Build and return the flux_map model, which allows to display the map of factory, the position of the fluxes, and
        the zones that are not allowed to touch when running the optimization algorithm (notouch zones)"""
        
        
        source_couples_lines=[]
        for (group_name, group_content) in list_lines.items():
        
            # preparing the ColumnDataSource for the multi_line plotting
            # Color in RGBA form (reg green blue alpha), alpha is used to manage opacity/transparency
            x_values=[]
            y_values=[]
            colors=[]
            for line in group_content:
                x_values.append([line[0]['posX'],line[1]['posX']])
                y_values.append([line[0]['posY'],line[1]['posY']])
                colors.append('#00cc0088')
            # Generating the ColumnDataSource
            source_couples_lines.append(ColumnDataSource( {
                'xs':x_values,
                'ys':y_values,
                'colors':colors,
                }, 
                name="name_couples_lines_"+group_name))
            
            
        
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
        
        flux_map = figure(plot_width=694, plot_height=438, tools=flux_map_tools, border_fill_color = "#F8F9FA", aspect_scale=1, match_aspect=True, x_range=(img_x-margin, box_w+margin), y_range=(img_y-margin - bottom_padding_for_center, img_h+margin + bottom_padding_for_center), active_scroll="wheel_zoom")

        # Build background image Bokeh's way of loading an image onto a graph is the following: you need to create a
        # source where each row contains  the information of one image : url, coordinates where to anchor the image,
        # height and width the picture should be displayed with. (coordinates are expressed in relation to the graph's
        # axes.) Then, you have to build a ImageURL object by passing the source and the names of the column containing
        # required infos. Only then you shall call the add_glyph method on the figure.
        bg_img_source = ColumnDataSource(dict(
            url=[flask.url_for('static', filename=mapconfig.path_to_map)],
            x1=[img_x],
            y1=[img_y],
            w1=[img_w],
            h1=[img_h]
        ))
        print("pathtomap", mapconfig.path_to_map)
        # x="x1", y="y1", anchor="bottom_left" means "The bottom left corner of the picture will be sticked to (x, y)"
        bg_image = ImageURL(url="url", x="x1", y="y1", h="h1", w="w1", anchor="bottom_left")
        flux_map.add_glyph(bg_img_source, bg_image)

        for val_data_source in source_couples_lines:
            flux_map.multi_line('xs','ys',source = val_data_source, line_color = 'colors', line_width=4) 
        
        
        # Add BoxEditTool
        # This is how we implement letting the user add forbidden zones (notouch zones) : We use a bokeh BoxEditTool to
        # let  the user input boxes. Bokeh automatically updates the source_notouch_zones datasource with coordinates of
        # the boxes.
        my_renderer = flux_map.rect('x', 'y', 'w', 'h', source=mapconfig.source_notouch_zones, color='color')

        # Add PointDrawTool
        # Plot fluxes
        renderer2 = flux_map.scatter(x='posX', y='posY', source=mapconfig.souce_flux,  color='color', size=15, name="scratter_dots")

        
        return flux_map   


    def build_flux_map_v2(config, mapconfig, id):
        """Build and return the flux_map model, which allows to display the map of factory, the position of the fluxes, and
        the zones that are not allowed to touch when running the optimization algorithm (notouch zones)"""
         # Load flux from DB
        groupe = {}
        query="""
            SELECT
                network.id as networkid,
                flux.id as flux_id,
                flux.name as flux_name,
                flux.media as flux_media,
                flux.fclass as flux_fclass,
                groupe,
                hotcold,
                posX, 
                posY,
                posXend, 
                posYend,
                network.ID_Exchanger_Type,
                network.Phi,
                network.h_global,
                network.S1,
                network.S2,
                network.Price
            FROM
                network
            LEFT JOIN 
                flux ON (network.flux_id = flux.id)
            WHERE
                solution_id=?"""
        result = engine.execute(query,(id))
        
        # on stock le résulat de la requête dans un dict de groupe contenant la lise des flux inclus
        for row in result:
            group_name='Groupe'+str(row['groupe'])
            if group_name not in groupe:
                groupe[group_name]=[]
            groupe[group_name].append({
                "flux_id": row['flux_id'],
                "flux_name": row['flux_name'],
                "flux_media": row['flux_media'],
                "flux_fclass": row['flux_fclass'],
                "posX": row['posX'],
                "posY": row['posY'],
                "posXend": row['posXend'],
                "posYend": row['posYend'],
                "hotcold": row['hotcold'],
                "ID_Exchanger_Type": row['ID_Exchanger_Type'],
                "Phi": row['Phi'],
                "h_global": row['h_global'],
                "S1": row['S1'],
                "S2": row['S2'],
                "Price": row['Price']
                })
                
        # on liste les groupes
        list_groups=[]
        for (key, val) in groupe.items():
            list_groups.append(key)

        # on regarde pour chaque groue le nombre de "lignes" à tracer entre les hot et cold
        list_lines={}
        distance_all_lines={}
        exchangers_names={}
        linear_meters=0
        for (group_name, group_content) in groupe.items():
            queryExch = "SELECT Name FROM exchanger_type WHERE ID_Exchanger_Type =" + str(group_content[0]['ID_Exchanger_Type']) #add exchanger data
            resultExch = engine.execute(queryExch)
            for rowExch in resultExch:
                exchangers_names[group_name]=rowExch["Name"]
            list_hot=[]
            list_cold=[]
            # on stocke d'abord la liste des hot et cold
            for ele in group_content:
                if ele['hotcold']=='hot':
                    list_hot.append(ele)
                else:
                    list_cold.append(ele)
            # on génère les lignes à tracer
            outlist=[]
            for ele in list_hot:
                for ele2 in list_cold:
                    outlist.append([ele, ele2])
            list_lines[group_name]=outlist
            
            # calcul des lines avec un autre algorith
            (list_lines[group_name], distance_all_lines[group_name]) = algocalc(list_hot, list_cold, outlist)
            linear_meters = linear_meters + distance_all_lines[group_name]
        
        source_couples_lines=[]
        for (group_name, group_content) in list_lines.items():
        
            # preparing the ColumnDataSource for the multi_line plotting
            # Color in RGBA form (reg green blue alpha), alpha is used to manage opacity/transparency
            x_values=[]
            y_values=[]
            colors=[]
            for line in group_content:
                x_values.append([line[0]['posX'],line[1]['posX']])
                y_values.append([line[0]['posY'],line[1]['posY']])
                colors.append('#00cc0088')
            # Generating the ColumnDataSource
            source_couples_lines.append(ColumnDataSource( {
                'xs':x_values,
                'ys':y_values,
                'colors':colors,
                }, 
                name="name_couples_lines_"+group_name))
            
            
        
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
        
        flux_map = figure(plot_width=694, plot_height=438, tools=flux_map_tools, border_fill_color = "#F8F9FA", aspect_scale=1, match_aspect=True, x_range=(img_x-margin, box_w+margin), y_range=(img_y-margin - bottom_padding_for_center, img_h+margin + bottom_padding_for_center), active_scroll="wheel_zoom")

        # Build background image Bokeh's way of loading an image onto a graph is the following: you need to create a
        # source where each row contains  the information of one image : url, coordinates where to anchor the image,
        # height and width the picture should be displayed with. (coordinates are expressed in relation to the graph's
        # axes.) Then, you have to build a ImageURL object by passing the source and the names of the column containing
        # required infos. Only then you shall call the add_glyph method on the figure.
        bg_img_source = ColumnDataSource(dict(
            url=[flask.url_for('static', filename=mapconfig.path_to_map)],
            x1=[img_x],
            y1=[img_y],
            w1=[img_w],
            h1=[img_h]
        ))
        print("pathtomap", mapconfig.path_to_map)
        # x="x1", y="y1", anchor="bottom_left" means "The bottom left corner of the picture will be sticked to (x, y)"
        bg_image = ImageURL(url="url", x="x1", y="y1", h="h1", w="w1", anchor="bottom_left")
        flux_map.add_glyph(bg_img_source, bg_image)

        for val_data_source in source_couples_lines:
            flux_map.multi_line('xs','ys',source = val_data_source, line_color = 'colors', line_width=4) 
        
        
        # Add BoxEditTool
        # This is how we implement letting the user add forbidden zones (notouch zones) : We use a bokeh BoxEditTool to
        # let  the user input boxes. Bokeh automatically updates the source_notouch_zones datasource with coordinates of
        # the boxes.
        my_renderer = flux_map.rect('x', 'y', 'w', 'h', source=mapconfig.source_notouch_zones, color='color')

        # Add PointDrawTool
        # Plot fluxes
        renderer2 = flux_map.scatter(x='posX', y='posY', source=mapconfig.souce_flux,  color='color', size=15, name="scratter_dots")

        
        return flux_map