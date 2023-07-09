import time
import math
from pulp import *

def build_model(model_name, parameters):

    m,n,l_values,s_values,D_values = parameters
    model = LpProblem(model_name, LpMinimize)


    # DECISION VARIABLES
    routes = [LpVariable.dicts(f"routes_{i+1}", (range(n+1), range(n + 1)), cat = "Binary") for i in range(m)]
    
    # Used to individuate possible presence of cycles in the matrix.
    y_cycles = [ LpVariable(f"y_cycles_{d}", cat="Binary") for d in range(m) ]

    # Absolute values of the the differenze of indices of row with indices of column.
    abs_s = [ LpVariable(f"abs_s_{d}", cat="Integer", lowBound=0) for d in range(m) ]

    # Used to define abs_s to simulate an absolute value.
    y_f = [ LpVariable(f"y_{d}", cat="Binary") for d in range(m) ]
    p = [ LpVariable(f"p_{d}", cat="Integer", lowBound=0) for d in range(m) ]
    enne = [ LpVariable(f"enne_{d}", cat="Integer", lowBound=0) for d in range(m) ] 


    # DEFINE CONSTRAINTS

    # All items are delivered, to ensure that the sum of the 1s in the routes matrix is exactly n+m
    model += lpSum(routes) == (n+m)

    #No 1s on the main diagonal. To ensure that is not possible to go from a distribution point to itself.
    # Forcing the sum on the main diagonal to be 0
    model += lpSum([routes[d][i][i] for d in range(m) for i in range(n+1)]) == 0

    # Exactly 1 value in the same columns (except the last) for all couriers.
    # To ensure that each destination point is visited only once by one courier.
    for j in range(n):
        model += lpSum([routes[d][i][j] for d in range(m)
                    for i in range(n+1)]) == 1

    # Exactly 1 value in the same row (except the last) for all couriers.
    # To ensure that only one courier can start from a distribution point.
    for i in range(n):
        model += lpSum([routes[d][i][j] for d in range(m)
                    for j in range(n+1)]) == 1

    for d in range(m):

        # Each courier delivers at least 1 item. (IMPLIED CONSTRAINT)
        # Forces to have at least two 1s for each courier.
        model += lpSum(routes[d]) >= 2

        # Each courier starts from the origin point. 
        # Forces to have exactly a 1 in the last row. 
        model += lpSum([routes[d][n][j] for j in range(n)]) == 1

        # Each courier ends to the origin point. 
        # Forces to have exactly a 1 in the last column.
        model += lpSum([routes[d][i][n] for i in range(n)]) == 1

        # Avoid courier overload.
        # The sum of the sizes of the items assigned for each courier don’t exceed the maximum load of that courier.
        model += lpSum([lpSum(routes[d][i]) * s_values[i]
                    for i in range(n)]) <= l_values[d]

        # Sum of indices of rows of all the 1s.
        sl = lpSum([lpSum([routes[d][i][j]*(i+1) for j in range(n)])
                for i in range(n)])

        # Sum of indices or columns of all 1s.
        sr = lpSum([lpSum([routes[d][j][i] * (i+1) for j in range(n)])
                for i in range(n)])

        # Difference of indices.
        s = sl -sr

        #Maximum value that sr or sl can assume.
        M = sum([i for i in range(n)])

        # Detect when the courier d deliver only one item => 
        # y_cycle = 0 There are all 0s inside the route[d] matrix except in the last row and column.
        # y_cycle = 1 There are 1s inside the route[d] matrix.
        # Force y_cycle[d] to be defined in range [sr/M , sr]. 
        model += y_cycles[d] >= sr/M
        model += y_cycles[d] <= sr
        
        # Implementation of the absolute value of s, abs_s = abs(s).
        # the absolute value is a non-linear function. However, abs(x) is a piecewise-linear function and we can use a modeling technique.  
        # We can use two separate variables p, n >= 0 and use an indicator variable y to ensure that only p or n can have a value other than zero at any time.
        model += s == p[d] - enne[d]
        model += p[d] <= M * y_f[d]
        model += enne[d] <= M*(1 - y_f[d])
        model += abs_s[d] == p[d] + enne[d]

        # Absolute values are always positively defined.
        model += abs_s[d] >=0

        # Couriers can have only a main cycle starting and ending to the origin point, no inner cycles admitted.
        # Every solution having y_cycles = 1 and abs_s[d] = 0 will be discarded because it represents an inner cycle.
        model += abs_s[d] >= y_cycles[d]
        

        # The path must be coherent => there should exist a coherent path from the first destination point to the origin.
        # The sum of the values on the row 1 is equal to the sum of values in the comumn 1.
        for i in range(n+1):
            model += (lpSum([routes[d][i][a] for a in range(n+1)])
                    == lpSum([routes[d][t][i] for t in range(n+1)]))

        # Couriers cannot go back to a destination point already visited, except if it is the origin point.
        # Example   o -> 1   1 -> is allowed.
        for i in range(n):
            for j in range(n):
                model += lpSum([routes[d][i][j], routes[d][j][i]]) <= 1


    # OBJECTIVE FUNCTION 
    objective = [lpSum([D_values[t][j] * routes[i][t][j] for t in range(n+1) for j in range(n+1)]) for i in range(m)]
    maximum = LpVariable("maximum", lowBound=0, cat="Integer")

    # Find the maximum in the objective function.
    for i in range(len(objective)):
        model += maximum>=objective[i]

    # Minimize the maximum.
    model+= maximum

    return model, routes

def solve_model(model, routes, parameters):

    m,n,_,_,D_values=parameters

    time_sol = 300
    optimal_sol = False
    obj_sol = None
    solution = []

    # Creat instance of the solver
    solver = pulp.PULP_CBC_CMD(mip=True, msg=False, timeLimit=300)

    # Solve the model (and time it)
    s_time = time()
    model.solve(solver)
    e_time = time()
    time_sol = math.floor(e_time-s_time)

    if model.status == LpStatusOptimal:
        length = model.objective.value()

    # GATHER RESULTS
    routes_values = []
    for d in range(m):
        r = []
        index = n
        while True: 
            index = [routes[d][index][j].varValue for j in range(n+1)].index(1.0)
            if index+1 != n+1: r.append(index+1)
            if(index == n):
                routes_values.append(r)
                break
    
    solution = routes_values
    obj_sol = length
    if time_sol < 300: optimal_sol = True

    results = {
        "time": time_sol,
        "optimal": optimal_sol,
        "obj": obj_sol,
        "sol": solution
    }

    return results