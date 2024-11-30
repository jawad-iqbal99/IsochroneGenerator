import os
import functools
from typing import List, Union
import networkx as nx
import osmnx as ox
from shapely.geometry import Point, Polygon
import geopandas as gpd
from alphashape import alphashape

class IsochroneGenerator:
    def __init__(self, graph_path: str = None, place_name: str = None, network_type: str = 'drive', default_speed: float = 48.28):
        """
        Initialize the IsochroneGenerator with a road network graph.

        Parameters:
        - graph_path (str): Path to the road network graphml file. If None, will attempt to fetch the graph from `place_name`.
        - place_name (str): Name of the place to fetch the graph from OpenStreetMap (if `graph_path` is not provided).
        - network_type (str): The type of road network to fetch ('drive', 'walk', 'bike', 'all'). Default is 'drive'.
        - default_speed (float): Default speed to use when max speed is not available for an edge.
        """
        self.DEFAULT_SPEED = default_speed
        self.graph_path = graph_path
        self.place_name = place_name
        self.network_type = network_type
        
        if graph_path:
            self.G = self._load_graph_from_file()
        elif place_name:
            self.G = self._load_graph_from_place(place_name)
        else:
            raise ValueError("You must provide either a 'graph_path' or a 'place_name'.")

        self.__update_graph_with_times()

    def _load_graph_from_file(self) -> nx.Graph:
        """
        Load the road network graph from a GraphML file.

        Returns:
        - nx.Graph: The road network graph.
        """
        if not os.path.exists(self.graph_path):
            raise FileNotFoundError(f"Graph file not found at {self.graph_path}")
        return ox.load_graphml(self.graph_path)

    def _load_graph_from_place(self, place_name: str) -> nx.Graph:
        """
        Load the road network graph for a given place name from OpenStreetMap.

        Parameters:
        - place_name (str): The name of the place (e.g., 'Somerset, UK').

        Returns:
        - nx.Graph: The road network graph.
        """
        print(f"Fetching road network graph for {place_name} from OpenStreetMap...")
        graph = ox.graph_from_place(place_name, network_type=self.network_type)
        
        # Save the graph to a GraphML file for future use
        self.graph_path = f"{place_name.replace(' ', '_').replace(',', '')}_{self.network_type}.graphml"
        ox.save_graphml(graph, self.graph_path)
        
        print(f"Graph for {place_name} ({self.network_type}) saved as {self.graph_path}")
        return graph

    def __update_graph_with_times(self) -> None:
        """
        Update graph edges with travel times based on maximum speed limits.
        """
        for u, v, k, data in self.G.edges(data=True, keys=True):
            if max_speed := data.get("maxspeed"):
                if isinstance(max_speed, list):
                    speed = sum(self.__parse_max_speed_to_kmh(s) for s in max_speed) / len(max_speed)
                else:
                    speed = self.__parse_max_speed_to_kmh(max_speed)
            else:
                speed = self.DEFAULT_SPEED

            meters_per_minute = speed * 1000 / 60  # km per hour to meters per minute       
            data['time'] = data['length'] / meters_per_minute

    def __parse_max_speed_to_kmh(self, max_speed: str) -> float:
        """
        Convert a max speed string to kilometers per hour.

        Parameters:
        - max_speed (str): The max speed string (e.g., '50 km/h' or '60 mph').

        Returns:
        - float: Speed in kilometers per hour.
        """
        conversion = 1.60934 if "mph" in max_speed else 1
        speed = int(max_speed.split()[0]) * conversion
        return speed if speed else self.DEFAULT_SPEED
    
    @functools.lru_cache(maxsize=128)
    def generate_isochrone(self, lat: float, lon: float, max_drive_time: float, use_alphashape: bool = False) -> Union[Polygon, List[Polygon]]:
        """
        Generate isochrone polygons based on a specified travel time.

        Parameters:
        - lat (float): Latitude of the center point.
        - lon (float): Longitude of the center point.
        - max_drive_time (float): Maximum travel time in minutes.
        - use_alphashape (bool): Whether to use alphashape to create concave hulls.

        Returns:
        - Union[Polygon, List[Polygon]]: Generated isochrone polygon(s).
        """
        # Find the nearest node to the given lat/lon
        center_node = ox.distance.nearest_nodes(self.G, lon, lat)

        # Get the nodes within the max travel time radius
        nodes_within_travel_time = [
            Point(data['x'], data['y']) 
            for index, data in nx.ego_graph(self.G, center_node, radius=max_drive_time, distance='time').nodes(data=True)
        ]

        # Combine the points to create the convex hull of the reachable area
        polys = gpd.GeoSeries(nodes_within_travel_time).union_all().convex_hull
        if use_alphashape:
            points = [(x.x, x.y) for x in nodes_within_travel_time]
            polys = alphashape(points, alpha=10) if alphashape(points, alpha=10).geom_type != 'MultiPolygon' else alphashape(points, alpha=20)
            
        return polys

    def save_isochrone_to_geojson(self, lat: float, lon: float, max_drive_time: float, filename: str, use_alphashape: bool = False) -> None:
        """
        Generate an isochrone and save it as a GeoJSON file.

        Parameters:
        - lat (float): Latitude of the center point.
        - lon (float): Longitude of the center point.
        - max_drive_time (float): Maximum travel time in minutes.
        - filename (str): The filename for the GeoJSON output.
        - use_alphashape (bool): Whether to use alphashape for concave hulls.
        """
        isochrone = self.generate_isochrone(lat, lon, max_drive_time, use_alphashape)
    
        # Create the GeoSeries
        isochrone_gdf = gpd.GeoSeries([isochrone])
    
        # Set the CRS explicitly if not already set
        if isochrone_gdf.crs is None:
            isochrone_gdf.set_crs("EPSG:4326", allow_override=True, inplace=True)
    
        # Export the isochrone as GeoJSON
        isochrone_gdf.to_file(filename, driver="GeoJSON")