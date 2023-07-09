import os
import json
import asyncio
from datetime import timedelta
from tqdm import tqdm
from minizinc import Instance, Model, Solver
from minizinc.result import Status
from minizinc.dzn import parse_dzn
from pathlib import Path
import math
#import matplotlib.pyplot as plt

def solve(model_name, solver_name, data_file):
    """Solve the minizinc model given a selected solver, data file (.dzn) and write results
    to an output_file

    Args:
        model_name (str): name of the model to be use to solve the instance
        solver (str): choosen solver to solve the instance
        data (str): data file containing the instance of the problem
        output_file (str): name of the file to write the solution
    """

    model = Model(f"CP/src/{model_name}.mzn")   # Load model from the file
    solver = Solver.lookup(solver_name)              # Look for the configuration of gecode solver
    
    instance = Instance(solver, model)          # Create instance of the problem
    instance.add_file(data_file)                # Add the data to the instance

    # Solve instance (set a timeout of 300000 miliseconds)
    timeout = datetime.timedelta(milliseconds=300000)
    result = instance.solve(timeout=timeout)

    # Default values established in case a solution is not found
    time_sol = 300000       # Time is set by default to maximum
    optimal_sol = False
    obj_sol = None
    solution = []

    # If the solution is found, change values
    if result.solution:
        time_sol = math.floor(int(result.statistics.get('time').total_seconds()))
        if time_sol < 300: optimal_sol = True
        obj_sol = int(result.objective)

        # Remove the repeated values from the solution (the repeated value is n+1 indicating the courier coming back to origin)
        for c in result.solution.routes: solution.append([item for item in c if c.count(item) == 1])

    # Create dictionary object (dump it to json)
    # TODO: Avoid the formatted solution to be display in mulitple lines
    data = {
        f"{model_name}_{solver_name}": 
        {
            "time": time_sol,
            "optimal": optimal_sol,
            "obj": obj_sol,
            "sol": solution
        }
    }

    # Return the json data
    return data

async def solve_instances(models, solvers, data_files, output_folder):

    tasks = set()
    
    for data_file in data_files:
        for solver_name in solvers:
            for model_name in models:

                # Create an instance for each file-solver-model
                model = Model(f"CP/src/{model_name}.mzn")   # Load model from the file
                solver = Solver.lookup(solver_name)         # Look for the configuration of gecode solver
                
                instance = Instance(solver, model)          # Create instance of the problem
                instance.add_file(f"CP/data/{data_file}")   # Add the data to the instance

                # Create a task for the solving of each instance
                task = asyncio.create_task(instance.solve_asynchronised(instance, timedelta(minutes=5)))
                task.solver = solver_name
                task.model = model_name
                task.instance = data_file
                tasks.add(task)
    
    done, _ = await asyncio.wait(tasks, return_when="ALL_COMPLETED")
    data = gather_results(done)

    dict_order = [f"{model_name}_{solver_name}" for solver_name in solvers_list for model_name in models_list]

    for data_file in data_files:

        output_file = f"{output_folder}{data_file[4:6]}.json"
        solution = data.get(data_file)

        solution = sort_dict(solution, dict_order)

        # Write the results
        with open(output_file, 'w') as file:
            json.dump(solution, file, indent=4)
    
    return data

async def solve_asynchronised(instance, timeout):
    async for sol in instance.solutions(timeout):
        if sol.solution is None: continue
        if sol.status == Status.OPTIMAL_SOLUTION:
            return sol


def gather_results(tasks):
    """Create a dictionary with the results of the unsynchronised solved tasks

    Args:
        tasks (set): set containing asyncio.Task objects with the results of the unsynchronised competition

    Returns:
        dict: dictionary containing the results of the computation
    """

    # Init dictionary to store the results
    data = {}

    for task in tasks:
        # Get the result for every task
        result = task.result()

        # DEFAULT VALUES (Only if a solution is not found)
        time_sol = 300       # Time is set by default to maximum
        optimal_sol = False
        obj_sol = None
        solution = []

        if result.solution:
            # FOUND SOLUTION => Change values
            print(result.statistics)
            time_sol = math.floor(int(result.statistics.get('time').total_seconds()))
            if time_sol < 300: optimal_sol = True
            obj_sol = int(result.objective)

            # Remove the repeated values from the solution (the repeated value is n+1 indicating the courier coming back to origin)
            for c in result.solution.routes: solution.append([item for item in c if c.count(item) == 1])

        # Create dictionary object
        json_dict = {
            f"{task.model}_{task.solver}": 
            {
                "time": time_sol,
                "optimal": optimal_sol,
                "obj": obj_sol,
                "sol": solution
            }
        }

        update_dict(data, f"{task.instance}", json_dict)

    return data


