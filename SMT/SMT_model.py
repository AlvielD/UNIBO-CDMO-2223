from z3 import *
from utils import *
from models import *
import json

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


if __name__ == "__main__":

    models_list = [
        "MCP",
        "MCPSymbreak",
        "MCPSymbreakImp"
    ]

    data_folder = 'test_data/'
    data_files = os.listdir(data_folder)

    for data_file in data_files:

        # READ PARAMETERS
        #file_path = "data/inst02.dat"
        parameters = parse_file(f"data/{data_file}")
        m, n, _, _, _ = parameters

        data = {}
        # TODO: Perform concurrent solving
        for model_name in models_list:

            # BUILD THE MODEL
            solver, routes, maximum = build_model(parameters, model_name)

            # SOLVE THE MODEL
            results = solve_model(solver, routes, maximum, parameters, model_name)
            update_dict(data, model_name, results.get(model_name))

        # WRITE THE RESULTS
        write_results(data, f"res/SMT/{data_file[4:6]}.json")