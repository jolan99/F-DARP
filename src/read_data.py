import json
from pathlib import Path
from class_request import Request
from class_scenario import Scenario
from requirements import *

def creates_instance(file_path: str) -> Scenario:
    """ Creates scenario from json file 
    Parameters : 
    ------------
    file_path : str
        The path towards the json file where the scenario data is collected
    
    Returns : 
    ------------
    scenario : Scenario    
        The data as a Scenario object
    """
    # print(f'debug 1')
    # print(f'debug read_data : file path : {file_path}')
    with open(file_path, "r") as file:
        scenario = json.load(file)
    
    requests = []
    total_potential_emissions = 0
    # print(f'debug 2')
    for i, req in enumerate(scenario["requests"], start=1):
        # Conversion des éléments de stops en int
        stops = [int(stop) for stop in req["stops"].keys()]
        time_windows = req["stops"]

        if "only_driver" in req:
            only_driver = req["only_driver"]
            only_passenger=req["only_passenger"]
            mainly_driver =req["mainly_driver"]
            mainly_passenger =req["mainly_passenger"]
        else : 
            only_driver = None
            only_passenger=None
            mainly_driver =None
            mainly_passenger =None
        if "v_capacity" in req :
            v_capacity=req["v_capacity"]
        else : 
            v_capacity=5
        if "emission_rate_vehicle" in req : 
            emission_rate_vehicle = float(req["emission_rate_vehicle"])
        else : 
            emission_rate_vehicle = 0

        
        if "car_model" in req : 
            car_model = req["car_model"]
        else : 
            car_model = None
        if "potential_trip_emission" in req :
            total_potential_emissions += float(req["potential_trip_emission"])
            potential_trip_emission = req["potential_trip_emission"]
        else : 
            total_potential_emissions = None
            potential_trip_emission = None 
        # print(f'debug 3')
        request = Request(
            user_id=i,
            stops=stops,
            nb_stops=len(stops),
            pick_ups=req["pick-ups"],
            deliveries=req["deliveries"],
            time_windows=time_windows,
            v_capacity=v_capacity,
            limit_via=15,
            driver=req["driver"],
            passenger=req["passenger"],
            only_driver=only_driver , 
            only_passenger=only_passenger,
            mainly_driver=mainly_driver,
            mainly_passenger =mainly_passenger,
            ref_gaspoz=None,
            emission_rate_vehicle = emission_rate_vehicle,
            car_model = car_model,
            potential_trip_emission = potential_trip_emission,
        )
        # print(f'debug 4')
        requests.append(request)
    
    # gets the name of the scenario
    # print(f'debug 5')
    path_scenario = os.path.normpath(file_path).replace("\\", "/")
    parties = path_scenario.split("/")
    full_name_scenario = parties[-1]
    # print(f' full_name : {full_name_scenario}')
    match = re.match(r"^([A-Z])_(.+)$", full_name_scenario)
    # print(f'debug 6')
    if match:
        type_scenario = match.group(1)
        name_scenario = match.group(2).replace(".json", "")
        # print(f'debug read data -- type scenario : {type_scenario}, name_scenario : {name_scenario}')
    else:
        print(f"Format non reconnu : {full_name_scenario}")

    # print(f'debug 7')
    # all_stops = [1, 2, 3, 4, 5,6]
    
    if (type_scenario == "A") or (type_scenario == "B") :
        all_stops = [1, 2, 3, 4, 5,6]
        dist_matrix_time = np.array([[0,4,4,16,4,16], [4,0,15,2,14,2], [4,15,0,12,1,12],[16,2,12,0,12,1],[4,14,1,12,0,1],[16,2,12,1,1,0]])
    # else : 
    #     all_stops = np.arange(1, int(nb_stops) + 1)
    #     dist_matrix_time = get_submatrix(int(nb_stops))
    #     all_stops = [1, 2, 3, 4, 5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    #     dist_matrix_time = np.array([
    #     [0,2,4,9,6,5,14,16,5,2,7,4,16,17,20,12,17,17,6,6], 
    #     [2,0,3,7,7,4,13,15,5,3,5,6,19,20,21,11,16,17,5,6], 
    #     [4,3,0,9,9,6,15,17,7,2,7,7,21,21,23,13,18,18,6,7],
    #     [9,7,9,0,9,7,14,15,4,8,8,9,19,20,21,11,15,16,6,5],
    #     [6,7,9,9,0,6,18,20,11,8,1,4,24,25,26,16,13,14,5,6],
    #     [5,4,6,7,6,0,16,17,8,6,2,4,21,22,23,14,12,15,3,3],
    #     [14,13,15,14,18,16,0,6,11,15,17,18,14,15,16,4,14,12,16,17],
    #     [16,15,17,15,20,17,6,0,13,17,19,20,16,17,18,6,16,14,18,19],
    #     [5,5,7,4,11,8,11,13,0,6,8,9,17,18,19,9,17,16,8,7],
    #     [2,3,2,8,8,6,15,17,6,0,7,6,18,21,22,12,17,18,6,7],
    #     [7,5,7,8,1,2,17,19,8,7,0,4,24,26,27,17,13,13,3,5],
    #     [4,6,7,9,4,4,18,20,9,6,4,0,22,24,25,15,15,15,5,5],
    #     [16,19,21,19,24,21,14,16,17,18,24,22,0,6,9,10,17,18,22,23],
    #     [17,20,21,20,25,22,15,17,18,21,26,24,6,0,8,13,18,21,24,24],
    #     [20,21,23,21,26,23,16,18,19,22,27,25,9,8,0,14,19,18,24,25],
    #     [12,11,13,11,16,14,4,6,9,12,17,15,10,13,14,0,12,11,14,15],
    #     [17,16,18,15,13,12,14,16,17,13,13,15,17,18,19,12,0,3,13,15],
    #     [17,17,18,16,14,15,12,14,16,18,13,15,18,21,18,11,3,0,14,15],
    #     [6,5,6,6,5,3,16,18,8,6,3,5,22,24,24,14,13,14,0,4],
    #     [6,6,7,5,6,3,17,19,7,7,5,5,23,24,25,15,15,15,4,0],
    # ])
    # print(f'debug 7')
    if type_scenario == "A":
        type_, nb_requests, od, b, op, nb_instance = parse_filename(full_name_scenario)
        dist_matrix_km = []
        scenario = Scenario(requests, all_stops, dist_matrix_km,dist_matrix_time,type_scenario, name_scenario, nb_instance,nb_od=od, nb_op=op,nb_b=b)
    elif type_scenario == "B":
        dist_matrix_km = []
        type_, nb_requests, od, op, md, mp, nb_instance = parse_filename(full_name_scenario)
        scenario = Scenario(requests, all_stops, dist_matrix_km,dist_matrix_time,type_scenario, name_scenario, nb_instance,nb_od=od, nb_op=op,nb_md=md,nb_mp= mp)
    else :
        # print(f'debug 8')
        # print(f'total_potential_emissions ; {total_potential_emissions} ')
        # print(f'full_name_scenario : {full_name_scenario}')
        type_, nb_requests, od, op, md, mp, nb_instance, nb_stops = parse_filename(full_name_scenario)
        all_stops = list(range(1, nb_stops + 1))
        # dist_matrix_time,dist_matrix_km= get_submatrix(nb_stops,type_scenario)
        # dist_matrix_km = np.array([
        #     [0,2.9,0.5,0.350,19.1,16],
        #     [2.9,0,3.1,2.6,19.1,16.2],
        #     [0.5,3.1,0,0.550,19.2,16.2],
        #     [0.350,2.6,0.550,0,18.9,15.8],
        #     [19.1,19.1,19.2,18.9,0,10.2],
        #     [16,16.2,16.2,15.8,10.2,0],
        # ])
        # dist_matrix_time = np.array([
        #     [0,7,2,1,20,15],
        #     [7,0,7,7,21,16],
        #     [2,7,0,1,20,15],
        #     [1,7,1,0,19,14],
        #     [20,21,20,19,0,14],
        #     [15,16,15,14,14,0],
        # ])
        dist_matrix_time = np.load("dist_matrix_time_size15.npy")
        dist_matrix_km = np.load("dist_matrix_time_size15.npy")
        # print(f'debug 9')
        scenario = Scenario(requests, all_stops, dist_matrix_km,dist_matrix_time,type_scenario, name_scenario, nb_instance,nb_od=od, nb_op=op,nb_md=md,nb_mp= mp,nb_stops = nb_stops,total_potential_emissions = total_potential_emissions)
        # print(f'debug 10')
    # print(f'debug 11')
    return scenario


