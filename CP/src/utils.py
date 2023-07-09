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