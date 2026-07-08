from requirements import * 
from class_solution import Solution
from read_data import creates_instance
from useful_functions import ordre_grandeur
from utils_paths import check_if_solutions_exist_for_list_methods,from_scenario_path_to_result_path
from utils_calculs import  compute_distance_from_stop_list
from collections import Counter
def from_json_to_Solution(file_path: str):
    """ Opens a solution.json file and creates a object of class Solution from it"""
    with open(file_path) as f:
        data = json.load(f)

        status = data["status"]
        # scenario = data["name_scenario"]
        
        def scenario_path(path_source):
            # Normaliser les séparateurs
            path_source = path_source.replace('\\', '/')
            
            # Découper le chemin
            parties = path_source.split('/')
            lettre = parties[1]  # Exemple : "C"
            folder_scenario = parties[2]  # Exemple : "12_3_od0_op0_md0_mp3_4"
            
            # Construire le nom du fichier : "C_12_3_od0_op0_md0_mp3_4.json"
            file_name = f"{lettre}_{folder_scenario}.json"
            
            # Construire le chemin final
            final_path = os.path.join("Scenarios", f"Scenarios_{lettre}", file_name)
            return final_path
        
        # print(f'result file : {file_path}')
        # print(f'debug ultils_results : scenario_path(file_path) : {scenario_path(file_path)} ')
        # print(f'scenario_path(file_path): {creer_chemin_scenario(file_path)}')
        scenario = creates_instance(scenario_path(file_path))
        obj_value = data["objective_value"]
        nb_requests_satisfied = data["nb_requests_satisfied"]

        # name_file = os.path.basename(file_path)
        method_used = data["method"]
        # method_used = name_file.split("_")[0]
        if "CPLEX" in file_path:
            solver = "CPLEX"
        else:
            solver = "CBC"
        itineraries = data["itineraries"]
        x_values = data["x"]
        y_values = data["y"]
        F_values = data["F"]
        theta_a_values = data["theta_a"]
        theta_d_values = data["theta_d"]
        Q_values = data["Q"]
        S_values = data["S"]
        nb_final_drivers = data["nb_final_drivers"]
        # print(f" method used : {method_used}")
        method_code = method_used.split("_")[0]
        if method_code in ("M1", "M2", "M3", "M4", "M5", "M6"):
            multiplicator_bonus = 0.1

        elif method_code in ("M7", "M8"):
            multiplicator_bonus = 0.001

        elif method_code in ("M10", "M11", "M12"):
            if scenario.total_potential_emissions != 0:
                multiplicator_bonus = ordre_grandeur(
                    1 / scenario.total_potential_emissions
                )
            else:
                multiplicator_bonus = 0.001

        else:
            print("ERROR from_json_to_solution, the method is not recognized")
    return Solution(status,scenario,obj_value,nb_requests_satisfied,method_used, x_values, y_values, F_values, theta_a_values, theta_d_values, Q_values,S_values,solver, itineraries,nb_final_drivers,multiplicator_bonus)


def routes_are_equal(routes_1 : list, routes_2 : list):
    """
    Checks if two itineraries are identical.
    Parameters : 
    -------------
    routes_1 : list 
        example : [[1, 3, 2]]
    routes_2 : same 

    Returns : 
    ----------
    bool : True or False
    """
    r1 = Counter(tuple(route) for route in routes_1)
    r2 = Counter(tuple(route) for route in routes_2)
    return r1 == r2
# from pathlib import Path
def compute_total_emissions(solution : Solution):
    """ Computes the total emissions of a solution 
    Parameters : 
    --------------
    solution : Solution 
    
    Returns : 
    ------------
    total_emissions : float 
    """

    # total_emissions =sum(solution.scenario.all_requests[u].emission_rate_vehicle * (sum( sum(solution.y[s+1][ss][u] * float(solution.scenario.dist_matrix_km[s][ss]) for s in range(solution.scenario.nb_stops)) for ss in range(solution.scenario.nb_stops)) )for u in range(len(solution.scenario.all_requests))) 
    total_emissions = 0
    index_driver =0 
    for u in range(len(solution.scenario.all_requests)):
        if solution.x[u][u] >= 0.9 :
            itinerary_user = solution.itineraries[index_driver]
            itinerary_user.pop()
            itinerary_user.remove(0)
            emission_user = compute_distance_from_stop_list(itinerary_user,"dist_matrix_km_size15.npy") * solution.scenario.all_requests[index_driver].emission_rate_vehicle
            total_emissions+= emission_user
            index_driver+=1

    return total_emissions