# instance = creates_instance("instance_od2_b3_op1_1.json")
# instance.print()

def parse_filename(filename):
    # Supprimer l'extension si présente
    name = filename.replace(".json", "")
    # print(f'debug read_data.py : name : {name}')
    # Type A : A_<nb_requests>_od<od>_b<b>_op<op>_<nb_instance>
    # pattern_a = r'^A_(\d+)_od(\d+)_b(\d+)_op(\d+)_(\d+)$'
    pattern_a = r'^A_od(\d+)_b(\d+)_op(\d+)_(\d+)$'

    
    # Type B : B_<nb_requests>_od<od>_op<op>_md<md>_mp<mp>_(<nb_instance>)
    pattern_b = r'^B_(\d+)_od(\d+)_op(\d+)_md(\d+)_mp(\d+)_(\d+)$'
    pattern_c = r'^C_(\d+)_od(\d+)_op(\d+)_md(\d+)_mp(\d+)_(\d+)$'
    pattern_c = r'^C_(\d+)_(\d+)_od(\d+)_op(\d+)_md(\d+)_mp(\d+)_(\d+)$'
    pattern_d = r'^D_(\d+)_(\d+)_od(\d+)_op(\d+)_md(\d+)_mp(\d+)_(\d+)$'

    match_a = re.match(pattern_a, name)
    match_b = re.match(pattern_b, name)
    match_c = re.match(pattern_c, name)
    match_d = re.match(pattern_d, name)
    # print(f'debug read_data match_a : {match_a}, match_b : {match_b}, match_c : {match_c}, mathc_d :  {match_d}')
    if match_a:
        type_ = 'A'
        # nb_requests = int(match_a.group(1))
        # od = int(match_a.group(2))
        # b = int(match_a.group(3))
        # op = int(match_a.group(4))
        # nb_instance = int(match_a.group(5))
        od = int(match_a.group(1))
        b = int(match_a.group(2))
        op = int(match_a.group(3))
        nb_instance = int(match_a.group(4))
        nb_requests = od+b+op
        return type_, nb_requests, od, b, op, nb_instance
    
    elif match_b:
        type_ = 'B'
        nb_requests = int(match_b.group(1))
        od = int(match_b.group(2))
        op = int(match_b.group(3))
        md = int(match_b.group(4))
        mp = int(match_b.group(5))
        nb_instance = int(match_b.group(6))
        return type_, nb_requests, od, op, md, mp, nb_instance
    
    elif match_c :
        type_ = 'C'
        nb_stops = int(match_c.group(1))
        # print(f'nb_stops : {nb_stops}')
        nb_requests = int(match_c.group(2))
        od = int(match_c.group(3))
        op = int(match_c.group(4))
        md = int(match_c.group(5))
        mp = int(match_c.group(6))
        nb_instance = int(match_c.group(7))
        return type_, nb_requests, od, op, md, mp, nb_instance, nb_stops
    elif match_d :
        type_ = 'D'
        nb_stops = int(match_d.group(1))
        # print(f'nb_stops : {nb_stops}')
        nb_requests = int(match_d.group(2))
        od = int(match_d.group(3))
        op = int(match_d.group(4))
        md = int(match_d.group(5))
        mp = int(match_d.group(6))
        nb_instance = int(match_d.group(7))
        return type_, nb_requests, od, op, md, mp, nb_instance, nb_stops
    else:
        print("Invalid format, read_data.py", filename)


