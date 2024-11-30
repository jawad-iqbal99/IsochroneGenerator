# IsochroneGenerator

`IsochroneGenerator` is a Python class that generates isochrones (areas reachable within a certain time limit) based on road network data from OpenStreetMap. It uses various Python libraries like `osmnx`, `networkx`, `shapely`, and `geopandas` to generate and export isochrones.

## Installation

First, clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/IsochroneGenerator.git
cd IsochroneGenerator

##Example Usage:
#1. Using an Existing Graph File:
python
Copy code
generator = IsochroneGenerator(graph_path="path_to_existing_graph.graphml")
isochrone = generator.generate_isochrone(lat, lon, max_drive_time=20, use_alphashape=False)
generator.save_isochrone_to_geojson(lat, lon, max_drive_time=20, filename="my_isochrone.geojson")

#2. Fetching the Graph Based on Place Name:
python
Copy code
generator = IsochroneGenerator(place_name="Swindon, UK", network_type='drive')
isochrone = generator.generate_isochrone(lat, lon, max_drive_time=20, use_alphashape=True)
generator.save_isochrone_to_geojson(lat, lon, max_drive_time=20, filename="swindon_drive_isochrone.geojson)
