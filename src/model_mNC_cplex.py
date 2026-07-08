from docplex.mp.model import Model
from class_request import Request
from class_solution import Solution
from class_scenario import Scenario


def model_mNC_cplex(scenario: Scenario, verbose: int) -> Solution:
    """ Il s'agit du modèle : 
            - 4 rôles 
            - coeff devant nb de requests : 9 
            - bonus : 0, 0.001, 0.002 
            - temps continu 
            - 7 variables"""
    model = Model("flexible_carpooling_cplex")

    n = len(scenario.all_requests)
    s_len = len(scenario.dist_matrix_km)
    
    ## Big-M values
    M1 = 288
    M3 = [req.nb_stops + 1 + req.limit_via for req in scenario.all_requests]

    multiplicator_bonus = 0.001
    # Variables
    x = [[model.binary_var(name=f"x_{u+1}_{v+1}") for v in range(n)] for u in range(n)]

    y = [[[model.binary_var(name=f"y_{s}_{ss+1}_{u+1}")
            for u in range(n)]
            for ss in range(s_len + 1)]
            for s in range(s_len + 1)]

    F = [[[model.integer_var(name=f"F_{s}_{ss+1}_{u+1}", lb=0)
            for u in range(n)]
            for ss in range(s_len + 1)]
            for s in range(s_len + 1)]

    theta_a = [[model.continuous_var(name=f"theta_a_{s+1}_{u+1}", lb=0)
                for u in range(n)] for s in range(s_len)]
    
    theta_d = [[model.continuous_var(name=f"theta_d_{s+1}_{u+1}", lb=0)
                for u in range(n)] for s in range(s_len)]

    Q = [[model.integer_var(name=f"Q_{s}_{u+1}", lb=0) for u in range(n)] for s in range(s_len + 1)]
    
    S = [model.continuous_var(name=f"S_{u+1}") for u in range(n)]

    # Objective (118)
    model.maximize(
        9 * model.sum(x[u][v] for u in range(n) for v in range(n)) +
        model.sum(S[u] for u in range(n)) -
        model.sum(x[u][u] for u in range(n))
    )

    # Constraints
    for s in scenario.all_stops_source:
        if s > 0:
            for u in range(n):
                model.add_constraint(y[s][s - 1][u] == 0) 
                model.add_constraint(F[s][s - 1][u] == 0)

    for u in range(n):
        model.add_constraint(Q[0][u] == 0)

    for v in range(n):
        model.add_constraint(model.sum(x[u][v] for u in range(n)) <= 1) #(123)

    for u in range(n):
        for v in range(n):
            model.add_constraint(x[u][v] <= x[u][u])  #(124)

    for u in range(n):
        model.add_constraint(y[0][s_len][u] == 1 - x[u][u])  # (132)
        for s in range(s_len):
            for ss in range(s_len):
                if (ss + 1) != s:
                    model.add_constraint(y[s + 1][ss][u] <= x[u][u]) #(133)


    for u in range(n):
        for s in range(s_len):        #(137)
            model.add_constraint( 
                model.sum(y[s + 1][ss][u] for ss in range(s_len + 1)) ==
                model.sum(y[ss][s][u] for ss in range(s_len + 1))
            ) 

    for u in range(n):
        model.add_constraint(model.sum(y[0][s][u] for s in range(s_len + 1)) == 1)   #(130)
        model.add_constraint(model.sum(y[s][s_len][u] for s in range(s_len + 1)) == 1)   #(131)

    for u in range(n):
        model.add_constraint(model.sum(F[0][s][u] for s in range(s_len + 1)) == M3[u]) #(140)
        for s in range(s_len + 1):
            model.add_constraint(model.sum(y[s][ss][u] for ss in range(s_len + 1)) <= 1)   #(138)
            model.add_constraint(model.sum(y[ss][s][u] for ss in range(s_len + 1)) <= 1)  #(139)

    for u in range(n):
        for v in range(n):
            for s in scenario.all_requests[v].stops: 
                model.add_constraint(                                 #(141)
                    model.sum(F[ss][s - 1][u] for ss in range(s_len + 1)) -
                    model.sum(F[s][ss][u] for ss in range(s_len + 1)) >= x[u][v]
                )
                model.add_constraint(                                #(142)
                    model.sum(F[ss][s - 1][u] for ss in range(s_len + 1)) -
                    model.sum(F[s][ss][u] for ss in range(s_len + 1)) <= x[u][v] + M3[u] * (1 - x[u][v])
                )

    for u in range(n):
        for s in range(s_len + 1):
            for ss in range(s_len + 1):
                model.add_constraint(F[s][ss][u] >= y[s][ss][u])     #(143)
                model.add_constraint(F[s][ss][u] <= M3[u] * y[s][ss][u])     #(144)

    for u in range(n):
        req = scenario.all_requests[u]
        if req.driver and not req.passenger:
            model.add_constraint(x[u][u] == 1)     #(125)
        if not req.driver:
            model.add_constraint(model.sum(x[u][v] for v in range(n)) == 0)     #(126)

    for u in range(n):
        model.add_constraint(y[0][scenario.all_requests[u].stops[0] - 1][u] == x[u][u])     #(135)
        model.add_constraint(y[scenario.all_requests[u].stops[-1]][s_len][u] == x[u][u])     #(136)

    for u in range(n):
        for s in range(s_len):
            model.add_constraint(theta_a[s][u] <= theta_d[s][u])     #(145)

    for u in range(n):
        for v in range(n):
            for s in scenario.all_requests[v].stops:
                for ss in scenario.all_requests[v].stops[scenario.all_requests[v].stops.index(s):]:
                    if ss != s:     #(134)
                        model.add_constraint(theta_d[s - 1][u] - theta_a[ss - 1][u] <= M1 * (1 - x[u][v]))

    for u in range(n):
        for v in range(n):
            r = scenario.all_requests[v]
            lb, ub = r.time_windows[str(r.stops[0])]
            model.add_constraint(lb * x[u][v] <= theta_d[r.stops[0] - 1][u])     #(146)
            model.add_constraint(theta_d[r.stops[0] - 1][u] - M1 * (1 - x[u][v]) <= ub * x[u][v])  #(147)

    for u in range(n):
        for v in range(n):
            for s in scenario.all_requests[v].stops:
                if s != scenario.all_requests[v].stops[0]:
                    lb, ub = scenario.all_requests[v].time_windows[str(s)]
                    model.add_constraint(lb * x[u][v] <= theta_a[s - 1][u])   #(148)
                    model.add_constraint(theta_a[s - 1][u] - M1 * (1 - x[u][v]) <= ub * x[u][v])   #(149)

    for u in range(n):
        for s in range(s_len):
            for ss in range(s_len):
                if s != ss:
                    model.add_constraint(     #(150)
                        theta_a[ss][u] >= theta_d[s][u] +
                        scenario.dist_matrix_time[s][ss] * y[s + 1][ss][u] -
                        M1 * (1 - y[s + 1][ss][u])
                    )
                    model.add_constraint(     #(151)
                        theta_a[ss][u] <= theta_d[s][u] +
                        scenario.dist_matrix_time[s][ss] * y[s + 1][ss][u] +
                        M1 * (1 - y[s + 1][ss][u])
                    )

    for u in range(n):
        for s in range(s_len + 1):   #(127)
            model.add_constraint(Q[s][u] <= scenario.all_requests[u].v_capacity * (1 - y[0][s_len][u]))

    for u in range(n):
        for s in range(s_len + 1):
            for ss in range(s_len):
                if s != (ss + 1):
                    model.add_constraint(     #(128)
                        Q[ss + 1][u] <= Q[s][u] + model.sum(
                            (scenario.all_requests[v].pick_ups[scenario.all_requests[v].stops.index(ss + 1)] -
                             scenario.all_requests[v].deliveries[scenario.all_requests[v].stops.index(ss + 1)]) * x[u][v]
                            for v in range(n) if (ss + 1) in scenario.all_requests[v].stops
                        ) + scenario.all_requests[u].v_capacity * (1 - y[s][ss][u])
                    )
                    model.add_constraint(     #(129)
                        Q[ss + 1][u] >= Q[s][u] + model.sum(
                            (scenario.all_requests[v].pick_ups[scenario.all_requests[v].stops.index(ss + 1)] -
                             scenario.all_requests[v].deliveries[scenario.all_requests[v].stops.index(ss + 1)]) * x[u][v]
                            for v in range(n) if (ss + 1) in scenario.all_requests[v].stops
                        ) - scenario.all_requests[u].v_capacity * (1 - y[s][ss][u])
                    )

    for u in range(n):
        req = scenario.all_requests[u]
        if req.only_passenger:
            model.add_constraint(S[u] == 2*multiplicator_bonus * model.sum(x[v][u] for v in range(n)))  #(152)
        elif req.only_driver:
            model.add_constraint(S[u] == 2*multiplicator_bonus * x[u][u])  #(153)
        elif req.mainly_driver:
            model.add_constraint(S[u] == 1*multiplicator_bonus * (model.sum(x[v][u] for v in range(n) if v != u)) + 2*multiplicator_bonus * x[u][u])   #(154)
        elif req.mainly_passenger:
            model.add_constraint(S[u] == 2*multiplicator_bonus * (model.sum(x[v][u] for v in range(n) if v != u)) + 1*multiplicator_bonus * x[u][u])  #(155)
        
        

    # model.add_constraint(x[0][0] == 1)
    # # model.add_constraint(x[0][1] == 1)
    # model.add_constraint(x[0][2] == 1)
    # model.add_constraint(y[0][4][0] == 1)
    # model.add_constraint(y[5][0][0] == 1)
    # # model.add_constraint(y[1][6][0] == 1)
    # model.add_constraint(y[6][3][0] == 1)
    # model.add_constraint(y[0][1][1] == 1)
    # model.add_constraint(y[2][4][1] == 1)
    # model.add_constraint(y[0][3][3] == 1)
    # model.add_constraint(y[4][4][3] == 1)
    model.context.cplex_parameters.mip.tolerances.mipgap = 1e-6
    model.context.cplex_parameters.mip.tolerances.absmipgap = 1e-9
    model.context.cplex_parameters.mip.tolerances.integrality = 1e-9
    model.context.cplex_parameters.simplex.tolerances.feasibility = 1e-9
    # Solve
    if verbose == 2:
        model.set_log_output(True)
    else:
        model.set_log_output(None)

    solution = model.solve(log_output=verbose,time_limit=600)

    
    if solution : 
        if verbose != 0 :print(f"Objective: {model.objective_value}")
        
        x_values=[[x[u][v].solution_value for v in range(n)] for u in range(n)]
        y_values=[[[y[s][ss][u].solution_value for u in range(n)]
            for ss in range(s_len + 1)]
            for s in range(s_len + 1)]
        F_values=[[[F[s][ss][u].solution_value for u in range(n)]
            for ss in range(s_len + 1)]
            for s in range(s_len + 1)]
        # for s in range(s_len+1) :
        #     for ss in range(s_len+1) :
        #         for u in range(n):
        #             if F_values[s][ss][u] >= 0.9 : 
        #                 print(f'F[{s}][{ss}][{u}] = {F_values[s][ss][u]}')
        theta_a_values=[[theta_a[s][u].solution_value for u in range(n)] for s in range(s_len)]
        theta_d_values=[[theta_d[s][u].solution_value for u in range(n)] for s in range(s_len)]
        Q_values=[[Q[s][u].solution_value for u in range(n)] for s in range(s_len + 1)]
        S_values=[S[u].solution_value for u in range(n)]
    else : 
        print(f'the solution is not feasible')
        return
    if model.solve_status.name == 'OPTIMAL_SOLUTION':
        print(f'the solution is optimal')
        status_ = 'Optimal'
    elif model.solve_status.name == 'INFEASIBLE_SOLUTION':
        print(f'the solution is not feasible')
        status_ = 'Infeasible'
    else : 
        print(f'the status of the solution is : {model.solve_status}')
        status_ = 'Feasible'

    if status_ != 'Infeasible' :
        if verbose != 0 :print(f'xvalues : {x_values}')
        for u in range(len(scenario.all_requests)):
            if x_values[u][u] >= 0.99 :
                if verbose != 0 :print(f'User {u+1} takes his car')
            for v in range(len(scenario.all_requests)):
                if x_values[u][v] >= 0.99 : 
                    if verbose != 0 :print(f'\t User {v+1} goes in the car driven by {u+1}')
        nb_requests_satisfied = sum(
            x_values[u][v] for u in range(len(scenario.all_requests)) for v in range(len(scenario.all_requests))
        )
    else : 
        nb_requests_satisfied = 0 


  
    # Collect values into a Solution object (assumed structure)
    
    return Solution(status_,scenario,model.objective_value,nb_requests_satisfied,"mNC_CPLEX", x_values, y_values, F_values, theta_a_values, theta_d_values, Q_values, S_values,'cplex',multiplicator_bonus=multiplicator_bonus,verbose = verbose)
    
