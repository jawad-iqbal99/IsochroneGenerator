# Import necessary libraries
import osmnx as ox
import networkx as nx
import geopandas as gpd
import json
from shapely.geometry import Polygon
import dash_leaflet as dl

from isochrone_generator import IsochroneGenerator

# 1. Initialize IsochroneGenerator
isochrone_gen = IsochroneGenerator()

# 2. Load the graph from OpenStreetMap (OSM)
graph = isochrone_gen._load_graph_from_place("Somerset, UK")

# 3. Generate an isochrone from a specific latitude, longitude, and max drive time (in minutes)
# For example, latitude and longitude of a point in Somerset (approximately 51.2094° N, 3.1016° W)
lat, lon = 51.2094, -3.1016  # Latitude and longitude for Somerset, UK
max_drive_time = 10  # Max drive time in minutes (e.g., generate isochrone for a 30-minute drive)

# Generate isochrone (a polygon that shows the area accessible within the max drive time)
isochrone = isochrone_gen.generate_isochrone(lat, lon, max_drive_time)

# Convert the road network (graph) to GeoJSON
# If you'd like to visualize the entire road network as GeoJSON
network_geojson = isochrone_gen.graph_to_geojson()


# Generate shortest paths from the center node to boundary nodes (optional)
# This will create paths from the center point (Somerset) to the boundary of the isochrone
geojson_paths = isochrone_gen.generate_shortest_paths()