def compute_detours_solution(csv_path : str,selected_methods : list,data_type : str):
    """
    Compute the detours made for a solution and prints results in csvfiles. 

    Example to run : compute_detours_solution("Scenarios\list_to_do.csv",["M7_CPLEX","M10_CPLEX"],'D')

    Parameters : 
    ------------
    csv_file : str 
        eg. "Scenarios\list_to_do.csv"
    selected_methods : list 
        eg. ["M7_CPLEX","M10_CPLEX"]
    data_type : str 
        eg. 'D'
    
    Returns : 
    -----------
    None
    """
    
    ## from ["M7_CPLEX","M10_CPLEX"] to ["M7","M10"] :
    list_methods = [m.split("_")[0] for m in selected_methods]

    ## create the label to name the files 
    method_label = "_vs_".join(selected_methods) if list_methods else "all_methods"
    
    ## total_detour_df : will hold the values of the detours for each scenario and will be saved in a csv file
    total_detour_df =  pd.DataFrame(columns=['scenario', 'initial_distance','initial_distance_tra','initial_emissions'])
    if len(selected_methods) == 2 : 
        total_detour_df[f"improv_emissions_{selected_methods[0]}_{selected_methods[1]}"] = pd.NA
        total_detour_df[f"improv_distance_{selected_methods[0]}_{selected_methods[1]}"] = pd.NA

        # total_detour_df[f"'initial_distance_tra'"]
        total_detour_df[f"improv_emissions_init_{selected_methods[0]}"] = pd.NA
        total_detour_df[f"improv_emissions_init_{selected_methods[1]}"] = pd.NA


    ## total_detour_dic : dictionnary that will be used to save data in total_detour_df
    total_detour_dic = {}
    
    ## creates the columns of total_detour_df
    for method in selected_methods:
        total_detour_df[f"final_distance_{method}"] = pd.NA
        total_detour_df[f"detour_km_{method}"] = pd.NA
        total_detour_df[f"detour_ratio_{method}"] = pd.NA
        total_detour_df[f"final_emissions_{method}"] = pd.NA
        

    ## initialize value 
    # total_initial_distance = 0 
    # total_initial_distance_everyone_travels = 0
    
    ## creates path to save total_detour_df
    output_path_global = f"Results\plots_{data_type}\{method_label}/detour_study_{method_label}.csv"
    os.makedirs( f"Results\plots_{data_type}\{method_label}", exist_ok=True)

    ## We open the path with al the scenarios to investigate
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            total_initial_distance_everyone_travels = 0
            # for user in range(nb_users):
            #     total_initial_distance_everyone_travels+= compute_distance_from_stop_list(list(map(int, data["stops"].keys())),"dist_matrix_km_size15.npy")
            # stops = list(map(int, data["stops"].keys()))

            ## scenario_detour_dic : dictionnary that will be used to save data in scenario_detour_df
            scenario_detour_dic = {}
            
            ## Get the path of the scenario, for example Scenarios/Scenarios_D/D_3_2_od1_op0_md1_mp0_3.json
            scenario_path = row[0]
            # print(f'debug utils_results : row {row}, scenario path : {scenario_path}')
            ## get the number of users in the scenario 
            nb_users = int(scenario_path.split(f"{data_type}_")[1].split("_")[1])

            ## from the name of the scenario, get the path to the result files
            result_path = from_scenario_path_to_result_path(scenario_path,data_type)
            # print(f'debug utils_results : result_path : {result_path}')

            ## scenario_detour_df : will hold the values of the detours for each user in one scenario and will be saved in a csv file
            ## one line for each user/request
            scenario_detour_df =  pd.DataFrame(columns=['user', 'initial_distance'])

            ## creates the columns of scenario_detour_df
            for method in selected_methods:
                # print(f"method 3 : {method}")
                scenario_detour_df[f"final_distance_{method}"] = pd.NA
                scenario_detour_df[f"detour_km_{method}"] = pd.NA
                scenario_detour_df[f"detour_ratio_{method}"] = pd.NA
            # print(f'debug utils_results : result_path : {result_path}')
            ## if the result file exists :
            if os.path.isdir(result_path):
                
                ## get the paths to the solutions for each method for which a solution file was found
                all_files_exist, found_files = check_if_solutions_exist_for_list_methods(result_path,list_methods)
                
                ## for each user, check the associated itinerary for each method.
                for user in range(nb_users) :

                    ## we check the result for each solution file found
                    
                    for file_path in found_files : 
                        # print(f"debug utils_results : user : {user}, file_path : {file_path}")
                        ## get the code of the method 
                        met = os.path.basename(file_path).split("_")[0]
                        method = f"{met}_CPLEX"
                        # print(f"method: {method}")
                        ## get the name of the scenario
                        instance = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
                        # print(f"instance : {instance}")
                        ## Creates the Solution object 
                        solution = from_json_to_Solution(file_path)
                        
                        ## Creates a dictionnary with the users that are drivers and the associated itinerary
                        drivers = [u for u in range(nb_users) if solution.x[u][u] >= 0.9]
                        driver_itinerary = {
                            driver: itinerary
                            for driver, itinerary in zip(drivers, solution.itineraries)
                        }

                        ## Get the initial distance of the user (in theory, if they drive without detour)
                        initial_distance = solution.scenario.all_requests[user].initial_distance
                        # total_initial_distance_everyone_travels+= initial_distance
                        # print(f"debug utils_results : totalinitial distance tra : {total_initial_distance_everyone_travels}")
                        # total_initial_distance_everyone_travels+=initial_distance
                        ## if the user is a driver, we take them into account to compute the detour
                        if solution.x[user][user] >= 0.9 :
                            # total_initial_distance += initial_distance 
                            final_distance = compute_distance_from_stop_list(driver_itinerary[user],"dist_matrix_km_size15.npy")
                            # print(f'debug utils_results : final distance : {final_distance}')

                            # for passenger in range(nb_users):
                            #     if solution.x[user][passenger] >= 0.9 :
                            #         print(f"debug utils_results : user : {user}, passenger : {passenger}")
                            #         total_initial_distance_everyone_travels+= initial_distance
                            #         print(f"debug utils_results : totalinitial distance tra : {total_initial_distance_everyone_travels}")
                        
                        else : final_distance = None

                        if final_distance :
                            detour_km = final_distance - initial_distance
                            detour_ratio = (final_distance - initial_distance)/initial_distance
                        else : 
                            detour_km = None
                            detour_ratio = None
                        

                        scenario_detour_dic[f"final_distance_{method}"] = final_distance
                        scenario_detour_dic[f"detour_km_{method}"] = detour_km
                        scenario_detour_dic[f"detour_ratio_{method}"] = detour_ratio

                        if data_type !='C' :
                            total_detour_dic[f"final_emissions_{method}"] = compute_total_emissions(solution)
                            # print(f'compute_total_emissions(solution) : {compute_total_emissions(solution)}')
                            # key = f"final_emissions_{method}"
                            # print(f"total_detour_dic[{key}] = {total_detour_dic[key]}")
                            # print(f"total_detour_dic[f final_emissions_method] {total_detour_dic[f"final_emissions_{method}"]}")
                            total_detour_dic['initial_emissions'] = solution.scenario.total_potential_emissions
                        # print(f"solution.scenario.total_potential_emissions : {solution.scenario.total_potential_emissions}")
                    ## add a row in the scenario file for the detour of the user we just studied
                    new_row = pd.DataFrame(
                            [[user+1, initial_distance, *scenario_detour_dic.values()]],
                            columns=["user", "initial_distance",*scenario_detour_dic.keys()]
                        )
                    scenario_detour_df = pd.concat([scenario_detour_df, new_row], ignore_index=True)
                                        
                    
                ## creates path to save scenario_detour_df and saves it
                output_path_local = f"Results\{data_type}\{instance}\detour_solutions_{method_label}.csv"
                scenario_detour_df.to_csv(output_path_local, index=False)
                

                total_detour_dic[f"initial_distance"] = scenario_detour_df["initial_distance"].sum()
                total_detour_dic[f"initial_distance_tra"]= solution.scenario.initial_distance_passenger_also
                # total_detour_dic[f"initial_distance_everyone_travels"] = total_initial_distance_everyone_travels
                # print(f"debug utils_results: scenario_detour_df[ffinal_distance] : ")
                # print(scenario_detour_df[f"final_distance_{method}"])
                # print("sum : ")
                # print(scenario_detour_df[f"final_distance_{method}"].sum())
                # print(f"in the for loop : method1 : {method} ")
                for method in selected_methods : 
                    total_detour_dic[f"final_distance_{method}"] = scenario_detour_df[f"final_distance_{method}"].sum()
                    # total_detour_dic[f"detour_km_{method}"] = total_detour_dic[f"final_distance_{method}"] - total_detour_dic[f"initial_distance"]
                    # total_detour_dic[f"detour_ratio_{method}"] = (total_detour_dic[f"final_distance_{method}"] - total_detour_dic[f"initial_distance"])/total_detour_dic[f"initial_distance"]
                    total_detour_dic[f"detour_km_{method}"] = total_detour_dic[f"final_distance_{method}"] - total_detour_dic[f"initial_distance_tra"]
                    total_detour_dic[f"detour_ratio_{method}"] = (total_detour_dic[f"final_distance_{method}"] - total_detour_dic[f"initial_distance_tra"])/total_detour_dic[f"initial_distance_tra"]
                    
                    # # print(f"in the for loop : method 2: {method} ")
                    # print(total_detour_dic[f"final_distance_{method}"] )


                if (len(selected_methods) == 2) and (data_type != 'C') : 
                    # print(f'total_detour_dic[ffinal_emissions_selected_methods[0]: {total_detour_dic[f"final_emissions_{selected_methods[0]}"]}')
                    # print(total_detour_dic['initial_emissions'])
                    if total_detour_dic[f"final_emissions_{selected_methods[0]}"] == 0 :
                        total_detour_dic[f"improv_emissions_{selected_methods[0]}_{selected_methods[1]}"] = 100
                    else : 
                        total_detour_dic[f"improv_emissions_{selected_methods[0]}_{selected_methods[1]}"] = (total_detour_dic[f"final_emissions_{selected_methods[0]}"] - total_detour_dic[f"final_emissions_{selected_methods[1]}"])*100/total_detour_dic[f"final_emissions_{selected_methods[0]}"]
                    
                    if total_detour_dic[f"initial_emissions"] == 0 : 
                        total_detour_dic[f"improv_emissions_init_{selected_methods[0]}"] = 100
                        total_detour_dic[f"improv_emissions_init_{selected_methods[1]}"] = 100
                    else : 
                        total_detour_dic[f"improv_emissions_init_{selected_methods[0]}"] = ( total_detour_dic[f"final_emissions_{selected_methods[0]}"]-total_detour_dic[f"initial_emissions"])*100/total_detour_dic[f"initial_emissions"]
                        total_detour_dic[f"improv_emissions_init_{selected_methods[1]}"] = (total_detour_dic[f"final_emissions_{selected_methods[1]}"]-total_detour_dic[f"initial_emissions"] )*100/total_detour_dic[f"initial_emissions"]
                        
                    total_detour_dic[f"improv_distance_{selected_methods[0]}_{selected_methods[1]}"] = (total_detour_dic[f"final_distance_{selected_methods[0]}"] - total_detour_dic[f"final_distance_{selected_methods[1]}"])*100/total_detour_dic[f"final_distance_{selected_methods[0]}"]

                
            
            ## add a row in the file for the detour of the scenario we just studied

                new_row = pd.DataFrame(
                        [[instance,*total_detour_dic.values()]],
                        columns=['scenario', *total_detour_dic.keys()]
                    )
                total_detour_df = pd.concat([total_detour_df, new_row], ignore_index=True)

    total_detour_df.to_csv(output_path_global, index=False)
    return 

