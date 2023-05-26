import subprocess
import os

def solve(model, solver, data, output_file):
    """Generates a bash command to run the minizinc programm in base of an specified model, solver and data.

    Args:
        model (String): path to the file containing the model to be used for solving the problem
        solver (String): solver to be used for solving the problem
        data (String): path to the data file containing the instance to be solved
        output_file (String): path to the file where to write the output results
    """

    cmd = f'minizinc --solver {solver} {model} {data} -t 300000 --statistics --json-stream --output-time'  # Bash command

    # Open output file and run the bash command
    with open(output_file, 'w') as file:
        subprocess.run(args=cmd.split(), stdout=file)

if __name__ == '__main__':

    # Define the options for our problem
    model_file = 'CP/src/CPdefinitive.mzn'
    solver = 'Gecode'
    data_folder = 'CP/data/'
    output_folder = 'res/CP/'

    data_files = os.listdir(data_folder)
    n_files = len(data_files)

    for data_file, i in zip(data_files, range(1, n_files+1)):
        output_file = f'{output_folder}{i}.json'
        solve(model_file, solver, f'{data_folder}{data_file}', output_file)   # Solve instance