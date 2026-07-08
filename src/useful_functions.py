# from requirements import * 
from class_request import Request
# from class_solution import Solution
from requirements import * 
def create_list_stops(list_requests : list):
    """Creates a list with the stops that are really visited in the scenario.
    """
    list_stops = []
    for request in list_requests:
        # print(f"request : {request}")
        # print(f'stops : {request.stops}')
        if type(request) == Request :
            for stop in request.stops :
                # print(f'stop : {stop}')
                if not stop in list_stops :
                    list_stops.append(stop)
                # print(f'liste stops : {list_stops}')
        elif type(request)==dict : 
            for stop in request["stops"].keys() :
                # print(f'stop : {stop}')
                if not stop in list_stops :
                    list_stops.append(stop)
                # print(f'liste stops : {list_stops}')
    # print(f'liste stop final : {list_stops}')
    return list_stops

def ordre_grandeur(x):
        if x == 0:
            return 0
        exp = math.floor(math.log10(abs(x)))
        return 10**exp

import numpy as np
def save_dist_matrices() :
    # dist_matrix_km = np.array([
    #             [0,2.9,0.5,0.350,19.1,16],
    #             [2.9,0,3.1,2.6,19.1,16.2],
    #             [0.5,3.1,0,0.550,19.2,16.2],
    #             [0.350,2.6,0.550,0,18.9,15.8],
    #             [19.1,19.1,19.2,18.9,0,10.2],
    #             [16,16.2,16.2,15.8,10.2,0],
    #         ])
    # dist_matrix_time = np.array([
    #             [0,7,2,1,20,15],
    #             [7,0,7,7,21,16],
    #             [2,7,0,1,20,15],
    #             [1,7,1,0,19,14],
    #             [20,21,20,19,0,14],
    #             [15,16,15,14,14,0],
    #         ])
    dist_matrix_km = np.array([
                [0,2.9,0.5,0.350,19.1,16,4.3,5.4,6.6,3.4,4.7,2.5,1.9,4.4,6.3],
                [2.9,0,3.1,2.6,19.1,16.2,1.5,2.5,2.8,0.55,3.4,1.3,2.5,2.5,5.7],
                [0.5,3.1,0,0.550,19.2,16.2,4.3,5.3,6.5,2.9,4.6,2.4,1.4,3.6,5.8],
                [0.350,2.6,0.550,0,18.9,15.8,4.1,5.1,6.3,3.2,4.4,2.2,1.6,4.1,6.1],
                [19.1,19.1,19.2,18.9,0,10.2,20.6,21.6,19.4,19.7,16.5,18.7,20.3,22.4,24.6],
                [16,16.2,16.2,15.8,10.2,0,19,22.2,11.2,18.1,8.3,17.1,18.7,20.8,2.3],
                [4.3,1.5,4.3,4.1,20.6,19,0,1.5,2.7,1.5,4,3,3.2,3.4,4.9],
                [5.4,2.5,5.3,5.1,21.6,22.2,15,0,1.9,2.5,5.7,4,4.2,4.4,5.1],
                [6.6,2.8,6.5,6.3,19.4,11.2,2.7,1.9,0,2.9,3.3,4.5,4.6,4.9,5.7],
                [3.4,0.55,2.9,3.2,19.7,18.1,1.5,2.5,2.9,0,3.7,2.3,2.2,2.3,4.5],
                [4.7,3.4,4.6,4.4,16.5,8.3,4,5.7,3.3,3.7,0,3,5.7,7.9,8.4],
                [2.5,1.3,2.4,2.2,18.7,17.1,3,4,4.5,2.3,3,0,3.5,5.4,7.1],
                [1.9,2.5,1.4,1.6,20.3,18.7,3.2,4.2,4.6,2.2,5.7,3.5,0,2.5,4.7],
                [4.4,2.5,3.6,4.1,22.4,20.8,3.4,4.4,4.9,2.3,7.9,5.4,2.5,0,3.4],
                [6.3,5.7,5.8,6.1,24.6,23,4.9,5.1,5.7,4.5,8.4,7.1,4.7,3.4,0],
            ])
    dist_matrix_time = np.array([
                [0,7,2,1,20,15,10,11,11,9,9,5,5,8,13],
                [7,0,7,7,21,16,4,6,5,3,8,5,8,8,10],
                [2,7,0,1,20,15,10,11,11,9,8,5,4,6,10],
                [1,7,1,0,19,14,9,11,11,9,8,5,4,8,12],
                [20,21,20,19,0,14,24,25,23,23,18,19,21,24,28],
                [15,16,15,14,14,0,20,22,19,19,14,15,18,20,24],
                [10,4,10,9,24,20,0,4,5,6,9,9,9,8,9],
                [11,6,11,11,25,22,4,0,4,7,10,10,10,9,8],
                [11,5,11,11,23,19,5,4,0,7,6,9,11,10,10],
                [9,3,9,9,23,19,6,7,7,0,8,7,6,7,10],
                [9,8,8,8,18,14,9,10,6,8,0,7,11,14,14],
                [5,5,5,5,19,15,9,10,9,7,7,0,7,9,13],
                [5,8,4,4,21,18,9,10,11,6,11,7,0,5,9],
                [8,8,6,8,24,20,8,9,10,7,14,9,5,0,5],
                [13,10,10,12,28,24,9,8,10,10,14,13,9,5,0],
            ])
    np.save("dist_matrix_time_size15.npy", dist_matrix_time)
    np.save("dist_matrix_km_size15.npy", dist_matrix_km)
    distance_matrix_time = np.load("dist_matrix_time_size15.npy")
    distance_matrix_km = np.load("dist_matrix_time_size15.npy")
    print(distance_matrix_time)
    print(distance_matrix_km)
    return 

# save_dist_matrices()
