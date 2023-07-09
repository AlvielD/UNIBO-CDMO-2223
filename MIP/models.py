import time
import math
from pulp import *

def build_model(model_name, parameters):

    m,n,l_values,s_values,D_values = parameters

    model = LpProblem(model_name, LpMinimize)

    # DECISION VARIABLES
    routes = [LpVariable.dicts(f"routes_{i+1}", (range(n+1), range(n + 1)), cat = "Binary") for i in range(m)]
    
    y = [ LpVariable(f"y_{d}", cat="Binary") for d in range(m) ]

    # DEFINE CONSTRAINTS

    # Force the model to have the chosen amount of iterms and couriers
    model += lpSum(routes) == (n+m)

    # Nº of 1s on diagonals
    model += lpSum([routes[d][i][i] for d in range(m) for i in range(n+1)]) == 0

    # Exactly 1 value in the same columns for each courier except last column
    for j in range(n):
        model += lpSum([routes[d][i][j] for d in range(m) for i in range(n+1)]) == 1

    # Exactly 1 value in the same row for each courier except last row
    for i in range(n):
        model += lpSum([routes[d][i][j] for d in range(m) for j in range(n+1)]) == 1

    for d in range(m):

        #At least 1 value for each courier
        model += lpSum(routes[d]) >= 2

        #Exactly 1 value in the last row for each courier   
        model += lpSum([routes[d][n][j]  for j in range(n+1)]) == 1

        #Exactly 1 value in the last column for each courier
        model += lpSum([routes[d][i][n]  for i in range(n+1)]) == 1

        #Loads constraint
        model += lpSum([lpSum(routes[d][i]) * s_values[i] for i in range(n)]) <= l_values[d]

        s = lpSum([lpSum([ routes[d][i][j]*(i+1) for j in range(n)]) for i in range(n)]) - lpSum([lpSum([ routes[d][j][i]* (i+1) for j in range(n)])  for i in range(n)])
        sl = lpSum([lpSum([ routes[d][i][j]*(i+1) for j in range(n)]) for i in range(n)])
        sr = lpSum([lpSum([ routes[d][j][i]* (i+1) for j in range(n)])  for i in range(n)])
        # Add additional constraints based on the if-then condition
        
        # Add constraints if the condition is met (y = 1)
        model+= y[d] >= sr/sum([i for i in range(n)]), f"random constraint_{d}"
        model += y[d] <= sr
        model += s >= y[d]
        #model += s>= (-1 * y[d])
        #model += s
        #model += y[d]

        #The path must be coherent => there should exist a coherent path from the first destination point to the origin
        #It's implemented by verifying that the sum of the values on the row 1 is equal to the sum of values in the comumn 1 => 
        #if there's a row in the ith row there should be a 1 also in the ith column and viceversa
        for i in range(n+1):
            model += ( lpSum([routes[d][i][a] for a in range(n+1) ]) == lpSum([routes[d][t][i] for t in range(n+1)]) )


        for i in range(n):
            for j in range(n):
                ##Couriers cannot go back to a destination point already visited, except if it is the origin point
                #Example   o -> 1   1 -> is allowed
                model += lpSum([routes[d][i][j],routes[d][j][i]]) <=1

    # OBJECTIVE FUNCTION 
    objective = [lpSum([D_values[t][j] * routes[i][t][j] for t in range(n+1) for j in range(n+1)]) for i in range(m)]

    maximum = LpVariable("maximum", lowBound=0, cat="Integer")

    for i in range(len(objective)):
        model.addConstraint(constraint = (maximum>=objective[i])) 

    model.setObjective(maximum)

    return model, routes

def solve_model(model, routes, parameters):

    m,n,_,_,D_values=parameters

    time_sol = 300
    optimal_sol = False
    obj_sol = None
    solution = []

    # Creat instance of the solver
    solver = pulp.PULP_CBC_CMD(mip=True, timeLimit=300)

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