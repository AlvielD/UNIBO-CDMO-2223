import os
import math
import json
import asyncio
import subprocess
from time import time
from datetime import timedelta
from tqdm import tqdm

from utils import *


# CONSTANTS
DEFAULT_TIMEOUT = 300000
DZN_FOLDER = 'CP/test_data/'
DATA_FOLDER = 'data/'
RES_FOLDER = 'res/CP/'


async def solve_instance(model, solver, data_file):
    """Solves an instance using the model and solver specified

    Args:
        model (string): name of the model to be used
        solver (string): name of the solver to be used
        data_file (string): name of the file to be used

    Returns:
        dict: dictionary containing the results
    """

    model_path = f"CP/src/{model}.mzn"
    data_file_path = f"{DZN_FOLDER}{data_file}"

    # Command to execute minizinc
    cmd = f"minizinc --solver {solver} -t 30000 {model_path} {data_file_path}"

    s_time = time()                                         # Measure starting time
    output = subprocess.check_output(cmd.split()).decode()  # Solve
    e_time = time()                                         # Measure ending time

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

    return result

async def solve_instances(models_list, solvers_list, data_file):

    tasks = set()

    for solver_name in solvers_list:
        for model_name in models_list:
            task = asyncio.create_task(
                solve_instance(model_name, solver_name, data_file)
            )
            tasks.add(task)
            task.solver = solver_name
            task.model = model_name
    
    done,_ = await asyncio.wait(tasks, return_when="ALL_COMPLETED")
    
    data = {}
    for task in done:
        result = task.result()
        data.update({f"{task.model}_{task.solver}": result})

    return data
    

def parse_solution(output):
    """Parse the solution string output by minizinc

    Args:
        output (string): minizinc's output

    Returns:
        int: value of the objective function
        list: list containing the route for each courier
    """

    m,n,_,_,_ = parse_file(f"{DATA_FOLDER}{data_file[:6]}.dat")

    output = output.split("\n")

    # Parse objective function value
    obj_sol = int(output[0].replace("\r", ""))

    # Parse the decision variables
    solution = []
    for i in range(m):
        solution.append([int(var) for var in output[i+1].split() if int(var) != n+1])

    return obj_sol, solution


if __name__ == "__main__":

    # List of models to be used
    models_list = [
        "MCP",
        "MCPSymbreakImp"
    ]

    # List of solvers to be used
    solvers_list = [
        "gecode",
        "chuffed"
    ]

    dict_order = [f"{model}_{solver}" for solver in solvers_list for model in models_list]

    data_files = os.listdir(DZN_FOLDER)

    # Solving loop
    for data_file, i in zip(data_files, tqdm(range(len(data_files)))):
        """data = {}
        for solver_name in solvers_list:
            for model_name in models_list:
                result = solve_instance(model_name, solver_name, data_file)
                data.update({f"{model_name}_{solver_name}": result})
        
        # Write the results
        with open(f"{RES_FOLDER}{data_file[4:6]}.json", 'w') as file:
            json.dump(data, file, indent=4)
        """
        data = asyncio.run(solve_instances(models_list, solvers_list, data_file))
        data = sort_dict(data, dict_order)

        # Write the results
        with open(f"{RES_FOLDER}{data_file[4:6]}.json", 'w') as file:
            json.dump(data, file, indent=4)