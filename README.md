# Isochrone Generator for Road Network Analysis
This repository contains an implementation of the Isochrone Generator class, which allows users to generate isochrones and shortest paths on road networks. The tool is built using NetworkX, OSMnx, Geopandas, and Dash-Leaflet for geospatial analysis and visualization.

## Features:
Road Network Loading: The class can load road network data from GraphML files or directly from OpenStreetMap using the ox.graph_from_place function.
Isochrone Generation: Given a location (latitude, longitude) and a travel time, the class generates isochrones (areas reachable within the specified travel time). It uses Alphashape for constructing concave hulls around reachable nodes within the network.
Shortest Path Calculation: The class can also compute the shortest paths from a central node to boundary nodes within the generated isochrone, using Dijkstra’s algorithm via NetworkX.

## GeoJSON Export: 
The tool supports exporting the generated road network and isochrones as GeoJSON files for easy integration with web mapping tools (such as Dash-Leaflet).
Visualization: The generated data can be visualized using Dash-Leaflet for interactive web-based mapping.
Key Methods:
## generate_isochrone(lat: float, lon: float, max_drive_time: float): 
Generates isochrone polygons based on a given center point and maximum drive time.
## generate_shortest_paths(): 
Computes the shortest paths from the center node to boundary nodes within the isochrone.
## graph_to_geojson(): 
Converts the road network graph to GeoJSON format, suitable for visualization and exporting to web mapping libraries.
## generate_city_boundary(city_name: str, filename: str): 
Generates a city boundary and saves it as a GeoJSON file (currently not implemented for direct saving).
# Libraries and Technologies:
### NetworkX: Used for graph-based network analysis.
### OSMnx: Used for loading OpenStreetMap data and working with urban road networks.
###Geopandas: For spatial data handling and conversion to GeoJSON format.
### Dash-Leaflet: For visualizing geographic data in web applications.
### Alphashape: For generating concave hulls (isochrones) around the reachable nodes.
