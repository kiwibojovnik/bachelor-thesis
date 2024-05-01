# Name: compare_data.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Comparing datas from two files and retrieving the differeents.
# Python Version: 3.12.3


# Import necessary libraries
import json  # Module for working with JSON data


def count_keys_with_no_results(data1, data2):
    """
    Count the keys in data1 that have no corresponding key in data2.

    Args:
        data1 (dict): First dataset.
        data2 (dict): Second dataset.

    Returns:
        int: Number of keys in data1 with no corresponding key in data2.
    """
    keys_with_no_results_count = 0

    for url, details1 in data1.items():
        if url in data2:
            details2 = data2[url]
            for key in details1:
                if key not in details2:
                    keys_with_no_results_count += 1

    return keys_with_no_results_count


def filter_details(details, ignore_keys):
    """
    Filter details dictionary by ignoring specified keys.

    Args:
        details (dict): Details dictionary to filter.
        ignore_keys (list): List of keys to ignore.

    Returns:
        dict: Filtered details dictionary.
    """
    return {key: value for key, value in details.items() if key not in ignore_keys}


def compare_headers(headers1, headers2, ignore_header_items):
    """
    Compare headers from two datasets.

    Args:
        headers1 (dict): Headers from the first dataset.
        headers2 (dict): Headers from the second dataset.
        ignore_header_items (list): List of header items to ignore.

    Returns:
        dict: Differences between headers from two datasets.
    """
    differences = {}

    for header_key in list(headers1):  # Convert to list to avoid RuntimeError
        if header_key in ignore_header_items or header_key not in headers2:
            continue
        # Deserialize JSON strings if present
        if isinstance(headers1[header_key], str) and headers1[header_key].startswith('{'):
            try:
                headers1[header_key] = json.loads(headers1[header_key])
            except json.JSONDecodeError:
                print(f"Warning: Error decoding JSON from headers1['{header_key}']")
                continue
        if isinstance(headers2[header_key], str) and headers2[header_key].startswith('{'):
            try:
                headers2[header_key] = json.loads(headers2[header_key])
            except json.JSONDecodeError:
                print(f"Warning: Error decoding JSON from headers2['{header_key}']")
                continue
        # Compare header values
        if headers1[header_key] != headers2[header_key]:
            differences[header_key] = {'CZ': headers1[header_key], 'BY': headers2[header_key]}

    return differences


def compare_files(data1, data2, ignore_keys=None, ignore_header_items=None):
    """
    Compare two datasets and find differences.

    Args:
        data1 (dict): First dataset.
        data2 (dict): Second dataset.
        ignore_keys (list, optional): Keys to ignore during comparison.
        ignore_header_items (list, optional): Header items to ignore during comparison.

    Returns:
        tuple: Differences between datasets, count of sites with differences, count of sites without differences.
    """
    if ignore_keys is None:
        ignore_keys = ['Time', 'Timestamp', 'HTML Content']
    if ignore_header_items is None:
        ignore_header_items = []

    differences = {}
    url_in_data = 0
    different_sites_count = 0
    same_sites_count = 0

    for url, details1 in data1.items():
        if url in data2:
            url_in_data += 1
            details2 = data2[url]
            details1_filtered = filter_details(details1, ignore_keys)
            details2_filtered = filter_details(details2, ignore_keys)

            headers_differences = {}
            if 'Headers' in details1_filtered and 'Headers' in details2_filtered:
                headers1 = details1_filtered['Headers']
                headers2 = details2_filtered['Headers']
                if not isinstance(headers1, dict):
                    continue

                headers_differences = compare_headers(headers1, headers2, ignore_header_items)

            # Compare the remaining keys
            key_differences = False
            for key in details1_filtered:
                if key == 'Headers' or key not in details2_filtered:
                    continue
                if details1_filtered[key] != details2_filtered[key]:
                    if url not in differences:
                        differences[url] = {}
                    differences[url][key] = {'CZ': details1_filtered[key], 'BY': details2_filtered[key]}
                    key_differences = True

            if headers_differences or key_differences:
                if url not in differences:
                    differences[url] = {}
                if headers_differences:
                    differences[url]['Headers'] = headers_differences
                different_sites_count += 1
            else:
                same_sites_count += 1

    return differences, different_sites_count, same_sites_count
