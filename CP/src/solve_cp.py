import os
import json

from datetime import timedelta
from minizinc import Instance, Model, Solver

def solve(model_name, solver, data, output_file):
    """Solve the minizinc model given a selected solver, data file (.dzn) and write results
    to an output_file

    Args:
        model_name (str): name of the model to be use to solve the instance
        solver (str): choosen solver to solve the instance
        data (str): data file containing the instance of the problem
        output_file (str): name of the file to write the solution
    """

    model = Model(f"CP/src/{model_name}.mzn")   # Load model from the file
    gecode = Solver.lookup(solver)              # Look for the configuration of gecode solver
    
    instance = Instance(gecode, model)          # Create instance of the problem
    instance.add_file(data)                     # Add the data to the instance

    # Solve instance (set a timeout of 300000 microseconds)
    result = instance.solve(timeout=timedelta(300000))

    # Set the optimal_sol parameter depending on the status of solution
    optimal_sol = False
    if str(result.status) == 'OPTIMAL_SOLUTION': optimal_sol = True 

    # Format the solution (remove repeated values)
    solution = result.solution.routes
    formatted_solution = []
    for c in solution:
        formatted_solution.append([item for item in c if c.count(item) == 1])

    # Create dictionary object (dump it to json)
    data = {
        f"{model_name}": 
        {
            "time": int(result.statistics.get('time').total_seconds()*1000),
            "optimal": optimal_sol,
            "obj": int(result.objective),
            "sol": str(formatted_solution)
        }
    }

    # Write the results
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == '__main__':

    # Define the options for our problem
    model_name = 'CPdefinitive'
    solver = 'gecode'
    data_folder = 'CP/data/'
    output_folder = 'res/CP/'

    data_files = os.listdir(data_folder)
    n_files = len(data_files)

    for data_file, i in zip(data_files, range(1, n_files+1)):
        output_file = f'{output_folder}{i}.json'
        solve(model_name, solver, f'{data_folder}{data_file}', output_file)   # Solve instance