def compute_final_emissions_solution(solution : Solution):
    """This function computes the final CO2 emissions for one solution regardless of the method used 
    to solve the scenario. 
    
    Parameters : 
    --------------
    solution : Solution 

    Returns : 
    --------------
    final_emissions : float 
    """

    final_emissions = 0 
    
    for itineraries in solution.itineraries :
        compute_distance_from_stop_list(itineraries,"dist_matrix_km_size15.npy")

    return final_emissions

def study_detours(csv_file : str):
    """Studies the detours statistics for the scenarios 
        - improvment of emissions 
        - ratio of detours 
    for the solution init, M7 and M10 
    
    Returns : 
    None """

    
    df = pd.read_csv("Results\plots_D\M7_CPLEX_vs_M10_CPLEX\detour_study_M7_CPLEX_vs_M10_CPLEX.csv")
    pd.to_numeric(
        df["improv_emissions_M7_CPLEX_M10_CPLEX"],
        errors="coerce"
    )
    mean_improvment_emission_M7_M10 = df["improv_emissions_M7_CPLEX_M10_CPLEX"].mean()
    print(f"mean improvment M7 to M10: {mean_improvment_emission_M7_M10}")
    mean_improvment_emission_init_to_M7 = df["improv_emissions_init_M7_CPLEX"].mean()
    mean_improvment_emission_init_to_M10 = df["improv_emissions_init_M10_CPLEX"].mean()
    print(f"mean improvment init to M7: {mean_improvment_emission_init_to_M7}")
    print(f"mean improvment init to M10: {mean_improvment_emission_init_to_M10}")
    max_imp_init_M7 = df["improv_emissions_init_M7_CPLEX"].max()
    print(f"Max improvment init-> M7 :{max_imp_init_M7}")
    # print((df["improv_emissions_M7_CPLEX_M10_CPLEX"] > 0).mean())

    # mean_detour_M7_M10 = df["improv_emissions_M7_CPLEX_M10_CPLEX"].mean()
    # print(f"mean improvment M7 to M10: {mean_detour_M7_M10}")
    mean_detour_init_to_M7 = df["detour_ratio_M7_CPLEX"].mean()
    mean_detour_init_to_M10 = df["detour_ratio_M10_CPLEX"].mean()
    print(f"mean improvment ratio init to M7: {mean_detour_init_to_M7}")
    print(f"mean improvment ratio init to M10: {mean_detour_init_to_M10}")
    print((df["improv_emissions_M7_CPLEX_M10_CPLEX"] > 0).mean())
    return 

