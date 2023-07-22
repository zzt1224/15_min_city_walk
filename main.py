import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox


def main():
    place = 'Chapinero,Bogotá,Colombia'
    network_type = 'walk'
    trip_times = [5, 10, 15, 25]  # in minutes
    travel_speed = 4.5  # walking speed in km/hour
    Graph = ox.graph_from_address(place, network_type=network_type)

    center_node = ox.nearest_nodes(Graph, 4.6519456, -74.0553)

    meters_per_minute = travel_speed * 1000 / 60
    for u, v, k, data in Graph.edges(data=True, keys=True):
        data['time'] = data['length'] / meters_per_minute

        # get one color for each isochrone
    iso_colors = ox.plot.get_colors(
        n=len(trip_times), cmap='plasma', start=0, return_hex=True)
    node_colors = {}
    for trip_time, color in zip(sorted(trip_times, reverse=True), iso_colors):
        subgraph = nx.ego_graph(
            Graph, center_node, radius=trip_time,  distance='time')
        for node in subgraph.nodes():
            node_colors[node] = color
    nc = [node_colors[node]
          if node in node_colors else 'none' for node in Graph.nodes()]
    ns = [15 if node in node_colors else 0 for node in Graph.nodes()]
    # plot graph
    fig, ax = ox.plot_graph(Graph, node_color=nc, node_size=ns, node_alpha=0.8,
                            node_zorder=2, bgcolor='k', edge_linewidth=0.2, edge_color='#999999')


if __name__ == "__main__":
    main()
