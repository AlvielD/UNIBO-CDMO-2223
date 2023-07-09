from z3 import *
from utils import *
from time import time

def build_params(parameters, solver):
    
    # READ PARAMETERS
    m, n, l_values, s_values, D_values = parameters

    # TURN PARAMETERS INTO Z3 VARIABLES
    l = Array('l', IntSort(), IntSort())
    for i in range(m):
        solver.add(l[i] == l_values[i])

    s = Array('s', IntSort(), IntSort())
    for i in range(n):
        solver.add(s[i] == s_values[i])

    D = Array('D', IntSort(), ArraySort(IntSort(), IntSort()))  # Distance to each point
    # Set the matrix of distances D to the default values
    for i in range(n+1):
    #    #a_i = Array('a_{i}', IntSort(), IntSort())
        for j in range(n+1):
            solver.add(D[i][j] == D_values[i][j])
    
    return solver, l, s, D

def solve_model(solver, routes, maximum, parameters, model_name):

    # Default values established in case a solution is not found
    time_sol = 300       # Time is set by default to maximum
    optimal_sol = False
    obj_sol = None
    solution = []

    m,n,_,_,_ = parameters

    solver.minimize(maximum)

    print("Checking satisfiability...")
    s_time = time()
    result = solver.check()
    if result == sat:
        print("Solving...")
        model = solver.model()
        length = model.evaluate(maximum)
        
        routes_sol = []
        for i in range(m):
            route = [model.evaluate(routes[i][j]).as_long() for j in range(n+1)]
            routes_sol.append([value for value in route if value != n+1])

        obj_sol = length.as_long()
        solution = routes_sol
    elif result == unknown:
        print("N/A")
    else:
        print("Unsat")

    e_time = time()

    time_sol = math.floor(e_time-s_time)
    if time_sol < 300: optimal_sol = True

    results = {
        f"{model_name}":{
            "time": time_sol,
            "optimal": optimal_sol,
            "obj": obj_sol,
            "sol": solution
        }
    }

    return results


def build_model(parameters, model_name=None):

    # CREATE SOLVER INSTANCE
    solver = Optimize()
    solver.set("timeout", 300000)

    # BUILD THE PARAMETERS INTO THE MODEL
    solver, l, s, D = build_params(parameters, solver)

    # DEFINE DECISION VARIABLES 
    routes = Array('routes', IntSort(), ArraySort(IntSort(), IntSort()))  # Routes for each courier

    # DEFINE DOMAIN CONSTRAINTS
    m, n, _, _, _ = parameters
    for i in range(m):
        for t in range(n):
            solver.add(And(routes[i][t] >= 1, routes[i][t] <= n + 1))

    # DEFINE CONSTRAINTS

    # All the values from 1 to n need to appear EXACTLY ONCE in the routes matrix
    for p in range(1,n+1):
        solver.add(Sum([If(routes[i][j] == p, 1, 0) for i in range(m) for j in range(n+1)]) == 1)

    for i in range(m):
        
        if model_name == "MCP":
            # The courier must finish at the origin point
            solver.add(routes[i][n] == n+1)
        else:
            for j in range(n-m+1, n+1):
                solver.add(routes[i][j] == n+1)

        
        # Constraint to force that the total size of items assigned to each courier cannot exceed their maximum load size and constraint to force that the total size of items assigned to each courier is at least the load of the min value of item sizes
        sums = Sum([If(routes[i][j] < n+1, s[routes[i][j] -1], 0) for j in range(n+1)])
        solver.add(sums <= l[i])

        #Constraint to force all the numbers after the first n+1 to be also n+1
        for j in range(n):
            solver.add(If(routes[i][j] == n+1, routes[i][j+1] == n+1, True))
        
        if model_name == "MCPSymbreakImp":
            # SYMMETRY BREAKING
            #Constraint to force the first value of each row of the matrix to be different from n+1
            solver.add(routes[i][0] < n+1)
            

    if model_name == "MCPSymbreakImp":
        # IMPLICIT CONSTRAINT
        # Constraint to force exactly (m * (n + 1)) - n n+1s
        solver.add(Sum([If(routes[i][j] == n + 1, 1, 0) for i in range(m) for j in range(n+1)]) == (m * (n + 1)) - n)

    # OBJECTIVE FUNCTION
    # Application of the same objective function above to all couriers
    # dist_courier = [(Sum( [D[routes[i][j]][routes[i][j + 1]] for j in range(n)] )+ D[n + 1][routes[i][0]] )  for i in range(m)]
    dist_courier = [(Sum( [D[routes[i][j]-1][routes[i][j + 1]-1] for j in range(n)] )+ D[n][routes[i][0]-1] )  for i in range(m)]
    maximum = z3_max(dist_courier)

    return solver, routes, maximum