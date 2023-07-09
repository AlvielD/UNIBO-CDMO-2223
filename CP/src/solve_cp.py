import os
import subprocess
from time import time
from datetime import timedelta

DEFAULT_TIMEOUT = timedelta(seconds=300)

def solve_instance(model, solver, data_file):

    out_file = f"res/CP/{data_file[4:6]}.json"
    model_path = f"CP/src/{model}.mzn"
    data_file_path = f"CP/test_data/{data_file}"

    cmd = f"minizinc --output-mode json --output-to-file {out_file} --solver {solver} -t {DEFAULT_TIMEOUT} {model_path} {data_file_path}"
    s_time = time()
    subprocess.run(cmd.split())
    e_time = time()
    time_sol = e_time-s_time




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