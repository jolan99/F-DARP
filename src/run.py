
from requirements import *
from model_mNC_cplex import model_mNC_cplex
from model_MACE_cplex import model_MACE_cplex
from read_data import creates_instance
from class_solution import Solution
from checker import checker

def run_model(method: str, solver: str, scenario: str, time_limit : int = 600, verbose: int = 0):
    if verbose != 2 : print(f'------ Scenario {scenario.name} --- with method {method} ------')
    if verbose == 2 : print(f'\n \n------------------------- Method {method} : -------------------------  \n')
    
    if method == "mNC":
        if solver == "CPLEX":
            solution = model_mNC_cplex(scenario, verbose)
    
    elif method == "MACE":
        if solver == "CPLEX":
            solution = model_MACE_cplex(scenario,time_limit, verbose)
    
    else:
        print("The method is not recognized. Chose between 'MACE' and 'mNC' ")
        return
    return solution



def run_on_single_file(
    path_file: str, method: str, solver: str, save: bool = True, time_limit : int = 600,verbose: int = 1
) -> Solution:
    """
    Run the MILP model on one scenario.

    Parameters :
    --------------
    path_file : str
        The path to find the scenario
    method : str
        Which milp, which formulation is used EX : "M10"
    solver : str 
        Which solver is used EX :"CPLEX"
    save : bool 
        If you want the solution to be saved 
    time_limit : int 
        Time limit givento the solver
    verbose : int = 1
        If True, will print details about the run.

    Returns :
    -------------
    solution : Solution
    """

    scenario = creates_instance(path_file)

    if verbose == 2:
        scenario.print()
    start_time = time.time()

    solution = run_model(method, solver, scenario,time_limit, verbose)
    end_time = time.time() 
    execution_time = end_time - start_time

    print(f"Execution time: {execution_time:.6f} seconds")

    if solution:
        solution.time = execution_time

        if solution.status != "Infeasible":
            if verbose == 2 : solution.print_simple()
            # solution.check(scenario)

            if save:
                solution.save(scenario, verbose)
                
            else:
                if verbose == 2:
                    solution.extract_itineraries(verbose)
            checker(solution)

    return solution



if __name__ == "__main__":
    verbose = 1
    save = True
    time_limit = 60
    method = "MACE" 
    solver = "CPLEX"

    run_on_single_file('Scenarios\Scenarios_D\D_15_100_od30_op10_md40_mp20_1.json', 'mNC','CPLEX',save=True,time_limit =time_limit,verbose=1)
   
   # ici on fait un exemple de changement. 