# IsochroneGenerator

`IsochroneGenerator` is a Python class designed to generate isochrones (areas reachable within a certain time limit) based on road network data from OpenStreetMap. It leverages several Python libraries such as `osmnx`, `networkx`, `shapely`, and`geopandas` to efficiently generate, visualize, and export isochrones.

## Features

- **Isochrone Generation**: Generate polygons representing areas reachable within a specified travel time from a given point.
- **Custom Speed**: Uses road speed limits to calculate travel times (supports multiple network types).
- **Flexible Input**: Supports both loading a pre-existing GraphML file or fetching a graph dynamically based on a place name.
- **Alphashape Option**: Supports generating concave hulls using the Alphashape algorithm for more accurate isochrones.
- **GeoJSON Export**: Save generated isochrones as GeoJSON files for easy integration with mapping tools.

## Installation

To install `IsochroneGenerator`, simply clone the repository and install the necessary dependencies.

### Clone the Repository

```bash
git clone https://github.com/jawad-iqbal99/IsochroneGenerator.git
cd IsochroneGenerator
