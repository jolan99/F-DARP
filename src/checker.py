
import csv
import os
from class_solution import Solution

from utils_results import from_json_to_Solution


def check_roles(solution: Solution):
    """ Checks if the role are well attributed in the solution"""
    solution_valid = True
    for user in range(len(solution.scenario.all_requests)):
        req = solution.scenario.all_requests[user]
        if req.only_driver : 
            role = "od"
        elif req.only_passenger :
            role = "op"
        else : 
            role = "other"
        if (role == "op") and (solution.x[user][user] >= 0.9) :
            solution_valid = False 
            print(f'ERROR detected 1.1: user {user +1} is planned as a driver but their role is only passenger')
        if (role == "od") and (solution.x[user][user] <= 0.4) :
            solution_valid = False 
            print(f'ERROR detected 1.2: user {user +1} is not planned as a driver but their role is only driver')
    return solution_valid

def check_bonus(solution : Solution):
    """ Check if the satisfaction bonus is correctly attributed """
    solution_valid = True 
    list_errors = []
    # print(f'solution.multiplicator_bonus : {solution.multiplicator_bonus}')
    upper_boud = 1.8*solution.multiplicator_bonus
    # print(f"upper bound : {upper_boud}")
    lower_bound = 0.8*solution.multiplicator_bonus
    # print(f"lower bound : {lower_bound}")
    if solution.S :
        for user in range(len(solution.scenario.all_requests)):
            req = solution.scenario.all_requests[user]
            if req.only_driver : 
                role = "od"
            elif req.only_passenger :
                role = "op"
            elif req.mainly_driver : 
                role = "md"
            elif req.mainly_passenger: 
                role = "mp"
            satisfaction_bonus = solution.S[user]

            request_satisfied = sum(solution.x[u][user] for u in range (len(solution.scenario.all_requests)))
         
            
            if (request_satisfied <= 0.3) and (satisfaction_bonus >= lower_bound) :
                solution_valid = False 
                print(f'ERROR detected 2.1: the satisfaction value is {satisfaction_bonus} but the user {user +1} request is not satisfied.')
                list_errors.append('2.1')
            ## If the request is satisfied, Su > 0
            if (request_satisfied >= 0.3) and (satisfaction_bonus <= lower_bound) :
                solution_valid = False 
                list_errors.append('2.2')
                print(f'ERROR detected 2.2: the satisfaction value is {satisfaction_bonus} but the user {user+1} request is satisfied.')
            ## If user is "od", Su = 0.2
            if (role == "od") and (satisfaction_bonus <= upper_boud) and (solution.x[user][user] >= lower_bound) :
                solution_valid = False 
                list_errors.append('2.3')
                print(f'ERROR detected 2.3: the satisfaction value is {satisfaction_bonus} but the user {user+1} is {role} and should drive themselve.')
            if (role == "od") and (satisfaction_bonus >= upper_boud) and (solution.x[user][user] <= lower_bound) and (request_satisfied >= lower_bound):
                solution_valid = False 
                list_errors.append('2.4')
                print(f'ERROR detected 2.4: the satisfaction value is {satisfaction_bonus} but the user {user+1} is {role} and should drive themselve.')
            ## If user is "op", Su can not be 0.1 (passenger can not be allocated the wrong role)
            if (role == "op") and (lower_bound <= satisfaction_bonus <= upper_boud) :
                solution_valid = False 
                list_errors.append('2.5')
                print(f'ERROR detected 2.5: the satisfaction value is {satisfaction_bonus} but the user {user+1} is {role} and they can not have the "wrong" role')
            ## If user md drives, Su = 0.2 
            if (role == "md") and (satisfaction_bonus <= upper_boud) and (solution.x[user][user] >= lower_bound) :
                solution_valid = False 
                list_errors.append('2.6')
                print(f'ERROR detected 2.6: the satisfaction value is {satisfaction_bonus} but the user {user+1} is {role} and  is planned as a driver')
            if (role == "md") and (satisfaction_bonus >= upper_boud) and (solution.x[user][user] <= lower_bound) :
                solution_valid = False 
                list_errors.append('2.7')
                print(f'ERROR detected 2.7: the satisfaction value is {satisfaction_bonus} but the user {user+1} is {role} and  is not planned as a driver')
            ## If user mp is a passenger, Su = 0.2
            if (role == "mp") and (satisfaction_bonus <= upper_boud) and (solution.x[user][user] <= lower_bound) and (request_satisfied >= lower_bound):
                solution_valid = False 
                list_errors.append('2.8')
                print(f'ERROR detected 2.8: the satisfaction value is {satisfaction_bonus} but the user {user+1} is {role} and  is planned as a passenger')
            if (role == "mp") and (satisfaction_bonus >= upper_boud) and (solution.x[user][user] >= lower_bound) :
                solution_valid = False 
                list_errors.append('2.9')
                print(f'ERROR detected 2.9: the satisfaction value is {satisfaction_bonus} but the user {user+1} is {role} and is not planned as a passenger')
            ## If user md is passenger, Su = 0.1
            if (role == "md") and ( lower_bound <= satisfaction_bonus <= upper_boud) and (solution.x[user][user] >= lower_bound):
                solution_valid = False 
                list_errors.append('2.10')
                print(f'ERROR detected 2.10: the satisfaction value is {satisfaction_bonus} but the user {user+1} is {role} and  is planned as a driver')
            if (role == "md") and ((lower_bound >=satisfaction_bonus) or (satisfaction_bonus >= upper_boud)) and (solution.x[user][user] <= lower_bound) and (request_satisfied >= 0.8):
                solution_valid = False 
                list_errors.append('2.11')
                print(f'ERROR detected 2.11: the satisfaction value is {satisfaction_bonus} but the user {user+1} is {role} and  is not planned as a driver')
            ## If user mp is driver, Su = 0.1
            if (role == "mp") and ( lower_bound <= satisfaction_bonus <= upper_boud) and (solution.x[user][user] <= lower_bound)and (request_satisfied >= lower_bound):
                solution_valid = False 
                list_errors.append('2.12')
                print(f'ERROR detected 2.12: the satisfaction value is {satisfaction_bonus} but the user {user+1} is {role} and  is not planned as a driver')
            if (role == "mp") and ((lower_bound >=satisfaction_bonus) or (satisfaction_bonus >= upper_boud)) and (solution.x[user][user]>= lower_bound):
                solution_valid = False 
                list_errors.append('2.13')
                print(f'ERROR detected 2.13: the satisfaction value is {satisfaction_bonus} but the user {user+1} is {role} and is planned as a driver')
    return solution_valid, list_errors

