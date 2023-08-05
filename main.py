import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
from shapely.geometry import Point, Polygon

place = '360 Huntington Ave, Boston, MA, United States'
# (string {"all_private", "all", "bike", "drive", "drive_service", "walk"})
network_type = 'walk'
trip_time = 15  # in minutes
travel_speed = 4.5  # walking speed in km/hour
meters_per_minute = travel_speed * 1000 / 60
cols = ["name", "amenity"]
point_of_interest={"Building": True}
# https://osmnx.readthedocs.io/en/stable/user-reference.html#module-osmnx.features
point_of_interest = {"amenity":True, "landuse":["retail","commercial"], "highway":"bus_stop"}


def main():
    ## Get graph from OSM
    Graph = ox.graph_from_address(place, network_type=network_type)

    center_node = ox.nearest_nodes(Graph, 0, 0)

    for u, v, k, data in Graph.edges(data=True, keys=True):
        data['time'] = data['length'] / meters_per_minute

    ## Get sub graph from the Graph with the radius of trip time    
    subgraph = nx.ego_graph(Graph, center_node, radius=trip_time,  distance='time')
    
    ## Get features from the sub graph
    features = ox.features_from_address(place, tags=point_of_interest, dist=trip_time * meters_per_minute * 2)

    def get_distance_from_nearest_node(geometry):
        distance = float('inf')
        if(type(geometry) == Polygon):
            nearest = ox.nearest_nodes(subgraph, geometry.centroid.x, geometry.centroid.y)
            distance = ox.distance.euclidean_dist_vec(Graph.nodes[nearest]['y'], Graph.nodes[nearest]['x'], geometry.centroid.y, geometry.centroid.x)
        return distance
    

    # filter features that are too far from the sub graph
    filtered_features = features[features['geometry'].apply(get_distance_from_nearest_node) < 0.0005]

    # https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html#geopandas-geodataframe-explore
    m = filtered_features.explore(tooltip=cols, cmap = "inferno_r")

    edges = ox.graph_to_gdfs(subgraph, nodes=False)

    edges_map = edges.explore(m=m, column = "length", popup = True, tiles = "CartoDB positron", cmap = "inferno_r")
                                        
    output_file_path = "index.html"

    edges_map.save(output_file_path)


if __name__ == "__main__":
    main()
