from requirements import *
def compute_distance_from_stop_list(stop_list : list,dist_matrix_path : str):
    """ Computes the distance of an itinerary

    Parameters : 
    ------------
    stop_list : list 
        ex : [1,3,4]
    dist_matrix : str 
        path to the distance matrix. Ex : "dist_matrix_km_size6.npy"


    Returns : 
    ----------
    distance : float 
        the distance of the itinerary
    """
    dist_matrix_km = np.load(dist_matrix_path)
    # print(dist_matrix_km)
    if len(stop_list) < 2:
        return 0

    distance = 0
    

    for origin, destination in zip(stop_list[:-1], stop_list[1:]):
        # print(f'debug utils_calculs : origine : {origin}, destination : {destination}')
        if origin == 0 : 
            pass
        elif destination == len(dist_matrix_km)+1 :
            pass
        elif origin > len(dist_matrix_km) :
            print(f"ERROR compute_distance_from_stop_list : The matrix distance is not big enough.")
            return
        else:
            distance += dist_matrix_km[origin-1][destination-1]
    # print(distance)
    return distance

# print(f'[11,10], {compute_distance_from_stop_list([11,10],"dist_matrix_km_size15.npy")}')
# print(f'[12,1,9], {compute_distance_from_stop_list([12,1,9],"dist_matrix_km_size15.npy")}')
# print(f'[8,5,10], {compute_distance_from_stop_list([8,5,10],"dist_matrix_km_size15.npy")}')
# print(f'[9,8], {compute_distance_from_stop_list([9,8],"dist_matrix_km_size15.npy")}')
# print(f'[3,7], {compute_distance_from_stop_list([3,7],"dist_matrix_km_size15.npy")}')
# print(f'[12,14], {compute_distance_from_stop_list([12,14],"dist_matrix_km_size15.npy")}')