import os
import csv

def export_folder_names_to_csv(folder_path, output_csv_path):
    # Liste les sous-dossiers uniquement
    folder_names = [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))]

    # Écrit les noms dans un CSV
    with open(output_csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow(["folder_name"])  # En-tête
        for folder_name in folder_names:
            writer.writerow([folder_name])
    
    print(f"{len(folder_names)} folder names exported to {output_csv_path}")



def export_json_filenames_to_csv(folder_path, output_csv_path):
    # Liste tous les fichiers qui se terminent par .json
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    # Écrit les noms de fichiers dans un CSV
    with open(output_csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow(["filename"])  # En-tête
        for filename in json_files:
            name = f"Scenarios/Scenarios_D/{filename}"
            writer.writerow([name])

    print(f"{len(json_files)} JSON filenames exported to {output_csv_path}")

import csv

def remove_matching_lines(file1_path, file2_path, output_path):
    prefix = "multimodal_carpooling/Scenarios/Scenarios_B\\"
    # Lecture du fichier 2 : lignes à retirer
    with open(file2_path, 'r') as f2:
        lines_to_remove = set(line.strip() for line in f2 if line.strip())

    # Lecture du fichier 1 et filtrage
    filtered_lines = []
    with open(file1_path, 'r') as f1:
        for line in f1:
            line_clean = line.strip()
            # Nettoyage : on retire "B_" et ".json"
            line_base = line_clean.replace("B_", "").replace(".json", "")
            if line_base not in lines_to_remove:
                filtered_lines.append(line_clean)

    # Écriture du fichier résultat
    with open(output_path, 'w', newline='') as out:
        writer = csv.writer(out)
        for row in filtered_lines:
            full_path = prefix + row
            writer.writerow([full_path])

    print(f"{len(filtered_lines)} lignes conservées dans {output_path}")

import pandas as pd
def add_prefix(file_path : str):
    # input_path = "nom_de_ton_fichier.csv"  # <-- Remplace par le bon nom de fichier
    df = pd.read_csv(file_path, header=None)  # Pas d'en-tête

    # === 2. Ajouter le préfixe à chaque ligne ===
    prefix = "Scenarios/Scenarios_C\\"
    df[0] = prefix + df[0]

    # === 3. Sauvegarder le résultat dans un nouveau fichier CSV ===
    # output_path = "fichier_modifie.csv"
    df.to_csv(file_path, index=False, header=False)

# add_prefix("Scenarios\list_to_do.csv")
# make list of scenarios B 
# export_folder_names_to_csv("multimodal_carpooling\Results\B", "multimodal_carpooling/Scenarios/liste_scenarios_solved_B.csv")
# export_folder_names_to_csv("Scenarios/Scenarios_D", "Scenarios/liste_scenarios_D.csv")

# makes list of what is already done, scenarios B 
# export_json_filenames_to_csv("Scenarios\Scenarios_D", "Scenarios/liste_scenarios_D.csv")

# update csv : scenarios left to do 
# remove_matching_lines("multimodal_carpooling/Scenarios/liste_scenarios_B.csv", "multimodal_carpooling/Scenarios/liste_scenarios_solved_B.csv", "multimodal_carpooling/Scenarios/list_to_do.csv")

# creates_instance("Scenarios/Scenarios_C/C_4_od1_op1_md1_mp1_1.json")