from z3 import *
import json

def write_results(results, output_file):
    # Write the results
    with open(output_file, 'w') as file:
        json.dump(results, file, indent=4)

def z3_max(vector):
    maximum = vector[0]
    for value in vector[1:]:
        maximum = If(value > maximum, value, maximum)
    return maximum

def z3_min(vector, n):
    minimum = vector[0]
    for i in range(1,n):
        value = vector[i]
        minimum = If(value < minimum, value, minimum)
    return minimum

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