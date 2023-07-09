import os
import subprocess
from time import time
import re
import math
from datetime import timedelta

DEFAULT_TIMEOUT = timedelta(seconds=300)

def parse_file(file):
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
        l = list(map(int, lines[2].split()))  

        # Size of each item
        s = list(map(int, lines[3].split()))

        # Distance matrix
        D = [list(map(int, line.split())) for line in lines[4:]]  # Distance matrix

    return m, n, l, s, D

def solve_instance(model, solver, data_file):

    # TODO: Set up the routes for data folders
    out_file = f"res/CP/{data_file[4:6]}.json"
    model_path = f"CP/src/{model}.mzn"
    data_file_path = f"CP/test_data/{data_file}"

    cmd = f"minizinc --solver {solver} -t {DEFAULT_TIMEOUT} {model_path} {data_file_path}"
    s_time = time()
    output = subprocess.check_output(cmd.split()).decode()
    e_time = time()
    time_sol = math.floor(e_time-s_time)

    obj_sol, solution = parse_solution(output)

    optimal = False
    if time_sol < 300: optimal = True

    result = {
        "time": time_sol,
        "optimal": optimal,
        "obj": obj_sol,
        "sol": solution
    }

    print(result)
    

def parse_solution(output):

    m,n,_,_,_ = parse_file(f"data/{data_file[:6]}.dat")

    output = output.split("\n")

    # Parse objective function value
    obj_sol = output[0].replace("\r", "")

    # Parse the decision variables
    solution = []
    for i in range(m):
        solution.append([int(var) for var in output[i+1].split() if int(var) != n+1])

    return obj_sol, solution


if __name__ == "__main__":

    models_list = [
        "MCP",
        "MCPSymbreakImp"
    ]

    solvers_list = [
        "gecode",
        "chuffed"
    ]

    data_folder = 'CP/test_data/'
    data_files = os.listdir(data_folder)

    for data_file in data_files:
        for solver_name in solvers_list:
            for model_name in models_list:
                solve_instance(model_name, solver_name, data_file)