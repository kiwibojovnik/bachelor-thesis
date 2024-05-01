# Name: save_to_JSON.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: March 5, 2024
# Description: Saving data into JSON file.
# Python Version: 3.12.3

# Import necessary libraries
import json  # Import JSON module for JSON operations
from requests.structures import CaseInsensitiveDict  # Import CaseInsensitiveDict from requests.structures


def convert_to_dict(case_insensitive_dict):
    """
    Converts CaseInsensitiveDict to a standard dictionary.

    Args:
        case_insensitive_dict (CaseInsensitiveDict): Input CaseInsensitiveDict to be converted.

    Returns:
        dict: Standard dictionary.
    """
    if isinstance(case_insensitive_dict, CaseInsensitiveDict):
        return dict(case_insensitive_dict)
    return case_insensitive_dict


def save_test_results(test_results, filename):
    """
    Save test results to a JSON file.

    Args:
        test_results (list): List of test results, each containing a dictionary.
        filename (str): Name of the file to save the results.
    """
    results_dict = {}
    for result in test_results:
        if result is not None:
            results_dict[result['URL']] = {k: convert_to_dict(v) for k, v in result.items()}

    # Save results to a JSON file
    with open(filename, 'w') as file:
        json.dump(results_dict, file, indent=4)  # Indent for better readability