# study_detours("ic")
# compute_detours_solution("Scenarios\liste_scenarios_D.csv",["M7_CPLEX","M10_CPLEX"],'D')
# compute_detours_solution("Scenarios\list_to_do.csv",["M3_CPLEX_tra","M5_CPLEX_tra"],'C')

# df = pd.read_csv("Results\plots_D\M7_CPLEX_vs_M10_CPLEX\detour_study_M7_CPLEX_vs_M10_CPLEX.csv")
# print(f'mean initial distance : {df["initial_distance"].mean()}')
# print(f'mean final_distance_M7_CPLEX : {df["final_distance_M7_CPLEX"].mean()}')
# print(f'mean final_distance_M10_CPLEX : {df["final_distance_M10_CPLEX"].mean()}')
# print(f'detour km mean M7 : {df["detour_km_M7_CPLEX"].mean()}')
# print(f'detour km mean M10 : {df["detour_km_M10_CPLEX"].mean()}')
# print(f'detour ratio meanM7 : {df["detour_ratio_M7_CPLEX"].mean()}')
# print(f'detour ratio mean M10 : {df["detour_ratio_M10_CPLEX"].mean()}')
# print(f'mean improvement CO2 worst VS M7 : {df["improv_emissions_init_M7_CPLEX"].mean()}')
# print(f'mean improvement CO2 worst VS M10 : {df["improv_emissions_init_M10_CPLEX"].mean()}')
# print(f'mean improvement CO2 M7 VS M10 : {df["improv_emissions_M7_CPLEX_M10_CPLEX"].mean()}')
# print(f'mean  CO2 worst : {df["initial_emissions"].mean()}')
# print(f'mean  CO2  M10 : {df["final_emissions_M10_CPLEX"].mean()}')
# print(f'mean CO2 M7 : {df["final_emissions_M7_CPLEX"].mean()}')
# print(f'mean improvement distance worst VS M7 : {df["detour_ratio_M7_CPLEX"].mean()}')
# print(f'mean improvement distance worst VS M10 : {df["detour_ratio_M10_CPLEX"].mean()}')
# print(f'mean improvement distance M7 VS M10 : {df["improv_distance_M7_CPLEX_M10_CPLEX"].mean()}')
# # -----------------------------------------------------------------------
# print(f'------------------------------------------------------------------')
# df = pd.read_csv("Results\plots_C\M7_CPLEX_tra_vs_M12_CPLEX_tra\detour_study_M7_CPLEX_tra_vs_M12_CPLEX_tra.csv")
# print(f'mean initial distance : {df["initial_distance"].mean()}')
# print(f'mean initial distance also passengers :  : {df["initial_distance_tra"].mean()}')
# print(f'mean final_distance_M7_CPLEX_tra : {df["final_distance_M7_CPLEX_tra"].mean()}')
# print(f'mean final_distance_M12_CPLEX_tra : {df["final_distance_M12_CPLEX_tra"].mean()}')
# print(f'detour km mean M7_tra : {df["detour_km_M7_CPLEX_tra"].mean()}')
# print(f'detour km mean M12_tra : {df["detour_km_M12_CPLEX_tra"].mean()}')
# print(f'detour ratio meanM7_tra : {df["detour_ratio_M7_CPLEX_tra"].mean()}')
# print(f'detour ratio mean M12_tra : {df["detour_ratio_M12_CPLEX_tra"].mean()}')
# df = pd.read_csv("Results\plots_C\M3_CPLEX_vs_M5_CPLEX\detour_study_M3_CPLEX_vs_M5_CPLEX.csv")
# print(f'mean initial distance : {df["initial_distance"].mean()}')
# print(f'mean final_distance_M3_CPLEX : {df["final_distance_M3_CPLEX"].mean()}')
# print(f'mean final_distance_M5_CPLEX : {df["final_distance_M5_CPLEX"].mean()}')
# print(f'detour km mean M3 : {df["detour_km_M3_CPLEX"].mean()}')
# print(f'detour km mean M5 : {df["detour_km_M5_CPLEX"].mean()}')
# print(f'detour ratio meanM3 : {df["detour_ratio_M3_CPLEX"].mean()}')
# print(f'detour ratio mean M5 : {df["detour_ratio_M5_CPLEX"].mean()}')
# # -----------------------------------------------------------------------
# print(f'------------------------------------------------------------------')
# df = pd.read_csv("Results\plots_C\M3_CPLEX_tra_vs_M5_CPLEX_tra\detour_study_M3_CPLEX_tra_vs_M5_CPLEX_tra.csv")
# print(f'mean initial distance : {df["initial_distance"].mean()}')
# print(f'mean initial distance also passengers :  : {df["initial_distance_tra"].mean()}')
# print(f'mean final_distance_M3_CPLEX_tra : {df["final_distance_M3_CPLEX_tra"].mean()}')
# print(f'mean final_distance_M5_CPLEX_tra : {df["final_distance_M5_CPLEX_tra"].mean()}')
# print(f'detour km mean M3_tra : {df["detour_km_M3_CPLEX_tra"].mean()}')
# print(f'detour km mean M5_tra : {df["detour_km_M5_CPLEX_tra"].mean()}')
# print(f'detour ratio meanM3_tra : {df["detour_ratio_M3_CPLEX_tra"].mean()}')
# print(f'detour ratio mean M5_tra : {df["detour_ratio_M5_CPLEX_tra"].mean()}')
# -----------------------------------------------------------------------
# import matplotlib.pyplot as plt

