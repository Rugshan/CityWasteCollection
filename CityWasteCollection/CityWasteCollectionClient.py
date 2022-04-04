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


# ----------------------------------------------------------------------------------------------------------------------
# COLLECTION FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

# Collection down a portion of the route (between two nodes).
def CollectWaste(from_node, to_node):

    # Initial print statement.
    print(f"Collecting from node {from_node} to node {to_node}.")

    # Simulating x number of collections along node pair.
    number_of_collections = random.randint(5, 11)

    for i in range(1, number_of_collections + 1):

        # Simulate volume per collection.
        collection_volume_litres = random.randint(25, 750)

        # Check if capacity is available.
        global current_capacity_litres
        if current_capacity_litres + collection_volume_litres <= total_capacity_litres:

            # global current_capacity_litres
            current_capacity_litres += collection_volume_litres

            print(f"Collected {collection_volume_litres} litres of waste. "
                  f"Vehicle's volume: {current_capacity_litres}L/{total_capacity_litres}L")

        else:

            print("Vehicle does not have enough capacity, requesting for another vehicle to continue route...")


# ----------------------------------------------------------------------------------------------------------------------
# MAIN PROGRAM
# ----------------------------------------------------------------------------------------------------------------------


# Main Program
def main(id_arg, type_arg):

    # Retrieve route.
    route_list = GetRoute(id_arg, type_arg)
    print(f"[Vehicle #{id_arg} ({type_arg})] Route: {route_list}")

    #
    for i, from_node in enumerate(route_list):

        if (i + 1) < len(route_list):
            to_node = route_list[i+1]
            CollectWaste(from_node, to_node)



# Startup
if __name__ == '__main__':

    # Get command line argument for vehicle ID and type
    vehicle_id = int(sys.argv[1])
    vehicle_type = str(sys.argv[2])

    # Start main program.
    main(vehicle_id, vehicle_type)


