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


def remove_http(url):
    """
    Removes 'http://' or 'https://' prefix from the URL.

    Args:
        url (str): The URL to format.

    Returns:
        str: The URL without the 'http://' or 'https://' prefix.
    """
    if url.startswith("http://"):
        url = url[len("http://"):]
    elif url.startswith("https://"):
        url = url[len("https://"):]
    return url