def update_dict(dict, key, value):
    """Update a dictionary of dictionaries. If the key exists, the value is used to update the inside dict.

    Args:
        dict (dict): dictionary to be updated
        key (string): key of the value we want to update
        value (dict): the dictionary that we want to insert
    """

    if key in dict:
        dict[key].update(value)
    else:
        dict[key] = value


def sort_dict(dict, dict_order):
    """Sorts a dictionary following an specified order of keys

    Args:
        dict (dict): dictionary we want to sort
        dict_order (list): list of ordered keys to follow

    Returns:
        dict: the sorted dictionary
    """
    return {key: dict[key] for key in dict_order}


def plot_results(results_folder):

    data_files = os.listdir(results_folder)
    n_files = len(data_files)

    times = []
    n_size = []
    model_name = 'CPdefinitive'

    for data_file, i in zip(data_files, range(1, n_files+1)):
        with open(results_folder+data_file, 'r') as file:
            data = json.load(file)

        times.append(data.get(model_name).get('time'))

        # Get m and n parameters from the results of the model
        m = len(data.get(model_name).get('sol'))
        n = m   # This is due to the fact tha n >= m
        # Look up for the maximum id of an item to figure out the n parameter
        for c in data.get(model_name).get('sol'):
            if max(c) > n: n = max(c)
        
        n_size.append(m*n)

    # Sort results by size of the problem (we define size as m*n)
    sorted_data = sorted(zip(n_size, times))
    sorted_n_size, sorted_times = zip(*sorted_data)

    # Plot results
    plt.plot(sorted_n_size, sorted_times)
    plt.show()


if __name__ == '__main__':

    # Define the options for our problem
    models_list = [
        'MCP',
        'MCPSymbreak',
        'MCPSymbreakImp'
    ]

    solvers_list = [
        'gecode',
        'chuffed'
    ]

    solved_instances = {
        'MCP_gecode':               {'solved' : True, 'p_size' : 1},
        'MCPSymbreak_gecode':       {'solved' : True, 'p_size' : 1},
        'MCPSymbreakImp_gecode':    {'solved' : True, 'p_size' : 1},
        'MCP_chuffed':              {'solved' : True, 'p_size' : 1},
        'MCPSymbreak_chuffed':      {'solved' : True, 'p_size' : 1},
        'MCPSymbreakImp_chuffed':   {'solved' : True, 'p_size' : 1},
    }

    data_folder = 'CP/test_data/'
    output_folder = 'res/CP/'

    data_files = os.listdir(data_folder)
    n_files = len(data_files)

    """
    #TODO: Implement concurrent solving => Substitude the p_size approach
    for data_file, id, i in zip(data_files, range(1, n_files+1), tqdm(range(n_files))):
        solution = {}

        # Calculate p_size for the actual instance
        data_filePath = Path(f"{data_folder}{data_file}")                 # Get the Path object (makes possible to parse with dzn)

        # Extract size of the problem (we define it as m*n)
        data = parse_dzn(data_filePath)
        m = list(data.values())[0]
        n = list(data.values())[1]
        p_size = m*n

        for solver in solvers_list:
            for model_name in models_list:

                # Default value (in case we do not solve the instance we fill with this)
                data = {
                    f"{model_name}_{solver}": 
                    {
                        "time": 300000,
                        "optimal": False,
                        "obj": None,
                        "sol": []
                    }
                }

                # We solve the problem if the previous problem was solved or if it had less or equal problem size
                if solved_instances[f'{model_name}_{solver}']['solved'] or solved_instances[f'{model_name}_{solver}']['p_size'] <= p_size:
                    output_file = f'{output_folder}{id}.json'
                    data, solved = solve(model_name, solver, f'{data_folder}{data_file}')   # Solve instance
                    solution.update(data)
                    
                    solved_instances[f'{model_name}_{solver}'].update({'solved': solved, 'p_size': p_size})


        # Write the results
        with open(output_file, 'w') as file:
            json.dump(solution, file, indent=4)
    """

    #plot_results('res/CP/')

    #asyncio.run(solve_instances(models_list, solvers_list, data_files, output_folder))
    result = solve(models_list[2], solvers_list[1], "CP/data/inst11.dzn")
    print(result)