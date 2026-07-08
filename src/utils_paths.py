from requirements import *

def from_scenario_path_to_result_path(scenario_path : str, data_type : str,verbose : int = 0):
    # from a path as "Scenarios/Scenarios_D/D_6_5_od2_op0_md1_mp2_4.json", gives the result path 
    # C:\Users\Anna\Documents\D1\multimodal_carpooling\Results\D\6_5_od2_op0_md1_mp2_4
    
    # Parameters : 
    # -------------
    # scenario_path : str 
    #     as "Scenarios/Scenarios_D/D_6_5_od2_op0_md1_mp2_4.json"
    # verbose : int = 0 
    #     If 0, does not print anything. If 1, prints details 

    # Returns : 
    # ------------
    # the result path : str
    # C:\Users\Anna\Documents\D1\multimodal_carpooling\Results\D\6_5_od2_op0_md1_mp2_4
    
    # base_results_dir = r"C:\Users\Anna\Documents\D1\multimodal_carpooling\Results\D"
    base_results_dir = f"Results\{data_type}"
    filename = os.path.basename(scenario_path)
    # print(f'debug data_analysis :  {filename}')
    # Supprimer l'extension .json
    scenario_name, ext = os.path.splitext(filename)
    scenario_name = scenario_name[2:]
    result_path = os.path.join(base_results_dir, scenario_name)
    if verbose == 1 : 
        print(f'The result path is : {result_path}')
    return result_path


def check_if_solutions_exist_for_list_methods(solution_folder : str, methods : list):
    """
    This functions checks if for a specific instance, a solution is given for all the required methods.

    Parameters : 
    ------------
    solution_folder : str 
    
    methods : list 
        example : ["M10","M12"]
    
    Returns : 
    -----------
    Exist : bool 
        True if a solution file exists for each method
    names_solution_files : list 
        Gives a list with the paths to the solutions files for each method. 
    
    """

    all_files_exist = True
    # print(f'debug utils_paths : {solution_folder}')
    cplex_dir = os.path.join(solution_folder, "cplex")
    # print(f'cplex dir : {cplex_dir}')
    if not os.path.isdir(cplex_dir):
        print(f"error utils_paths. folder cplex does not exist.")
        return False
    found_files = []
    # for method in methods:
    #     found_files[method] = None

    for filename in os.listdir(cplex_dir):
        if not filename.lower().endswith(".json"):
            continue

        for method in methods:
            if filename.startswith(method + "_"):
                found_files.append(os.path.join(cplex_dir, filename))
    
    if len(found_files) != len(methods):
        all_files_exist = False
    # if None in found_files :
    #     all_files_exist == False

    # print(f'all files exist : {all_files_exist}')
    # print(f"found files : {found_files}")
    return all_files_exist, found_files


# check_if_solutions_exist_for_list_methods("Results\D/5_5_od0_op1_md1_mp3_2",["M10","M12"])