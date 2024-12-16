#!/usr/bin/env python
# coding: utf-8

# In[11]:


import dash
import dash_leaflet as dl
from shapely.geometry import Point, shape
from dash import html, Output, Input, dcc, State
import osmnx as ox
import time
import json
import geopandas as gpd  
from isochrone_generator import IsochroneGenerator

city_boundaries = {}
isochrone_dict = {}
city_graphs = {}

####

class DashApp:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.city_boundaries = city_boundaries
        self.isochrone_dict = isochrone_dict
        self.city_graphs = city_graphs
        self.setup_layout()
        self.register_callbacks()

    ####

    def setup_layout(self):
        self.app.layout = html.Div([
            html.Div([
                # Left side (Map)
                html.Div([
                    # Loading spinner for the map (this will show while waiting for callback)
                    dcc.Loading(
                        id="loading-isochrone", 
                        type="circle",  # You can choose from 'circle', 'dot', or 'default'
                        overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                        children=dl.Map([
                            dl.TileLayer(),
                            # GeoJSON layer for the isochrone
                            dl.GeoJSON(id='boundary_layer'),
                            dl.GeoJSON(id='isochrone_layer')
                        ], center=(52.778151, -1.840227), zoom=5, style={'height': '80vh'}, id='map')
                    )
                ], 
                style={'flex': 2, 'height': '100vh'}),  # Make this div take up the left portion of the screen

                # Right side (Form with buttons)
                html.Div([
                    html.Div([
                        dcc.Input(id='citynameid', placeholder='London, UK', type='text', value="", style={'width': '100%'})  # City name input
                    ], style={'padding': '10px 0'}),  # Spacing between rows

                    html.Div([
                        html.Button("Search", id="btn", style={'width': '100%'})  # Search button
                    ], style={'padding': '10px 0'}),  # Spacing between rows

                    html.Div([
                        html.Button("Add boundary", id="boundarybtn", style={'width': '100%'})  # Add boundary button
                    ], style={'padding': '10px 0'}),  # Spacing between rows
                    
                    html.Div([
                        html.Div(children = "Click on the Map to get Lat and Lon", id="textid", style={'width': '100%'})  # Add boundary button
                    ], style={'padding': '10px 0'}),  # Spacing between rows
                    
                    html.Div([
                        dcc.Input(id='latid', placeholder='Enter Latitude', type='number', value="", style={'width': '27%', 'marginRight': '2%'}),
                        dcc.Input(id='lonid', placeholder='Enter Longitude', type='number', value="", style={'width': '27%', 'marginRight': '2%'}),
                        dcc.Input(id='timeid', placeholder='Enter Time Limit', type='number', value="", style={'width': '30%'})
                    ], style={'padding': '10px 0', 'display': 'flex', 'flexWrap': 'wrap'}),  # Flex to make inputs in one row

                    html.Div([
                        html.Button("Add isochrone", id="isochronebtn", style={'width': '100%'})  # Add isochrone button
                    ], style={'padding': '10px 0'}),  # Spacing between rows

                ], style={'padding': '20px', 'height': '100vh', 'flex': 1})  # Set width and padding for the right panel
            ], style={'display': 'flex'}),  # Use flexbox to align left and right sections

            # ConfirmDialog to show the message
            dcc.ConfirmDialog(
                id='confirm_dialog',
                message='',
                displayed=False  
            ),
        ])

    ####

    def register_callbacks(self):
        # Callback for searching and centering the map
        @self.app.callback(
            [Output("map", "viewport"),  # Map viewport
             Output('confirm_dialog', 'displayed', allow_duplicate=True),  # Show confirm dialog
             Output('confirm_dialog', 'message', allow_duplicate=True),  # Message in confirm dialog
            ],
            Input("btn", "n_clicks"),  # Trigger on search button click
            State("citynameid", "value"),  # Get the current value of the city input
            prevent_initial_call=True
        )
        def update_map_search(n_search_clicks, city_name):
            new_center = [52.778151, -1.840227]  # Default center in case of an error or no input
            zoom = 5
            dialog_message = ""  # Default message for the dialog
            show_dialog = False  # Default value for showing the dialog (no dialog initially) 
    
            # If "Search" button is clicked, center the map on the city without adding boundaries
            if n_search_clicks:

                if city_name is None or city_name == '':
                    return dict(center=new_center, zoom=zoom, transition="flyTo"),True, 'Please enter city name'
                
                try: 
                    # If successful, get city coordinates and update the map center
                    lat, lon = self.get_city_coordinates(city_name)
                    new_center = [lat, lon]
                    zoom = 8
    
                except ValueError as e:
                    # If an error occurs, show the error message and update the map center
                    new_center = [52.778151, -1.840227]  # Default center in case of an error
                    zoom = 5
                    dialog_message = f"City not found!\nError: {e}"  # Show the error in the confirmation dialog
                    show_dialog = True  # Set the flag to display the dialog
    
            # Return the updated map center, zoom level, and dialog state/message
            return dict(center=new_center, zoom=zoom, transition="flyTo"), show_dialog, dialog_message
            
        ####

        # Callback for adding the boundary to the map
        @self.app.callback(
            [Output("boundary_layer", "children"),
             Output('confirm_dialog', 'displayed', allow_duplicate=True),
             Output('confirm_dialog', 'message', allow_duplicate=True)], 
            Input("boundarybtn", "n_clicks"),  # Trigger when "Add boundary" is clicked
            State("citynameid", "value"),  # Get the current value of the city input
            State("boundary_layer", "children"),  # Get the current children of the boundary layer
            prevent_initial_call=True
        )
        def update_map_boundary(n_boundary_clicks, city_name, existing_boundaries):
            boundary_geojson = existing_boundaries or []
            dialog_message = ''
            show_dialog = False
            # If "Add boundary" button is clicked, get the city's boundary and add it to the map
            if n_boundary_clicks:
                if city_name is None or city_name == '':
                    return None, True, 'Please enter a Valid city name'
                
                if city_name not in self.city_boundaries:
                    try:
                        # Get the boundary as a GeoDataFrame
                        gdf = ox.geocode_to_gdf(city_name)
                        geojson_data = gdf.geometry.to_json()  # GeoJSON format as string
                        geojson_dict = json.loads(geojson_data)  # Convert to dictionary
                        new_boundary_geojson = dl.GeoJSON(data=geojson_dict)  # Create a new GeoJSON layer

                        # Save the boundary in the dictionary
                        self.city_boundaries[city_name] = geojson_dict

                        # If city graph does not exist, generate it
                        if city_name not in self.city_graphs:
                            result = self.generate_graph(city_name)  # Try to generate the graph
                    except Exception as e:
                        dialog_message = f"Error: {e}"  # Show the error in the confirmation dialog
                        show_dialog = True  # Set the flag to display the dialog
                        
            if city_name in self.city_boundaries:
                boundary_geojson.append(dl.GeoJSON(data=self.city_boundaries[city_name]))
         
            return boundary_geojson, show_dialog, dialog_message
        
        ####

        # Define the callback to update the latitude and longitude when the map is clicked
        @self.app.callback(
            [Output('confirm_dialog', 'displayed', allow_duplicate=True),
             Output('confirm_dialog', 'message', allow_duplicate=True),
             Output('latid', 'value'),
             Output('lonid', 'value')],
            [State('citynameid', 'value'),  # Get the city name from the dropdown or input field
             Input('map', 'clickData')], 
            prevent_initial_call=True, # Listen for clicks on the map
        )
        def update_lat_lon(cityname, clickData):
  
            if clickData:
                # Extract the latitude and longitude from the clickData
                lat = clickData['latlng']['lat']
                lon = clickData['latlng']['lng']
                
                # Create a Point object from the latitude and longitude
                point = Point(lon, lat)

                if not cityname in self.city_boundaries:
                    return False, '', None, None
                # Get the boundary of the selected city
                cityboundary = self.city_boundaries.get(cityname)

                # Convert the GeoJSON to a Shapely Polygon
                polygon = shape(cityboundary['features'][0]['geometry'])
                    
                # Check if the point is inside the polygon
                if polygon.contains(point):
                    return False, '', lat, lon  # Don't show dialog, return lat and lon
                else:
                    return True, 'The point is outside the city boundary!', None, None, 
            
            # Return None, None if no click or city boundary is not found
            return False, '', None, None

        ####

        # Define the callback to update the map when the button is clicked
        @self.app.callback(
            [Output('isochrone_layer', 'children'),
             Output('confirm_dialog', 'displayed', allow_duplicate=True),
             Output('confirm_dialog', 'message', allow_duplicate=True)],
            State('citynameid', 'value'),
            State('latid', 'value'),
            State('lonid', 'value'),
            State('timeid', 'value'),
            Input('isochronebtn', 'n_clicks'),
            prevent_initial_call=True,
        )
        def update_isochrone(cityname, lat, lon, time, n_clicks):
            # Ensure that when the button is clicked, all fields are checked
            if n_clicks > 0:
                # If any of the fields are empty, show an error message
                if not lat or not lon or not time or not cityname:
                    return None, True, 'Null or Invalid input'
        
                # Check if the values are empty strings or None
                if lat == "" or lon == "" or time == "" or cityname == "":
                    return None, True, 'Null or Invalid input'
        
                cityboundary = self.city_boundaries.get(cityname)
                polygon = shape(cityboundary['features'][0]['geometry'])

                # Check if the point is inside the polygon
                if not polygon.contains(Point(lon, lat)):
                    return None, True, 'The point is outside the city boundary!' 
                
                # If all fields are valid, proceed with isochrone generation
                if cityname in self.city_graphs:
                    generator = self.city_graphs[cityname]
                    # Generate new isochrone
                    new_isochrone = generator.generate_isochrone(lat, lon, time, use_alphashape=True)
                    
                    # Convert the isochrone to a GeoDataFrame and then to GeoJSON
                    new_isochrone_gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[new_isochrone])
                    new_geojson_data = new_isochrone_gdf.geometry.to_json()
        
                    # Return the new GeoJSON data to the map
                    data = dl.GeoJSON(data=json.loads(new_geojson_data), style={
                        "color": "black", "weight": 2, "opacity": 1, "fillColor": "white", "fillOpacity": 0.2
                    })
                 
                    return data, False, ""  # Successfully generated isochrone
                else:
                    return None, True, 'City not found in the graph data.'
        
            # Return empty GeoJSON if the button hasn't been clicked yet
            return None, False, ""

        ####

    # Generate graph
    def generate_graph(self, city_name: str):
        if city_name not in self.city_graphs:
            try:
                # Attempt to create a graph for the city
                graph = IsochroneGenerator(place_name=city_name)
                
                # If successful, store the graph in memory for future use
                self.city_graphs[city_name] = graph
                return self.city_graphs[city_name]  # Return the graph immediately
                
            except Exception as e:
                # If an error occurs, handle it and return the error message
                error_message = f"Failed to create graph for {city_name}. Error: {str(e)}"
                return error_message  # Return the error message instead of raising an exception
                
        # If the graph already exists in the dictionary, return it directly
        return self.city_graphs.get(city_name)

    ####

    def get_city_coordinates(self, city_name):
        """Get coordinates for the city."""
        try:
            gdf = ox.geocode_to_gdf(city_name)
            lat, lon = gdf.geometry.centroid.y.values[0], gdf.geometry.centroid.x.values[0]
            return lat, lon
        
        except Exception as e:
            return f"Error: {e}"

    ####

    def get_isochrone(self, city_name, lat, lon, timelimit):
        """Generate isochrone for a given location and time limit."""
        if city_name in self.city_graphs:
            isochrone_generator = self.city_graphs[city_name]  # Fetch the pre-generated graph
            # isochrone_generator = IsochroneGenerator(city_name, graphml)  # Use pre-generated graph
            isochrone_gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[isochrone_generator])

            # Convert the GeoDataFrame to GeoJSON format (as a string)
            geojson_data = isochrone_gdf.geometry.to_json()
            
            # Parse the GeoJSON string into a dictionary
            geojson_dict = json.loads(geojson_data)
            return geojson_dict
        else:
            raise ValueError(f"No graph data available for {city_name}")
    
    ####

# Run the app
if __name__ == '__main__':
    app_instance = DashApp()
    app_instance.app.run_server(debug=True)

