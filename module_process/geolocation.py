# Name: process_data.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Functions for adding geolocation on based of IP address.
# Python Version: 3.12.3


import ipinfo
from utils import load_config

# Instantiate an IPInfo object with your API token
handler = ipinfo.getHandler(load_config.load_credentials("ipinfo-access_token"))


def get_info(ip_address):
    """
    Get geolocation information for the given IP address using the IPInfo API.

    Args:
        ip_address (str): The IP address for which geolocation information is to be fetched.

    Returns:
        dict: A dictionary containing geolocation details such as region, country, city, latitude, and longitude.
              Returns None if geolocation information cannot be obtained.
    """
    try:
        details = handler.getDetails(ip_address)
        return {
            'Region': details.region,
            'Country': details.country,
            'City': details.city,
            'GPS - latitude': details.latitude,
            'GPS - longitude': details.longitude
        }
    except Exception as e:
        return None


def add_geolocation(json_data):
    """
    Add geolocation information to each IP address entry in the provided JSON data.

    Args:
        json_data (dict): JSON data containing IP addresses for which geolocation information is to be added.

    Returns:
        dict: The JSON data with geolocation information added to each IP address entry.
    """
    # Iterate over each website
    for filename, websites in json_data.items():
        # Iterate over each website in the file
        for website, details in websites.items():
            trace_hop_ips = details.get("Trace hop IP", {})

            # Iterate over each country
            for country, trace_ips in trace_hop_ips.items():
                # Check if trace_ips is a list (for BY)
                if isinstance(trace_ips, list):
                    # Iterate over each IP in the list
                    for ip_info in trace_ips:
                        ip_address = ip_info[0]
                        # Get geolocation information for the IP address
                        geolocation_data = get_info(ip_address)
                        # Add geolocation data to the IP info
                        ip_info.append(geolocation_data)

    return json_data

