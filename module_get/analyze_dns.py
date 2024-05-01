# Name: analyze_dns.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Functions for detection manipulation with DNS:
# Python Version: 3.12.3


# Import necessary libraries
import dns.resolver  # Import the DNS resolver module for DNS resolution
from utils import reformat_url  # Import the reformat_url function from the utils module
from timeout_decorator import timeout  # Import the timeout decorator for setting execution timeout

function_timeout = 60  # Timeout value for function execution in seconds


@timeout(function_timeout)
def detect_dns_repeated_query(address):
    """
    Detects repeated DNS queries to identify potential DNS manipulation.

    Args:
        address (str): The URL address to be checked.

    Returns:
        str: The result of the detection - "Manipulate" if DNS attack is detected, otherwise "No manipulation".
    """
    domain = reformat_url.extract_domain(address)

    try:
        resolver = dns.resolver.Resolver()  # Create a resolver object for DNS resolution

        # First query for a non-existent hostname
        resolver.resolve(domain, 'A')
        return "No manipulation"  # If no error is raised, no attack is detected

    except dns.resolver.NXDOMAIN:
        try:
            # Repeated query for the same non-existent hostname
            resolver.resolve(domain, 'A')
            return "Manipulate"  # If NXDOMAIN is returned, an attack is detected
        except dns.resolver.NXDOMAIN:
            return "No manipulation"  # If NXDOMAIN is returned again, no attack is detected
        except Exception as e:
            print("Error during the second query:", e)
            return "No manipulation"  # In case of any other exception, assume no attack

    except TimeoutError:
        print("Resolver identification test exceeded timeout.")
        return "N/A"

    except Exception as e:
        print("Error detecting repeated DNS query:", e)
        return "No manipulation"


@timeout(function_timeout)
def detect_dns_hijacking(address):
    """
    Detects DNS hijacking by querying an existing hostname.

    Args:
        address (str): The URL address to be checked.

    Returns:
        str: The result of the detection - "Manipulate" if DNS hijacking is detected, otherwise "No manipulation".
    """
    domain = reformat_url.extract_domain(address)

    try:
        resolver = dns.resolver.Resolver()  # Create a resolver object for DNS resolution

        # Query an existing hostname, censored DNS server should return an unexpected or no response
        answers = resolver.resolve(domain, 'A')
        if answers:
            return "No manipulation"  # If a valid response is received, no attack is detected
        else:
            return "Manipulate"  # If no response is received, a possible attack is detected
    except dns.resolver.NoAnswer:
        return True  # If no response is received, a possible attack is detected

    except TimeoutError:
        print("Resolver identification test exceeded timeout.")
        return "N/A"

    except Exception as e:
        print("Error detecting DNS hijacking:", e)
        return "No manipulation"
