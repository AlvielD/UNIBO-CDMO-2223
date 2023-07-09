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