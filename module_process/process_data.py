# Name: process_data.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Necessary functions for refomrating input URLs and extracting domains.
# Python Version: 3.12.3


# Import necessary libraries
import os  # Module for interacting with the operating system
import json  # Module for working with JSON data
import re  # Module for regular expressions

from module_process import compare_data, define_censorship, geolocation, statistics  # Custom modules for data processing


def match_filename(filename1, filename2):
    """
    Checks if two filenames match based on a specific pattern.

    Args:
        filename1 (str): The first filename.
        filename2 (str): The second filename.

    Returns:
        bool: True if filenames match, False otherwise.
    """
    pattern = r"results_([a-zA-Z\d]+_\d+)_.*\.json"

    match_pattern1 = re.match(pattern, filename1)
    match_pattern2 = re.match(pattern, filename2)

    if match_pattern1 and match_pattern2:
        country_identifier1 = match_pattern1.group(1)
        country_identifier2 = match_pattern2.group(1)

        # Split the country and number to compare them separately
        country1, number1 = country_identifier1.split('_')
        country2, number2 = country_identifier2.split('_')

        # Check if both the country and number match
        if country1 == country2 and number1 == number2:
            return True
    return False


def process_two_files(folder1, folder2):
    """
    Processes two folders containing JSON files.

    Args:
        folder1 (str): Path to the first folder.
        folder2 (str): Path to the second folder.

    Returns:
        tuple: A tuple containing diffs dictionary, total count of different keys, total count of same keys,
               and total count of failed address records.
    """
    diffs = {}
    different_keys_count_total = 0
    same_keys_count_total = 0
    fail_address_records_total = 0

    for file1 in os.listdir(folder1):
        for file2 in os.listdir(folder2):
            if match_filename(file1, file2):
                # Load JSON data from both files
                with open(os.path.join(folder1, file1), 'r', encoding='utf-8', errors='replace') as f1, \
                        open(os.path.join(folder2, file2), 'r', encoding='utf-8', errors='replace') as f2:
                    json_data1 = json.load(f1)
                    json_data2 = json.load(f2)

                    fail_address_records = compare_data.count_keys_with_no_results(json_data1, json_data2)

                    # Find differences
                    diff_single, different_keys_count, same_keys_count = compare_data.compare_files(json_data1, json_data2)

                # Add differences to diffs dictionary
                diffs[file1] = diff_single
                different_keys_count_total += different_keys_count
                same_keys_count_total += same_keys_count
                fail_address_records_total += fail_address_records

    return diffs, different_keys_count_total, same_keys_count_total, fail_address_records_total


def run_processing_data(folder1, folder2):
    """
    Run processing data from two folders.

    Args:
        folder1 (str): Path to the first folder.
        folder2 (str): Path to the second folder.
    """
    # Find differences in each test
    print("Finding differences in each test.")
    diffs, different_keys_count_total, same_keys_count_total, fail_address_records_total = process_two_files(folder1,
                                                                                                             folder2)

    # Save differences to a file
    with open('clean_diff.json', 'w') as diff_file1:
        json.dump(diffs, diff_file1, ensure_ascii=False, indent=4)

    print("\nDefinition of censorship type.")
    # Define censorship type based on test failures
    diffs = define_censorship.add_censorship_type_to_differences(diffs)

    print("Adding geolocation information to traceroute data.")
    # TODO: Implement: Get GPS location for specific IP addresses in traceroute data, possibly only for those from Belarus
    diffs = geolocation.add_geolocation(diffs)

    stats = statistics.count_censorship_types(diffs)

    print("Printing statistics about censorship: ")

    # Print statistics about censorship
    print("The number of different tests for website addresses: ", different_keys_count_total)
    print("The number of identical results for addresses: ", same_keys_count_total)
    print("The number of failed addresses (not working in CZ): ", fail_address_records_total)

    for censorship_type, count in stats.items():
        print(f"- {censorship_type}: {count} occurrences")

    print("Saving results of each test with additional information to file.")
    # Save differences to a file
    with open('try2.json', 'w') as diff_file:
        json.dump(diffs, diff_file, ensure_ascii=False, indent=4)
