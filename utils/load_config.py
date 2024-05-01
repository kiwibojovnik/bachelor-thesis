# Name: load_config.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Function for loading necessary information for configuration.
# Python Version: 3.12.3


# Import necessary libraries
import json  # Import JSON module for JSON operations


def load_credentials(credentials_type):
    """
    Load credentials from a JSON configuration file.

    Args:
        credentials_type (str): Type of credentials to load from the configuration.

    Returns:
        str: Retrieved credential value.
    """
    with open(f'config.json') as f:
        config_data = json.load(f)  # Load JSON data from the file

    return config_data[credentials_type]