from pulp import *
from models import *
from utils import *
from pulp.apis import *
from datetime import timedelta
from tqdm import tqdm

# CONSTANTS
DEFAULT_TIMEOUT = timedelta(seconds=300)
DATA_FOLDER = 'test_data/'
RES_FOLDER = 'res/MIP/'

if __name__ == "__main__":
    
    models_list = [
        "MCP",
        "MCPSymbreakImp"
    ]

    data_files = os.listdir(DATA_FOLDER)

    for data_file, i in zip(data_files, tqdm(range(len(data_files)))):

        # READ PARAMETERS
        parameters = parse_file(f"{DATA_FOLDER}{data_file}")
        m,n,_,_,_ = parameters

        data = {}
        for model_name in models_list:

            # BUILD MODEL
            model, routes = build_model(model_name, parameters)

            # SOLVE THE PROBLEM
            results = solve_model(model, routes, parameters)
            data.update({f"{model_name}": results})
        
        # WRITE RESULTS
        write_results(data, f"res/MIP/{data_file[4:6]}.json")