def create_dic_for_one_itinerary(itinerary : list, user : int, solution : Solution):
    """ fonction that creates a dictionnary for each itinerary that says for each stop the arrival and departure time
    Parameters : solution : Solution 
    Return : dic """
    dic = {}
    for stop in itinerary :
       
        if (stop != 0 )and (stop != len(solution.scenario.dist_matrix_km)+1) :
          
            dic[stop] = [solution.theta_a[stop-1][user],solution.theta_d[stop-1][user]]
    return dic 
def create_detailed_itinerary_dic(solution : Solution):
    dic = {}
    itineraries_copy = solution.itineraries.copy()
    for driver in range(solution.scenario.nb_requests) :
        if solution.x[driver][driver] >= 0.9 : 
            list_passengers = []
            for passenger in range(solution.scenario.nb_requests) :
                if solution.x[driver][passenger] >= 0.9 :
                    list_passengers.append(passenger)
                   
            dic[driver] = [list_passengers, create_dic_for_one_itinerary(itineraries_copy[0] ,driver, solution )]
            del itineraries_copy[0]

    return dic 
def check_times_window(solution : Solution):
    """ Checks if the departure and arrival times are within the time windows off the travelers
    Parameters : 
    -------------
    solution : Solution 
    
    Returns : 
    -------------
    bool
    """
    
    solution_valid = True 
    list_errors = []
    solution.detailed_itineraries = create_detailed_itinerary_dic(solution)
    for user in range(solution.scenario.nb_requests):
       
        for driver in  range(solution.scenario.nb_requests):
            if solution.x[driver][user] >= 0.9 :
                dic_itinerary = solution.detailed_itineraries[driver][1]
                enum = 0
                for stop in solution.scenario.all_requests[user].stops :
                    arrival_window, departure_window = solution.scenario.all_requests[user].time_windows[str(stop)]
                    if stop not in dic_itinerary :
                        pass
                    else : 
                        arrival_time = dic_itinerary[stop][0]
                        departure_time = dic_itinerary[stop][1]
                        if enum == 0 : 
                            if not (arrival_window - 0.9 <= departure_time <= departure_window + 0.9) :
                                solution_valid = False
                                print(f'ERROR detected 3.1: The departure time for user {user+1} at stop {stop} is {departure_time} but the time window is {solution.scenario.all_requests[user].time_windows[str(stop)]}')
                                list_errors.append('3.1')
                        else : 
                            if not (arrival_window - 0.9 <= arrival_time <= departure_window + 0.9) :
                                solution_valid = False
                                print(f'ERROR detected 3.2: The arrival time for user {user+1} at stop {stop} is {arrival_time} but the time window is {solution.scenario.all_requests[user].time_windows[str(stop)]}')
                                list_errors.append('3.2')
                        enum += 1   
    return solution_valid, list_errors

