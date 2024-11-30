IsochroneGenerator
IsochroneGenerator is a Python class designed to generate isochrones (areas reachable within a certain time limit) based on road network data from OpenStreetMap. It leverages several Python libraries such as osmnx, networkx, shapely, geopandas, and folium to efficiently generate, visualize, and export isochrones.

Features
Isochrone Generation: Generate polygons representing areas reachable within a specified travel time from a given point.
Custom Speed: Uses road speed limits to calculate travel times (supports multiple network types).
Flexible Input: Supports both loading a pre-existing GraphML file or fetching a graph dynamically based on a place name.
Alphashape Option: Supports generating concave hulls using the Alphashape algorithm for more accurate isochrones.
GeoJSON Export: Save generated isochrones as GeoJSON files for easy integration with mapping tools.
Interactive Map: Optionally visualize the generated isochrones on an interactive Folium map.
Installation
To install IsochroneGenerator, simply clone the repository and install the necessary dependencies.

Clone the Repository
bash
Copy code
git clone https://github.com/yourusername/IsochroneGenerator.git
cd IsochroneGenerator
Install Dependencies
Create a virtual environment (optional but recommended) and install the required libraries using pip:

bash
Copy code
# Optional: Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
The requirements.txt file should include dependencies like:

Copy code
osmnx
networkx
shapely
geopandas
folium
alphashape
Example Usage
1. Using an Existing Graph File
If you already have a pre-generated road network graph in GraphML format, you can simply load the graph and generate isochrones from it.

python
Copy code
from isochrone_generator import IsochroneGenerator

# Instantiate the IsochroneGenerator with a GraphML file
generator = IsochroneGenerator(graph_path="path_to_existing_graph.graphml")

# Generate an isochrone for a specific point (latitude, longitude) with a time limit
lat, lon = 51.5074, -0.1278  # Example coordinates for London
isochrone = generator.generate_isochrone(lat, lon, max_drive_time=20, use_alphashape=False)

# Save the generated isochrone to a GeoJSON file
generator.save_isochrone_to_geojson(lat, lon, max_drive_time=20, filename="my_isochrone.geojson")
2. Fetching the Graph Based on Place Name
If you don't have a GraphML file and wish to fetch the road network dynamically based on a place name, you can do so with osmnx by providing the place name and network type.

python
Copy code
from isochrone_generator import IsochroneGenerator

# Instantiate the IsochroneGenerator by providing a place name and network type
generator = IsochroneGenerator(place_name="Swindon, UK", network_type="drive")

# Generate an isochrone with a 20-minute drive time from a given point
lat, lon = 51.5550, -1.7810  # Example coordinates for Swindon, UK
isochrone = generator.generate_isochrone(lat, lon, max_drive_time=20, use_alphashape=True)

# Save the generated isochrone to a GeoJSON file
generator.save_isochrone_to_geojson(lat, lon, max_drive_time=20, filename="swindon_drive_isochrone.geojson")
