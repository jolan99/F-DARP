from requirements import *
from class_scenario import Scenario
## defines the solution class
class Solution:
    def __init__(self,status,scenario,obj_value,nb_requests_satisfied,method_used, x_values, y_values, F_values, theta_a_values, theta_d_values, Q_values,S_values = None,solver = None, itineraries = None,nb_final_drivers = None,multiplicator_bonus : float = 0.1, time_limit : int = 600, verbose = 1) -> None:
        """
        Parameters : 
        -------------
        status : 
            gives the status of the solution : feasible, optimal... 
        x_values: 
            values for the variable x in the solution
        y_values : 
            values of the variable y in the solution 
        F_values :
            values of the variable F in the solution
        theta_a_values :
            values of the variable theta_a_values in the solution
        theta_d_values : 
            values of the variable theta_d_values in the solution
        Q_values : 
            values of the variable Q_values in the solution
        Delta_value : 
            values of the variable Delta_value in the solution
        Q_tot_values : 
            values of the variable Q_tot_values in the solution
        """
        self.scenario = scenario
        self.status = status
        self.obj_value = obj_value
        self.nb_requests_satisfied = nb_requests_satisfied
        self.method_used = method_used
        self.x = x_values
        self.y = y_values
        self.F = F_values
        self.theta_a = theta_a_values
        self.theta_d = theta_d_values 
        self.Q = Q_values 
        # self.Delta = Delta_value
        # self.Q_tot = Q_tot_values
        self.S = S_values
        self.time = None
        self.verbose = verbose
        if itineraries :
            self.itineraries = itineraries
        else : 
            self.itineraries = self.extract_itineraries()
        if solver :
            self.solver = solver
        else : 
            self.solver = 'CBC'
        def creates_path_solution(scenario):
            os.makedirs(f"Results/{scenario.type}/{scenario.name}/{self.solver}", exist_ok=True)
        creates_path_solution(scenario)
        self.path_solution = f"Results/{scenario.type}/{scenario.name}/{self.solver}"
        if self.verbose ==2 : print(f'the file path is : {self.path_solution}')
        self.ratio_roles_satisfied = self.set_ratio_roles_satisfied(scenario)
        self.detailed_itineraries = None 
        self.nb_final_drivers = nb_final_drivers
        self.multiplicator_bonus = multiplicator_bonus
        self.time_limit= time_limit
        self.real_emissions = compute_real_emissions(self)
        print(f'ESSAI : real emissions : {self.real_emissions}')
       


    def print_simple(self):
        """Prints details on the solution"""
        print(f'objective value : {self.obj_value}')
        print(f'ratio role satisfied : {self.ratio_roles_satisfied}')
        print(f'itineraries : {self.itineraries}')
        print(f'x : {self.x}')
        print(f'y : {self.y}')
        print(f'F : {self.F}')
        print(f'theta_a : {self.theta_a}')
        print(f'theta_d : {self.theta_d}')
        print(f'Q : {self.Q}')
        if self.S :
            print(f'S : {self.S}')
        


    # def check(self, scenario : Scenario)-> bool:
    #     """Solution checker
    #     Parameters : 
    #     -------------
    #     scenario : Scenario 
    #         details on the scenario 
        
    #     Returns : 
    #     -------------
    #     test_solution : bool 
    #         True if the solution is valid
    #     """
    #     if self.verbose != 0 : print(f'---------------------------------- CHECKER ------------------------------------')
    #     test_solution = True
    #     ## are requests given to several cars ? 
    #     for u in range(scenario.nb_requests):
    #         times_satisfied = 0
    #         for v in range(scenario.nb_requests) :
    #             if self.x[v][u] == 1 : 
    #                 times_satisfied += 1 
    #         if times_satisfied >= 2 :
    #             print(f'ERROR : The solution is not valid. The request of user {u} is treated more than once.')
    #             test_solution = False 
    #     ## if a user takes his car, then they can not go in someone else's car. 
    #     for u in range(scenario.nb_requests):
    #         if self.x[u][u] == 1 :
    #             for v in range(scenario.nb_requests) :
    #                 if v != u :
    #                     if self.x[v][u] == 1 : 
    #                         print(f'ERROR : A driver is also planned in someone else\'s car. ')
    #                         test_solution = False
    #     ## If a user u does not take they car, y[source][puit][u] must be 1. (and all the other y[s][ss][u] as well)
    #     for u in range(scenario.nb_requests):
    #         if self.x[u][u] == 0 :
    #             if self.y[0][scenario.nb_stops] == 0 : 
    #                 print(f'ERROR : The user does not drive but is not associated the empty itinerary')
    #                 test_solution = False
    #         ## + vérifier que tous les autres  y[s][ss][u] sont bien à 0. 

        

    #     if test_solution  :
    #         print(f'The solution is valid.')
    #     if self.verbose != 0 : print(f'-------------------------------- END CHECKER ------------------------------------')
    #     return test_solution 
    
    def save_solution(self)-> None:
        """
        Save the details of a solution in a json file 

        Parameters :
        -------------
        path_scenario: str 
            The path towards the scenario
        results_dir : str 
            The direction where to save the solution
        """
        
        # Build the path of the output file
        output_path = os.path.join(self.path_solution, f"{self.method_used}_solution_time_limit{self.time_limit}.json")
        
        # Convert the Solution object into a dictionary
        solution_scenario = {
            "method" : self.method_used,
            "solver" : self.solver,
            "status": self.status,
            "type_scenario" : self.scenario.type,
            "name_scenario" : self.scenario.name, 
            "number_instance" : self.scenario.nb_instance,
            "list_stops" : self.scenario.list_stops,
            "ratio_flexible" : self.scenario.ratio_flexible,
            "nb_probable_drivers" : self.scenario.nb_drivers,
            "nb_final_drivers" : len(self.itineraries),
            "objective_value": self.obj_value,
            "real_emissions" : self.real_emissions,
            "avoided_emissions" : self.scenario.total_potential_emissions - self.real_emissions, 
            "nb_requests_satisfied" : self.nb_requests_satisfied,
            "percentage_requests_satisfied" : (self.nb_requests_satisfied * 100)/len(self.scenario.all_requests),
            "ratio_roles_satisfied" : self.ratio_roles_satisfied,
            "time": self.time,
            "time_limit" : self.time_limit,
            "itineraries" : self.itineraries,
            "x": self.x,
            "y": self.y,
            "F": self.F,
            "theta_a": self.theta_a,
            "theta_d": self.theta_d,
            "Q": self.Q,
            "S": self.S
        }
        
        # Save in JSON
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(convert_numpy(solution_scenario), json_file, indent=4)
        
        if self.verbose != 0 : print(f"Solution sauvegardée dans {self.path_solution}")

    def save_in_big_csv(self, file_path: str, filename : str ="all_results.csv")-> None:
        """ Reads a json solution file, and print in a csv file the main informations about the solution.

        Parameters : 
        -------------
        file_path : str
            The path where the solution will be saved as a json file 
        filename : str 
            The name of the csv file where you want to save the informations
        """
        
        # # Vérifier si le fichier existe
        file_exists = os.path.isfile(filename)
        
        # Charger les données existantes
        rows = []
        if file_exists:
            with open(filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
        
        # Vérifier si l'instance existe déjà et la mettre à jour
        updated = False
        for row in rows:
            if row["instance"] == self.scenario.name and row["method"] == self.method_used:
                row["time"] = self.time
                row["status"] = self.status
                updated = True
                break
        
        # Ajouter une nouvelle ligne si l'instance n'existe pas
        if self.scenario.type =="A" : 
            if not updated:
                rows.append({"od": self.scenario.od, "b": self.scenario.b, "op": self.scenario.op, "ratio_flexible":self.scenario.ratio_flexible,"nb_probable_drivers" : self.scenario.nb_drivers,"nb_stops" : self.scenario.nb_stops,"type_instance": self.scenario.type, "instance": self.scenario.name,"method": self.method_used , "solver" : self.solver,"time": self.time, "status": self.status,"obj_value" : self.obj_value,"ratio_requests_satisfied" :((self.nb_requests_satisfied * 100)/len(self.scenario.all_requests)),"nb_final_drivers": len(self.itineraries)})
        elif (self.scenario.type == "B" ) or (self.scenario.type == "C" ) or (self.scenario.type == "D" ):
                rows.append({"od": self.scenario.od, "md": self.scenario.md, "mp": self.scenario.mp, "op": self.scenario.op, "ratio_flexible":self.scenario.ratio_flexible,"nb_probable_drivers" : self.scenario.nb_drivers,"nb_stops" : self.scenario.nb_stops,"type_instance": self.scenario.type, "instance": self.scenario.name,"method": self.method_used ,"solver" : self.solver, "time": self.time, "status": self.status,"obj_value" : self.obj_value,"ratio_requests_satisfied" :((self.nb_requests_satisfied * 100)/len(self.scenario.all_requests)),"ratio_roles_satisfied":self.ratio_roles_satisfied,"nb_final_drivers": len(self.itineraries)})
                
        # Écrire les données dans le fichier
        with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
            if self.scenario.type =="A" :
                fieldnames = ["od", "b", "op", "ratio_flexible","nb_probable_drivers","nb_stops", "type_instance","instance","method","solver", "time", "status","obj_value","ratio_requests_satisfied","nb_final_drivers"]

            elif (self.scenario.type == "B" ) or (self.scenario.type == "C" )or (self.scenario.type == "D" ):
                fieldnames = ["od", "md","mp", "op", "ratio_flexible","nb_probable_drivers","nb_stops","type_instance", "instance","method","solver", "time", "status","obj_value","ratio_requests_satisfied","ratio_roles_satisfied","nb_final_drivers"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
        
        if self.verbose != 0 : print(f"Données enregistrées pour {self.scenario.name} dans {filename}")
    
    
    def extract_itineraries(self, verbose : int =  1)-> list:
        """ 
        Extract itineraries from a solution. From a y variable, writes the itinerary for the user u 
        
        Parameters : 
        --------------
        verbose : int INUTILE à ENLEVER
            from 0 to 2, gives different level of informations

        Returns : 
        -------------
        list_itineraries : list[list[int]]
            The itinerary for the driver u 
        """
        list_itineraries = []
        for u in range(self.scenario.nb_requests):
            itinerary = [0]
            for s in range(len(self.scenario.dist_matrix_km)+1):
                if self.y[0][s][u] >= 0.9999 : 
                    itinerary.append(s+1)
                    next_stop = s+1
                    break
            safety_stop = 0
            while next_stop != (len(self.scenario.dist_matrix_km)+1):
                safety_stop+=1 
                for ss in range(len(self.scenario.dist_matrix_km)+1):
                    if self.y[next_stop][ss][u] >= 0.9999 : 
                        itinerary.append(ss+1)
                        next_stop = ss+1
                if safety_stop == 10 : 
                    print(f"ERROR : In extract_itineraries, infinity loop")
                    break
            
            if self.verbose != 0 : print(f'The itinerary for user {u+1} is : {itinerary}')
            
            if itinerary != [0,len(self.scenario.dist_matrix_km)+1] :
                list_itineraries.append(itinerary)
        print(f"list_itineraries : {list_itineraries}")
        return list_itineraries

    def save_itineraries(self) -> None:
        """
        Prints the itineraries in a graph form.
        
        Parameters : 
        -------------
        itineraries : 
            The list of the different itineraries 
        path_instance : .
            The path where the graph will be saved 
        """
     

        G = nx.DiGraph()

        #Generates a palette of distinct colors (as many as itineraries)
        colors = plt.cm.get_cmap("tab20", len(self.itineraries))  
        
        color_map = []

        for idx, itinerary in enumerate(self.itineraries):
            for i in range(len(itinerary) - 1):
                G.add_edge(itinerary[i], itinerary[i + 1], itinerary=idx)  # Ajouter l'index de l'itinéraire comme attribut
                color_map.append(colors(idx))  # Assigner la couleur correspondante à l'itinéraire

        pos = nx.spring_layout(G, seed=42)  # Mise en page basée sur des forces

        # Plots the graph
        plt.figure(figsize=(10, 7))

        nx.draw_networkx_nodes(
            G, pos, node_size=2000, node_color="beige"
        )

        nx.draw_networkx_labels(
            G, pos, font_size=15, font_weight="bold"
        )

        for idx, itinerary in enumerate(self.itineraries):
            edges = [(itinerary[i], itinerary[i + 1]) for i in range(len(itinerary) - 1)]
            for u, v in edges:
                x1, y1 = pos[u]
                x2, y2 = pos[v]

                arrow = FancyArrowPatch(
                    posA=(x1, y1), posB=(x2, y2),
                    arrowstyle="-|>", color=colors(idx), 
                    mutation_scale=20, lw=2,
                    connectionstyle="arc3,rad=0.2"  
                )
                plt.gca().add_patch(arrow)  

        handles = [mlines.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors(i), markersize=10) 
                for i in range(len(self.itineraries))]
        labels = [f"Itinéraire {i+1}" for i in range(len(self.itineraries))]

        # prints legend
        plt.legend(handles=handles, labels=labels, title="Légende des itinéraires", loc="upper left")

        # prints the graph
        plt.title("Itinéraires avec couleurs distinctes, courbes et flèches")
        plt.axis("off")

        plt.savefig(f"{self.path_solution}/{self.method_used}_itineraries_time_limit{self.time_limit}.png", bbox_inches='tight',format='pdf')

        # plt.show()
        plt.close()

    def save(self,scenario,verbose):
        """ 
        Shorter function that saves all the required informations
        Parameters : 
        -------------
        self : Solution 
        """
        # self.itineraries = self.extract_itineraries( verbose)
        self.save_itineraries()
        self.save_solution()

    def set_ratio_roles_satisfied(self,scenario):
        nb_roles_satisfied = 0
        if self.verbose == 2: print(f'method : {self.method_used}')
        method_code = self.method_used.split("_")[0].strip()
       
        if method_code in ["mNC"]:
            bonus_satisfied = 0.0018
        elif method_code in ["MACE"]:
            def ordre_grandeur(x):
                if x == 0:
                    return 0
                exp = math.floor(math.log10(abs(x)))
                return 10**exp
            
            multiplicator_bonus = ordre_grandeur(1/scenario.total_potential_emissions )
            bonus_satisfied = 1.8 * multiplicator_bonus
        else: 
            print(f' ERROR: the bonus is not attributed for this method')

        if self.S :
            for u in range(self.scenario.nb_requests) :
                if self.S[u] >= bonus_satisfied:
                    nb_roles_satisfied +=1
        else : 
            for u in range(self.scenario.nb_requests) :
                if sum(self.x[v][u] for v in range (self.scenario.nb_requests))>= 0.9 : ## checks if the user is proposed a solution
                    if self.x[u][u] >= 0.9 : 
                        if self.scenario.all_requests[u].only_driver or self.scenario.all_requests[u].mainly_driver : ## checks if the user prefers to be driver
                            nb_roles_satisfied += 1
                    else : 
                        if self.scenario.all_requests[u].only_passenger or self.scenario.all_requests[u].mainly_passenger : ## checks if the user prefers to be apssenger
                            nb_roles_satisfied += 1
        ratio = (nb_roles_satisfied * 100)/ self.scenario.nb_requests
        return ratio




def print_one_itinerary(itinerary)-> None:
    """
    Print one itinerary as a graph 
    
    Parameters : 
    -------------
    itinerary : 
        list of the different stops visited 
        
    """
    

    # Creates a directed graph
    G = nx.DiGraph()

    # Adds nodes and vertices
    for i in range(len(itinerary) - 1):
        G.add_edge(itinerary[i], itinerary[i + 1])

    pos = {node: (index, 0) for index, node in enumerate(itinerary)}

    # Plots the graph
    plt.figure(figsize=(10, 3))
    nx.draw(
        G, pos, with_labels=True, 
        node_size=2000, node_color="beige",  
        font_size=15, font_weight="bold", 
        arrowsize=20, arrowstyle="->",
        edge_color="orange" 
    )

    # prints the graph
    plt.title("Itinéraire")
    plt.axis("off")
    plt.show()


def convert_numpy(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(i) for i in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def compute_real_emissions(solution : Solution):
    RE =  sum(solution.scenario.all_requests[u].emission_rate_vehicle * (sum( sum(solution.y[s+1][ss][u] * float(solution.scenario.dist_matrix_km[s][ss]) for s in range(len(solution.scenario.dist_matrix_km))) for ss in range(len(solution.scenario.all_stops))) )for u in range(len(solution.scenario.all_requests))) 
    return RE 






