# gRPC Imports
import grpc

import CityWasteCollectionClient
import WasteCollectionGroundControl_pb2
import WasteCollectionGroundControl_pb2_grpc

# Graphing Imports
import pylab
import numpy as np
import networkx as nx
import matplotlib.pyplot as plot
import pprint

# Threading Imports
from concurrent import futures
import threading

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

    all_source_to_target_paths_integer = [list(map(int, lst)) for lst in all_source_to_target_paths]

    print("\nAll source-to-target paths:")
    pprint.pprint(all_source_to_target_paths_integer)

    # Return paths.
    return all_source_to_target_paths_integer


# Routes Global Variable
global_routes_list = GetNetworkPaths()


# Dispatcher Function (Threaded)
def Dispatcher(vehicle_id, vehicle_type, route_list):

    # Dispatch another vehicle with the route provided by the caller vehicle.
    CityWasteCollectionClient.main(vehicle_id + 50, vehicle_type, route_list)

    # Print statement.
    print(f"Dispatching Vehicle #{vehicle_id + 50} to continue Vehicle #{vehicle_id}'s path. "
          f"Starting at node #{route_list[0]}.")


# ----------------------------------------------------------------------------------------------------------------------
# GRPC SERVICE
# ----------------------------------------------------------------------------------------------------------------------
class WasteCollectionServiceServicer(WasteCollectionGroundControl_pb2_grpc.WasteCollectionServiceServicer):

    # GetRoute Function
    def GetRoute(self, request, context):

        # Request
        vehicle_id = request.vehicle_id
        vehicle_type = request.vehicle_type

        # Call GetNetworkPaths
        if len(global_routes_list) > 0:

            # Read first available route.
            route_list = global_routes_list[0]

            # Print to terminal.
            print(f"Vehicle #{vehicle_id} ({vehicle_type}) has been assigned route: {route_list}")

            # Remove assigned route.
            # global global_routes_list
            global_routes_list.pop(0)

            # Create Response
            collection_route = WasteCollectionGroundControl_pb2.CollectionRoute()
            collection_route.nodes.extend(route_list)

            return collection_route

        else:

            # Print to terminal.
            print(f"Vehicle #{vehicle_id} ({vehicle_type}) cannot be assigned a route.")

            # Create response (with values -1)
            collection_route = WasteCollectionGroundControl_pb2.CollectionRoute()
            collection_route.nodes.extend([-1, -1])

            return collection_route

    # DispatchAnotherVehicle Function
    def DispatchAnotherVehicle(self, request, context):

        # Request
        vehicle_id = request.vehicle_id
        vehicle_type = request.vehicle_type
        remaining_nodes = request.remaining_nodes

        # Print to terminal.
        print(f"Request received from Vehicle #{vehicle_id} "
              f"to dispatch another vehicle to remaining route {remaining_nodes}.")

        # Call dispatcher.
        # Start Dispatcher Thread
        dispatcher_thread = threading.Thread(target=Dispatcher, args=[vehicle_id, vehicle_type, remaining_nodes])
        dispatcher_thread.start()

        # Response
        response = WasteCollectionGroundControl_pb2.DispatchInfo()
        response.vehicle_id = vehicle_id
        response.vehicle_type = vehicle_type
        response.startNode = remaining_nodes[0]

        return response


# ----------------------------------------------------------------------------------------------------------------------
# MAIN SERVER FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

# Main Function
def main():

    # Server Definition
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    WasteCollectionGroundControl_pb2_grpc.add_WasteCollectionServiceServicer_to_server(WasteCollectionServiceServicer(),
                                                                                       server)
    # Select port and start server.
    server.add_insecure_port('[::]:44444')
    server.start()
    print('City Waste Collection Server Started...')

    # Blocking Call
    server.wait_for_termination()


# Startup
if __name__ == '__main__':
    main()
