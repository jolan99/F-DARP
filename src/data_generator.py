import os
import json
import numpy as np
import random
import math
import pandas as pd
import csv
from useful_functions import create_list_stops


    

def generate_request(request_type : str, nb_stops : int, type_scenario : str = None, seed : int = None) -> dict:
    """ Generates a random requests following the given type.
    Parameters : 
    -------------
    request_type : str
        either 'od', 'b' or 'op' 
    
    Returns : 
    ------------
    dict """

    dist_matrix_time = np.load("dist_matrix_time_size15.npy")
    dist_matrix_km = np.load("dist_matrix_km_size15.npy")
    
    if seed : 
        
        random.seed(seed)
    v = int(random.randint(0, 1))
    s = v + 2
    stops = random.sample(range(1, nb_stops+1), s)
    h = int(random.randint(0, 15))
    span = int(random.randint(h+5, 25))
    stop_dict = {}
    time = h
    duration = span
    
    for i in range(s):
        stop = stops[i]
        stop_dict[int(stop)] = [int(time), int(duration)]
        
        if i < s - 1:
            next_stop = stops[i + 1]
            distance = int(dist_matrix_time[stop - 1][next_stop - 1])
            time += distance
            duration += distance
    
    people = int(random.randint(1, 2))
    pick_ups = [0] * s
    deliveries = [0] * s
    
 

    pick_ups[0] = int(random.randint(1, people))
    if pick_ups[0] < people : 
        pick_ups[1] = people - pick_ups[0]
    if s == 3 : 
        deliveries[1] = int(random.randint(0, people-1))
        deliveries[2] = people - deliveries[1]
    elif s == 2 : 
            deliveries[1] = people

    if request_type != "op":
        v_capacity = int(random.randint(3, 5))
    else : 
        v_capacity = 0

    request = {
        "stops": stop_dict,
        "pick-ups": pick_ups,
        "deliveries": deliveries,
        "v_capacity" : v_capacity
    }
    
    if request_type == "od":
        request["driver"] = True
        request["passenger"] = False
        request["only_driver"] = True
        request["only_passenger"]= False
        request["mainly_passenger"]= False
        request["mainly_driver"]= False
    elif request_type == "md":
        request["driver"] = True
        request["passenger"] = True
        request["only_driver"] = False
        request["only_passenger"]= False
        request["mainly_passenger"]=False
        request["mainly_driver"]= True
    elif request_type == "mp":
        request["driver"] = True
        request["passenger"] = True
        request["only_driver"] = False
        request["only_passenger"]= False
        request["mainly_passenger"]= True
        request["mainly_driver"]= False
    elif request_type == "op":
        request["driver"] = False
        request["passenger"] = True
        request["only_driver"] = False
        request["only_passenger"]= True
        request["mainly_passenger"]= False
        request["mainly_driver"]= False
    elif request_type == "b":
        request["driver"] = True
        request["passenger"] = True
        request["only_driver"] = False
        request["only_passenger"]= False
        request["mainly_passenger"]= False
        request["mainly_driver"]= False

    if request_type != 'op':
        ## Choose randomly a car from emissions.csv : 
        # print(f'request type : {request_type}')
        df = pd.read_csv("src\list_cars_critair.csv")
        
        categories = ["E", "1", "2", "3", "4", "5"]
        probabilites = [0.029, 0.357, 0.35, 0.179, 0.052, 0.033]
        vignette_choisie = np.random.choice(categories, p=probabilites)
        sous_df = df[df["Vignette"] == vignette_choisie]
        
        print(f"debug data generator : seed ? {seed}")
        if seed : 
            print("debug")
            ligne_aleatoire = sous_df.sample(
                n=1,
                random_state=seed
            ).iloc[0]
        else : 
            ligne_aleatoire = sous_df.sample(n=1).iloc[0]
        if vignette_choisie == "E" : 
            emission_rate_vehicle = ligne_aleatoire["CO2_emissions_min"]*15/100
        else : 
            emission_rate_vehicle = ligne_aleatoire["CO2_emissions_min"]
        car_model = ligne_aleatoire["model"]
        request["car_model"]= str(car_model)
        request["emission_rate_vehicle"]= str(emission_rate_vehicle)
        
        potential_trip_emission = sum(
                emission_rate_vehicle * float(dist_matrix_km[stops[i]-1, stops[i+1]-1])
                for i in range(len(stops) - 1)
            )
    else : 
        potential_trip_emission = sum(
                168 * float(dist_matrix_km[stops[i]-1, stops[i+1]-1])
                for i in range(len(stops) - 1)
            )
    request["potential_trip_emission"]= str(potential_trip_emission)
    return request

def generate_scenarios_D(od : int, op : int,md : int,mp : int,x : int,nb_stops, seed : int = None)-> None:
    """ Generates scenarios randomly 
    Parameters : 
    -------------
    od : int 
        number of only drivers 
    op : int 
        number of onmy passenger
    md : int 
        number of mainly driver 
    mp : int 
        number of mainly passenger
    x : int 
        number of instances created 
    nb_stops : int
        number of possible stops in the scenario
    Returns : 
    ----------
    dict :  {list of the requests}
     """ 
    folder_name = "Scenarios/Scenarios_D"
    os.makedirs(folder_name, exist_ok=True)
    created_files = []
    csv_file = "instances_created.csv"

    for i in range(1, x + 1):
    
        requests = []
        
        for _ in range(od):
            requests.append(generate_request("od",nb_stops,seed))
        for _ in range(op):
            requests.append(generate_request("op",nb_stops,seed))
        for _ in range(md):
            requests.append(generate_request("md",nb_stops,seed))
        for _ in range(mp):
            requests.append(generate_request("mp",nb_stops,seed))
        
        list_stops =create_list_stops(requests)
        # print(f'debug !! list stops : {list_stops}')
        instance_data = {"requests": requests}

        file_name = f"{folder_name}/D_{len(list_stops)}_{od+op+md+mp}_od{od}_op{op}_md{md}_mp{mp}_{i}.json"
        if not os.path.exists(file_name):
            with open(file_name, "w") as f:
                json.dump(instance_data, f, indent=4)
            created_files.append(file_name)
            print(f"Instance saved as {file_name}")
        else:
            print(f"Fichier déjà existant, instance non enregistrée : {file_name}")

        
        
        
    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for name in created_files:
            writer.writerow([name])


def run_all_combinations():
    total_combinations = 0
    csv_file = "instances_created.csv"

    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename"])  


    for nb_stops in range(7, 15):
        for nb_requests in range(2, 11):  # nb_requests from 2 to 10
            max_op = math.floor(0.3 * nb_requests)
            max_od = math.floor(0.8 * nb_requests)
            min_md_mp_sum = math.ceil(0.5 * nb_requests)

            for op in range(0, max_op + 1):
                for od in range(0, max_od + 1):
                    remaining = nb_requests - op - od
                    if remaining < 0:
                        continue  

                    # md + mp must be equal to remaining AND ≥ 50% of nb_requests
                    if remaining < min_md_mp_sum:
                        continue  # doesn't meet md+mp constraint

                    # Now vary md from 0 to remaining, mp = remaining - md
                    for md in range(0, remaining + 1):
                        mp = remaining - md
                        # valid combination found
                        generate_scenarios_D(od, op, md, mp, 4,nb_stops)
                        total_combinations += 1

 
number_od = 30
number_op = 10
number_md = 40
number_mp = 20
number_scenarios=1
geographic_size=15
set_seed=10

generate_scenarios_D(number_od,number_op,number_md,number_mp,number_scenarios,geographic_size,seed = 10)
# run_all_combinations()

