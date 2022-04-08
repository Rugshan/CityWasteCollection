# gRPC Imports
import grpc
import WasteCollectionGroundControl_pb2
import WasteCollectionGroundControl_pb2_grpc

# Imports
import sys
import random

# Global Variables
# Variables
total_capacity_litres = 21000.0
current_capacity_litres = 0.0


# ----------------------------------------------------------------------------------------------------------------------
# SERVICE FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

# GetRoute Service Function
def GetRoute(id_arg, type_arg):

    # gRPC Channel
    with grpc.insecure_channel('0.0.0.0:44444', options=(('grpc.enable_http_proxy', 0),)) as channel:

        # Stub and Response
        stub = WasteCollectionGroundControl_pb2_grpc.WasteCollectionServiceStub(channel)
        response = stub.GetRoute(WasteCollectionGroundControl_pb2.VehicleIdentifier(vehicle_id=id_arg,
                                                                                    vehicle_type=type_arg))

    # Extract route from response
    route_list = response.nodes

    return route_list


# DispatchAnotherVehicle Service Function
def DispatchAnotherVehicle(vehicle_id, vehicle_type, remaining_nodes):

    # gRPC Channel
    with grpc.insecure_channel('0.0.0.0:44444', options=(('grpc.enable_http_proxy', 0),)) as channel:

        # Stub
        stub = WasteCollectionGroundControl_pb2_grpc.WasteCollectionServiceStub(channel)

        # Request
        request = WasteCollectionGroundControl_pb2.VehicleCurrentContext()
        request.vehicle_id = vehicle_id
        request.vehicle_type = vehicle_type
        request.remaining_nodes.extend(remaining_nodes)

        # Response
        response = stub.DispatchAnotherVehicle(request)

    # Extract response.
    print(f"[CityWasteCollectionServer] Dispatched Vehicle #{response.vehicle_id} "
          f"to finish remaining path starting at node #{response.startNode}")


# ----------------------------------------------------------------------------------------------------------------------
# COLLECTION FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

# Collection down a portion of the route (between two nodes).
def CollectWaste(from_node, to_node, route_list):

    # Initial print statement.
    print(f"Collecting from node {from_node} to node {to_node}.")

    # Simulating x number of collections along node pair.
    number_of_collections = random.randint(5, 11)

    for i in range(1, number_of_collections + 1):

        # Simulate volume per collection.
        collection_volume_litres = random.randint(25, 1000)

        # Check if capacity is available.
        global current_capacity_litres
        if current_capacity_litres + collection_volume_litres <= total_capacity_litres:

            current_capacity_litres += collection_volume_litres

            # Print status.
            print(f"Collected {collection_volume_litres} litres of waste. "
                  f"Vehicle's volume: {current_capacity_litres}L/{total_capacity_litres}L")

            # RabbitMQ to Log

        else:

            # Print status.
            print("Vehicle does not have enough capacity, requesting for another vehicle to continue route...")

            # Remaining Path
            remaining_start_index = route_list.index(from_node)
            remaining_end_index = len(route_list)
            remaining_nodes = route_list[remaining_start_index:remaining_end_index]

            # Request another vehicle.
            DispatchAnotherVehicle(vehicle_id, vehicle_type, remaining_nodes)

            # Break (isDone)
            return True

    # Not done.
    return False

# ----------------------------------------------------------------------------------------------------------------------
# MAIN PROGRAM
# ----------------------------------------------------------------------------------------------------------------------


# Main Program
def main(id_arg, type_arg, *args):

    # Retrieve route; either automatically or dispatched by server.

    if len(args) == 0:
        route_list = list(GetRoute(id_arg, type_arg))
    else:
        route_list = list(args)

    print(f"[Vehicle #{id_arg} ({type_arg})] Route: {route_list}")

    is_done_response = False

    # Collect waste along each edge in the given path.
    for i, from_node in enumerate(route_list):

        if (i + 1) < len(route_list) and not is_done_response:
            to_node = route_list[i+1]
            is_done_response = CollectWaste(from_node, to_node, route_list)

# Startup
if __name__ == '__main__':

    # Get command line argument for vehicle ID and type
    vehicle_id = int(sys.argv[1])
    vehicle_type = str(sys.argv[2])

    # Start main program.
    main(vehicle_id, vehicle_type)


