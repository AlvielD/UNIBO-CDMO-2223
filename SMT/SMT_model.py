from z3 import *
import json


def parse_file(file, solver):
    """Parse a .dat file and create the z3 variables containing the parameters of the problem

    Args:
        file (string): path to the file containing the instance data
        solver (z3.Z3PPObject): solver for the model

    Returns:
        int: number of couriers
        int: number of items
        z3.Array(IntSort, IntSort): load size for each courier
        z3.Array(IntSort, IntSort): size of each item
        z3.Array(IntSort, ArraySort(IntSort, IntSort)): distances matrix
    """

    # Read the file and initialize the variables
    with open(file, "r") as file:
        lines = file.readlines()

        # Parse the values from the file
        m = int(lines[0].strip())  # Number of couriers
        n = int(lines[1].strip())  # Number of items

        # Maximum load for each courier
        l_values = list(map(int, lines[2].split()))  
        l = Array('l', IntSort(), IntSort())
        for i in range(m):
            solver.add(l[i] == l_values[i])

        # Size of each item
        s_values = list(map(int, lines[3].split()))
        s = Array('s', IntSort(), IntSort())
        for i in range(n):
            solver.add(s[i] == s_values[i])

        # Distance matrix
        D_values = [list(map(int, line.split())) for line in lines[4:]]  # Distance matrix
        D = Array('D', IntSort(), ArraySort(IntSort(), IntSort()))  # Routes for each courier
        # Set the matrix of distances D to the default values
        for i in range(n+1):
        #    #a_i = Array('a_{i}', IntSort(), IntSort())
            for j in range(n+1):
                solver.add(D[i][j] == D_values[i][j])

    return m, n, l, s, D

def write_results(results, output_file):
    # Write the results
    with open(output_file, 'w') as file:
        json.dump(results, file, indent=4)

def z3_max(vector):
    maximum = vector[0]
    for value in vector[1:]:
        maximum = If(value > maximum, value, maximum)
    return maximum

def z3_min(vector):
    minimum = vector[0]
    for i in range(1,n):
        value = vector[i]
        minimum = If(value < minimum, value, minimum)
    return minimum

if __name__ == "__main__":

    # CREATE SOLVER INSTANCE
    solver = Optimize()


    # READ PARAMETERS
    file_path = "../data/inst03.dat"
    m, n, l, s, D = parse_file(file_path, solver)


    # DEFINE DECISION VARIABLES 
    routes = Array('routes', IntSort(), ArraySort(IntSort(), IntSort()))  # Routes for each courier


    # DEFINE DOMAIN CONSTRAINTS
    for i in range(m):
        for t in range(n):
            solver.add(And(routes[i][t] >= 1, routes[i][t] <= n + 1))


    # DEFINE CONSTRAINTS

    # All the values from 1 to n need to appear EXACTLY ONCE in the routes matrix
    for p in range(1,n+1):
        solver.add(Sum([If(routes[i][j] == p, 1, 0) for i in range(m) for j in range(n+1)]) == 1)

    for i in range(m):
        
        # The courier must finish at the origin point
        solver.add(routes[i][n] == n+1)
        
        # Constraint to force that the total size of items assigned to each courier cannot exceed their maximum load size and constraint to force that the total size of items assigned to each courier is at least the load of the min value of item sizes
        sums = Sum([If(routes[i][j] != n+1, s[routes[i][j] -1], 0) for j in range(n+1)])
        solver.add(And(sums <= l[i], sums>=z3_min(s)))
        
        
        # SYMMETRY BREAKING
        #Constraint to force the first value of each row of the matrix to be different from n+1
        solver.add(routes[i][0] != n+1)

        #Constraint to force all the numbers after the first n+1 to be also n+1
        for j in range(n):
            solver.add(If(routes[i][j] == n+1, routes[i][j+1] == n+1, True))
    
    # IMPLICIT CONSTRAINT
    # Constraint to force exactly (m * (n + 1)) - n n+1s
    solver.add(Sum([If(routes[i][j] == n + 1, 1, 0) for i in range(m) for j in range(n+1)]) == (m * (n + 1)) - n)

    # OBJECTIVE FUNCTION
    # Application of the same objective function above to all couriers
    # dist_courier = [(Sum( [D[routes[i][j]][routes[i][j + 1]] for j in range(n)] )+ D[n + 1][routes[i][0]] )  for i in range(m)]
    dist_courier = [(Sum( [D[routes[i][j]-1][routes[i][j + 1]-1] for j in range(n)] )+ D[n][routes[i][0]-1] )  for i in range(m)]
    maximum = z3_max(dist_courier)

    # Default values established in case a solution is not found
    solved = False          # Assume by default we do not solve the instance
    time_sol = 300000       # Time is set by default to maximum
    optimal_sol = False
    obj_sol = None
    solution = []

    solver.minimize(maximum)
    if solver.check() == sat:
        model = solver.model()
        length = model.evaluate(maximum)
        
        routes_sol = []
        for i in range(m):
            route = [model.evaluate(routes[i][j]).as_long() for j in range(n+1)]
            routes_sol.append([value for value in route if value != n+1])
        print(routes_sol)
        print(length)

        obj_sol = length.as_long()
        solution = routes_sol
    else:
        print("no sat")

    results = {
        "time": time_sol,
        "optimal": optimal_sol,
        "obj": obj_sol,
        "sol": solution
    }

    write_results(results, "../res/SMT/3.json")

    print('---n---')
    print(n)
    print("---SIZES---")
    print([model.evaluate(s[i]) for i in range(n) ])
    print("---LOADS---")
    print([model.evaluate(l[i]) for i in range(m) ])
    print('---DISTANCES---')  
    for i in range(n+1):
        row = []
        for j in range(n+1):
            a = model.evaluate(D[i][j]).as_long()
            row.append(a)
        print(row)

    print('---ROUTES---')  
    for i in range(m):
        row = []
        for j in range(n+1):
            a = model.evaluate(routes[i][j]).as_long()
            row.append(a)
        print(row)

    print('---DIST COURIER---')  
    print([model.evaluate(dist_courier[i]) for i in range(m)])