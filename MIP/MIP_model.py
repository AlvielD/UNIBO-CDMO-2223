from pulp import *
from models import *
from utils import *
from pulp.apis import *

if __name__ == "__main__":
    
    models_list = [
        "MCP",
        "MCPSymbreak",
        "MCPSymbreakImp"
    ]

    data_folder = "test_data/"
    data_files = os.listdir(data_folder)

    for data_file in data_files:

        # READ PARAMETERS
        parameters = parse_file(f"data/{data_file}")
        m, n, _, _, _ = parameters

        data = {}

        for model_name in models_list:

            # BUILD MODEL
            model, routes = build_model(model_name, parameters)

            # SOLVE THE PROBLEM
            results = solve_model(model, routes, parameters)
            data.update({f"{model_name}": results})
        
        # WRITE RESULTS
        write_results(data, f"res/MIP/{data_file[4:6]}.json")