# plt.figure()
# plt.boxplot(
#     [df["improv_emissions_init_M7_CPLEX"], df["improv_emissions_init_M10_CPLEX"], df["improv_emissions_M7_CPLEX_M10_CPLEX"]],
#     labels=["from initial to M7", "from initial to M10", "from M7 to M10"],
#     showfliers=True
# )
# plt.ylabel("Improvement (%)")
# plt.title("Distribution of improvements over 770 instances")
# plt.show()

# def ecdf(data):
#     x = np.sort(data)
#     y = np.arange(1, len(x) + 1) / len(x)
#     return x, y

# plt.figure()

# for col, label in [
#     ("improv_emissions_init_M7_CPLEX", "from initial to M7"),
#     ("improv_emissions_init_M10_CPLEX", "from initial to M10"),
#     ("improv_emissions_M7_CPLEX_M10_CPLEX", "from M7 to M10"),
# ]:
#     x, y = ecdf(df[col])
#     plt.plot(x, y, label=label)

# plt.xlabel("Improvement (%)")
# plt.ylabel("Proportion of instances")
# plt.title("ECDF of improvements")
# plt.legend()
# plt.show()

# plt.figure()
# plt.scatter(df["initial_emissions"], df["final_emissions_M10_CPLEX"], alpha=0.5)
# plt.xlabel("Initial value (%)")
# plt.ylabel("Total improvement (M10 − initial) (%)")
# plt.title("Saturation analysis")
# plt.show()


# methods = ["initial_emissions", "final_emissions_M7_CPLEX", "final_emissions_M10_CPLEX"]

# median = df[methods].median()
# q25 = df[methods].quantile(0.25)
# q75 = df[methods].quantile(0.75)

# plt.figure()
# plt.plot(methods, median, marker="o", label="Median")
# plt.fill_between(methods, q25, q75, alpha=0.3, label="IQR")
# plt.ylabel("Value (%)")
# plt.title("Typical progression per instance")
# plt.legend()
# plt.show()