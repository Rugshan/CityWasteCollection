# gRPC Imports
import grpc
import networkx

import WasteCollectionGroundControl_pb2
import WasteCollectionGroundControl_pb2_grpc

# Graphing Imports
import pylab
import numpy as np
import networkx as nx
import matplotlib.pyplot as plot
import pprint


# ----------------------------------------------------------------------------------------------------------------------
# GRPC SERVICE
# ----------------------------------------------------------------------------------------------------------------------
class WasteCollectionServiceServicer(WasteCollectionGroundControl_pb2_grpc.WasteCollectionServiceServicer):

    # GetRoute Function
    def GetRoute(self, request, context):

        # Call GetNetworkPaths
        # Send route to client; Make sure route hasn't been taken already.

        return 0

    # DispatchAnotherVehicle Function
    def DispatchAnotherVehicle(self, request, context):

        return 0


# ----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

# GetMapNetwork
def GetMapNetwork():

    # Get node-pairs (edges) in a list of tuples.
    with open('maps/NodeMap.txt', 'r') as f:
        edge_tuples = [tuple(line.split()) for line in f]
        f.close()

    # Create a directed graph.
    map_graph = nx.DiGraph()
    map_graph.add_edges_from(edge_tuples)

    # Draw directed graph.
    pos = nx.kamada_kawai_layout(map_graph)
    nx.draw_networkx_nodes(map_graph, pos, node_color="cyan", node_size=100, alpha=1)
    nx.draw_networkx_labels(map_graph, pos, font_size=8)
    nx.draw_networkx_edges(map_graph, pos, edgelist=edge_tuples, arrows=True)
    plot.show()

    # Get source and target nodes of DiGraph.
    sources = [x for x in map_graph.nodes() if map_graph.out_degree(x) == 1 and map_graph.in_degree(x) == 0]
    targets = [x for x in map_graph.nodes() if map_graph.out_degree(x) == 0 and map_graph.in_degree(x) == 1]

    # Return dict containing DiGraph, sources, targets.
    map_dict = {
        "map_graph": map_graph,
        "sources": sources,
        "targets": targets
    }

    return map_dict


# Return NetworkPaths
def GetNetworkPaths():

    # Get and extract map dict.
    map_dict = GetMapNetwork()
    map_graph = map_dict["map_graph"]
    sources = map_dict["sources"]
    targets = map_dict["targets"]

    # Print Source and Target nodes.
    pprint.pprint(f"Source Nodes: {sources}")
    pprint.pprint(f"Target Nodes: {targets}")

    # Get all pair paths.
    all_paths = dict(nx.all_pairs_shortest_path(map_graph, cutoff=7))

    # Reduce to all source nodes
    all_source_paths = {s: all_paths[s] for s in sources}

    # Reduce to starting at source and ending at target.
    all_source_to_target_paths = []

    for s in all_source_paths:
        for t in all_source_paths[s]:
            if t in targets:
                source_to_target_path = all_source_paths[s][t]
                all_source_to_target_paths.append(source_to_target_path)

    print("\nAll source-to-target paths:")
    pprint.pprint(all_source_to_target_paths)

    # Return paths.
    return all_source_to_target_paths


# ----------------------------------------------------------------------------------------------------------------------
# MAIN SERVER FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

# Main Function
def main():
    GetNetworkPaths()


# Startup
if __name__ == '__main__':
    main()
