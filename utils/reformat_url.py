# Name: reformat_url.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Necessary functions for refomrating input URLs and extracting domains.
# Python Version: 3.12.3


# Import necessary libraries
from urllib.parse import urlparse  # Import urlparse function from urllib.parse module


def add_http(url):
    """
    Adds 'http://' prefix to the URL if it's missing.

    Args:
        url (str): The URL to format.

    Returns:
        str: The formatted URL with 'http://' prefix.
    """
    if not url.startswith("http"):
        url = "http://" + url
    return url


def extract_domain(url):
    """
    Extracts the domain from a URL, ensuring it returns only the domain without any paths or parameters.

    Args:
        url (str): The URL to extract the domain from.

    Returns:
        str: The extracted domain.
    """
    # Add scheme if missing
    if not urlparse(url).scheme:
        url = '//' + url

    # Parse the URL to extract the netloc part which contains the domain
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # Remove any port number if present (e.g., www.example.com:80 -> www.example.com)
    domain = domain.split(':')[0]

    # Return the domain
    return domain


def get_keyword(domain):
    """
    Uses the extract_domain function to get the keyword from a domain.
    For example, from 'www.golos3524.cz' it would extract 'golos3524'.

    Args:
        domain (str): The domain to extract the keyword from.

    Returns:
        str: The extracted keyword.
    """
    # First, extract the domain from the URL
    domain = extract_domain(domain)

    # Split the domain by dots and get the second to last element
    # This is because the last element is typically the TLD (e.g., 'com', 'cz')
    parts = domain.split('.')
    if len(parts) >= 2:
        keyword = parts[-2]
    else:
        keyword = domain  # In case the URL is something like 'localhost'

    return keyword
