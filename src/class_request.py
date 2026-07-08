## Defines the request class
from requirements import *
from utils_calculs import compute_distance_from_stop_list
class Request:
    def __init__(
        self,
        user_id: int,
        stops: list,
        nb_stops: int,
        pick_ups: list,
        deliveries: list,
        time_windows: dict,
        v_capacity: int,
        limit_via: int,
        driver: bool,
        passenger: bool,
        only_driver : bool = None, 
        only_passenger : bool = None,
        mainly_driver : bool = None,
        mainly_passenger : bool = None,
        ref_gaspoz : str = None,
        emission_rate_vehicle : float = None,
        potential_trip_emission : float = None,
        car_model : str = None,
    ) -> None:
        """Initializes an object of the class Request

        Parameters :
        --------------

        user_id : int
            Id of the user/ of the request.
        stops : list[int]
            List of the stops requested by the user. They are in order. That is,that is, if stops = [3,80], then stop 3 has to be visited before stop 80.
        nb_stops : int
            The total number of stops required.
        picks_up : list[int]
            For each stop, gives the number of people to be taken in the car for this request
        deliveries : list[int]
            For each stop, gives the number of people to be leave the car for this request.
        time_windows : dict
            Contains as many keys as there are stops to be visited in this request.
            For each stop, a lit of 2 integer is a given which indicated the earlier and latest time to be in a location.
            For example, dict = { "3": [4,12],"12": [5,13]}  Here, the request is to be at "3" between times 4 and 12, and to be at "12" between times 5 and 13.
        v_capacity : int
            Idicates the capacity of the vehicle driven by the user. If the user does not drive, the capacity is 0.
        driver : bool
            If True, the user accpets to be a driver for this request
        passenger : bool
            If True, the user accepts to be a passenger for this request.

        """
        self.user_id = user_id
        self.stops = stops
        self.nb_stops = nb_stops  ## can be taken with len(self.stops)
        self.pick_ups = pick_ups
        self.deliveries = deliveries
        self.time_windows = time_windows
        self.v_capacity = v_capacity
        self.limit_via = limit_via
        self.driver = driver
        self.passenger = passenger
        self.only_driver = only_driver
        self.only_passenger = only_passenger
        self.mainly_driver = mainly_driver
        self.mainly_passenger = mainly_passenger
        self.ref_gaspoz = ref_gaspoz
        self.emission_rate_vehicle = emission_rate_vehicle
        self.potential_trip_emission = potential_trip_emission
        self.car_model = car_model
        self.initial_distance = compute_distance_from_stop_list(self.stops,"dist_matrix_km_size15.npy")
    
    def print(self):
        """ Print all the details of a request"""
        
        print(f'Details of the request #{self.user_id}')
        print(f'The {self.nb_stops} stops to pass by are : {self.stops}')
        print(f"debug class_request : initial distance : {self.initial_distance}")
        print(f'picks-up : {self.pick_ups}, and deliveries : {self.deliveries}')
        print(f'time windows : {self.time_windows}')
        if self.only_driver :
            print(f'Role : only driver')
        elif self.only_passenger :
            print(f'Role : only passenger')
        elif self.mainly_driver :
            print(f'Role : mainly driver')
        elif self.mainly_passenger :
            print(f'Role : mainly passenger')
        if self.emission_rate_vehicle : 
            print(f'emission rate of the vehicle : {self.emission_rate_vehicle}')
        if self.car_model : 
            print(f'car model : {self.car_model}')
        print(f'potential_trip_emission : {self.potential_trip_emission}')
        print(f'driver : {self.driver},  passenger : {self.passenger},  vehicle_capacity : {self.v_capacity}')

    