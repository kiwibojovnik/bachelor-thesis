# Name: statistics.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Retrieving statistics bout data.
# Python Version: 3.12.3


def count_censorship_types(data):
    """
    Counts the occurrences of different censorship types in the provided data.

    Args:
        data (dict): Dictionary containing test results data.

    Returns:
        dict: Dictionary containing censorship type counts.
    """
    censorship_stats = {}  # Dictionary to store censorship type counts

    # Iterate through each file and its data
    for file_name, file_data in data.items():
        # Iterate through each URL and its data
        for url, url_data in file_data.items():
            # Get censorship type from URL data, default to "No censorship found" if not present
            censorship_type = url_data.get("CENSORSHIP TYPE", "No censorship found")
            # Update censorship type count in the dictionary
            censorship_stats[censorship_type] = censorship_stats.get(censorship_type, 0) + 1

    return censorship_stats