def check_consistent_times(solution : Solution):
    """ Checks the consistency of the solution in relation to the time. 
    - Checks that the arrival time is earlier than the departure time 
    - Checks that the arrival time takes into account the distance between two stops"""
    solution_valid = True 
    list_errors = []
    solution.detailed_itineraries = create_detailed_itinerary_dic(solution)
    for driver, detailed_itinerary in solution.detailed_itineraries.items() :
        former_stop = None
        departure_former_stop = None 
        for stop, times in detailed_itinerary[1].items():
            arrival_time = times[0]
            departure_time = times[1]
            if arrival_time > departure_time + 0.1 : 
                print(f'ERROR detected 4.1 : Inconsistency in carpool driven by user {driver+1}. Arrival time at stop {stop} is {arrival_time}, which is later than departure time ({departure_time})')
                solution_valid = False
                list_errors.append('4.1')
            if former_stop != None :
                if arrival_time <solution.scenario.dist_matrix_time[former_stop-1][stop-1] + departure_former_stop - 0.01:
                    print(f'ERROR detected 4.2 : In carpool driven by {driver+1}. The travel distance between stop {former_stop} and {stop} is not respected. Travel distance : {solution.scenario.dist_matrix_time[former_stop-1][stop-1]}, but departure from {former_stop} at {departure_former_stop}, and arrival at {stop} at {arrival_time}, which is {departure_time - departure_former_stop} minutes.')
                    solution_valid = False
                    list_errors.append('4.2')
            former_stop = stop
            departure_former_stop = departure_time
            
    return solution_valid, list_errors

def check_itinerary(solution : Solution):
    solution_valid = True 
    list_errors = []
    solution.detailed_itineraries = create_detailed_itinerary_dic(solution)
    for user in range(solution.scenario.nb_requests):
        for driver in  range(solution.scenario.nb_requests):
            if solution.x[driver][user] >= 0.9 :
                dic_itinerary = solution.detailed_itineraries[driver][1]
                previous_stop = None
                for stop in solution.scenario.all_requests[user].stops :
                    if stop not in dic_itinerary :
                        print(f'ERROR detected 5.1: The user {user+1} is planned in carpool driven by {driver+1}, but the stop {stop} is not visited')
                        list_errors.append('5.1')
                        solution_valid = False 
                    if (stop in dic_itinerary) and (previous_stop in dic_itinerary) : 
                        if previous_stop : 
                            if dic_itinerary[stop][0] < dic_itinerary[previous_stop][1]: 
                                print(f'ERROR detected 5.2: In carpool driven by {driver +1}, the stops for passenger {user +1} are not in the correct order. The stop {stop} is visited before stop {previous_stop} ')
                                list_errors.append('5.2')
                                solution_valid = False 
                        
                    previous_stop = stop

    return solution_valid, list_errors



def checker(solution : Solution):
    solution_valid_1 = check_roles(solution)
    solution_valid_2_bool, solution_valid_2_errors = check_bonus(solution)
    solution_valid_3_bool, solution_valid_3_errors = check_times_window(solution)
    solution_valid_4_bool, solution_valid_4_errors = check_consistent_times(solution)
    solution_valid_5_bool, solution_valid_5_errors = check_itinerary(solution)
    conditions = [solution_valid_1,solution_valid_2_bool, solution_valid_3_bool, solution_valid_4_bool,solution_valid_5_bool]
    solution_valid = all(conditions)
    list_errors = solution_valid_2_errors + solution_valid_3_errors +solution_valid_4_errors + solution_valid_5_errors
    if solution_valid : 
        print(f'New checker : The solution is valid')
    else :
        print(f'New checker : The solution is not valid')

    return solution_valid, list_errors

def traiter_csv(csv_path, output_csv_path):
    resultats = []

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            if row['method'] == 'M8_CPLEX':
                instance = row['instance']
                lettre = row.get('type_instance', 'C')  # défaut à 'C' si absent
                path = os.path.join("Results", lettre, instance, "cplex", "M8_CPLEX_solution.json")
                
                if os.path.exists(path):
                    print(f"debug checker : path : {path}")
                    solution = from_json_to_Solution(path)
                    
                    val_bool, val_list = checker(solution)
                    resultats.append((instance, val_bool,val_list))
                else:
                    print(f" Fichier non trouvé : {path}")

    # Écriture du CSV de sortie avec 3 colonnes
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['instance', 'valeur_1.3', 'valeur_2.3','valeur_1.4', 'valeur_2.4'])
        writer.writerows(resultats)

from utils_paths import check_if_solutions_exist_for_list_methods 
def check_validity_solution_folder(folder_path : str, methods : list,output_csv_path : str):
    """
    This function will check if the solution saved for a list of methods is valid or not. 
    and saves the info in a csv file.
    Parameters : 
    -------------
    folder_path : str
    methods : list 
        ex : ["M10","M7"]
    output_csv_path : str
        Name of the csv file that will save the results
    Returns : 
    ------------
    None
    """

    resultats = []
    
    all_files_exist, found_files = check_if_solutions_exist_for_list_methods("Results/D/6_10_od5_op0_md4_mp1_3",methods)
    

    for file_path in found_files :
        method = os.path.basename(file_path).split("_")[0]
        scenario = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
        solution = from_json_to_Solution(file_path)
    
        val_bool, val_list = checker(solution)
        resultats.append((scenario,method, val_bool,val_list))
    
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['scenario', 'method', 'validity','errors'])
        writer.writerows(resultats)
    return
