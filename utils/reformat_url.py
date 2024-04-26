import re
import requests
from urllib.parse import urlparse


# Utility functions for URL validation and formatting

def is_url(url):
    """
    Checks if the string is a valid URL.

    Args:
        url (str): The string to check.

    Returns:
        bool: True if the string is a valid URL, False otherwise.
    """
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:A-Z0-9?\.)+'  # domain...
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # ...including TLD
        r'localhost|'  # localhost...
        r'(?::\d+)?'  # optional port
        r')(?:/?|[/?]\S+)$', re.IGNORECASE)  # rest of the URL
    return re.match(url_pattern, url) is not None


def is_domain(url):
    """
    Checks if the string is a valid domain.

    Args:
        url (str): The string to check.

    Returns:
        bool: True if the string is a valid domain, False otherwise.
    """
    domain_pattern = re.compile(
        r'^(?:a-zA-Z0-9?\.)+'  # subdomain...
        r'(?:[a-zA-Z]{2,}\.?)$', re.IGNORECASE)  # ...including TLD
    return re.match(domain_pattern, url) is not None


def is_ip(url):
    """
    Checks if the string is a valid IP address.

    Args:
        url (str): The string to check.

    Returns:
        bool: True if the string is a valid IP address, False otherwise.
    """
    ip_pattern = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'  # first three octets...
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')  # ...and the last one
    return re.match(ip_pattern, url) is not None


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

def remove_www(url):
    """
    Removes the 'www.' prefix from a URL if it's present.

    Args:
        url (str): The URL to format.

    Returns:
        str: The formatted URL without the 'www.' prefix.
    """
    # Remove 'www.' prefix if present
    if url.startswith("www."):
        url = url.replace("www.", "")

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
        url (str): The URL to extract the keyword from.

    Returns:
        str: The extracted keyword.
    """
    # First, extract the domain from the URL
    domain = extract_domain(domain)

    # Split the domain by dots and get the second to last element
    # This is because the last element is typically the TLD (e.g., 'com', 'cz')
    parts = domain.split('.')
    if len(parts) >= 2:
        keyword = parts[-2]  # This is typically the part just before the TLD
    else:
        keyword = domain  # In case the URL is something like 'localhost'

    # Return the keyword
    return keyword

