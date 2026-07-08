from class_request import Request
from requirements import *
from useful_functions import create_list_stops
from utils_calculs import  compute_distance_from_stop_list
class Scenario:
    def __init__(self,all_requests : list, all_stops : list, dist_matrix_km : list,dist_matrix_time : list, type_scenario : str, name_scenario : str,nb_instance : int, nb_od :int, nb_op : int,  nb_b : int = None, nb_md : int = None, nb_mp : int = None,nb_stops : int = None, total_potential_emissions : float = None):
        """
        Parameters : 
        --------------
        all_requests : list[Request]
            list of all the request to process
        all_stops :list[int]
            list of all the stops
        dist_matrix : list
            matrix of the distances between all the stops
        name_scenario : str
            name of the scenario 
        """
        
        self.all_requests = all_requests
        self.nb_requests = len(all_requests)
        self.all_stops = all_stops 
        if nb_stops :
            # print(f'nb_stop : {nb_stops}, type : {type(nb_stops)}')
            self.nb_stops = int(nb_stops)
        else :
            self.nb_stops = len(all_stops)

        self.all_stops_source = all_stops.copy()
        self.all_stops_source.insert(0,0)
    
        self.all_stops_sink = all_stops.copy()
        self.all_stops_sink.append(len(all_stops)+1)

        self.all_stops_source_sink = all_stops.copy()
        self.all_stops_source_sink.insert(0,0)
        self.all_stops_source_sink.append(len(all_stops)+1)   
        self.dist_matrix_km = dist_matrix_km
        self.dist_matrix_time = dist_matrix_time
        self.type = type_scenario
        self.name = name_scenario
        self.nb_instance = nb_instance
        self.od = nb_od
        self.op = nb_op 
        self.b = nb_b 
        self.md = nb_md 
        self.mp = nb_mp
        if self.b : 
            self.nb_drivers = self.od + self.b
            self.ratio_flexible = (nb_b * 100)/ len(all_requests)
        else : 
            # print(f'debug class_solution-- od : {type(self.od)}: {self.od}, op : {type(self.op)}: {self.op}, md : {self.md}: {self.md}, mp : {type(self.op)}: {self.mp}')
            self.nb_drivers = self.od + self.md + self.mp 
            self.ratio_flexible = ((nb_md + nb_mp) * 100)/ len(all_requests)

        all_visited_stops = [0,self.nb_stops+1]
        for requests in self.all_requests :
            # print('type : ',type(requests))
            for stop in requests.stops:
                if stop not in all_visited_stops :
                    all_visited_stops.append(stop)
        self.all_visited_stops = all_visited_stops
        self.total_potential_emissions = total_potential_emissions
        # all the stops that are actually visited : 
        self.list_stops = create_list_stops(all_requests)
        # all the stops that ate acutally visited + source and sink
        extended_list_stops = create_list_stops(all_requests)
        extended_list_stops.insert(0, 0)
        extended_list_stops.append(7)
        self.extended_list_stops = extended_list_stops
        # all the stops that are actually visited and the source
        list_stops_source = create_list_stops(all_requests)
        # list_stops_source.append(0)
        list_stops_source.insert(0, 0)
        self.list_stops_source=list_stops_source
        # all the stops that are actually visited and the sink
        list_stops_sink = create_list_stops(all_requests)
        list_stops_sink.append(7)
        self.list_stops_sink=list_stops_sink
        
        total_initial_distance_everyone_travels = 0
        for user in range(len(all_requests)):
            total_initial_distance_everyone_travels+= compute_distance_from_stop_list(list(map(int, all_requests[user].stops)),"dist_matrix_km_size15.npy")
        self.initial_distance_passenger_also = total_initial_distance_everyone_travels

    def print(self):
        """ Print the details of a scenario """
        
        print(f'\n \n------------------------- The Scenario {self.name} : -------------------------  \n')
        print(f'There are {len(self.all_requests)} requests.\n')
        for i in range (len(self.all_requests)):
            self.all_requests[i].print()
            print(f'\n')
        print(f'The stops are : {self.list_stops} \n')
        print(f'The distance matrix is : {self.dist_matrix_time}')
        print(f'There are {self.nb_drivers} probable drivers ')
        if self.total_potential_emissions: 
            print(f'Total potential emissions : {self.total_potential_emissions}')
        print(f'\n \n------------------------- end scenario {self.name} : -------------------------  \n')

def ordre_grandeur(x):
        if x == 0:
            return 0
        exp = math.floor(math.log10(abs(x)))
        return 10**exp

