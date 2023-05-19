import subprocess


def solve(model, solver, data, output_file):
    """Generates a bash command to run the minizinc programm in base of an specified model, solver and data.

    Args:
        model (String): path to the file containing the model to be used for solving the problem
        solver (String): solver to be used for solving the problem
        data (String): path to the data file containing the instance to be solved
        output_file (String): path to the file where to write the output results
    """

    cmd = f'minizinc --solver {solver} {model} {data} --json-stream --output-time'  # Bash command

    # Open output file and run the bash command
    with open(output_file, 'w') as file:
        subprocess.run(args=cmd.split(), stdout=file)


if __name__ == '__main__':

    # Define the options for our problem
    model_file = 'CP/src/CPdefinitive.mzn'
    solver = 'Gecode'
    data_file = 'CP/data/instance_1.dzn'
    output_file = 'results/CP/results.json'

    solve(model_file, solver, data_file, output_file)   # Solve instance