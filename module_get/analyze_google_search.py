# Name: analyze_google_search.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Function for detecting manipulation with Google search.
# Python Version: 3.12.3


from googlesearch import search  # Import the googlesearch package for searching on Google
from utils import reformat_url  # Import reformat_url function from the utils module
from timeout_decorator import timeout  # Import the timeout decorator for setting execution timeout

function_timeout = 60  # Timeout value for function execution in seconds


def get_search_results(query):
    """
    Get search results from Google for a given query.

    Args:
        query (str): The search query.

    Returns:
        list: List of search results.
    """
    results = []

    for result in search(query, num=10, stop=10, pause=2):
        results.append(result)

    return results


@timeout(function_timeout)
def is_domain_in_results(address):
    """
    Check if a domain is present in the search results on Google.

    Args:
        address (str): The URL address to be checked.

    Returns:
        str: The result of the check - "Match" if the domain is found in the results, otherwise "No match".
    """
    try:
        domain = reformat_url.extract_domain(address)  # Extract the domain from the given URL
        keyword = reformat_url.get_keyword(domain)  # Get the keyword from the domain

        results = get_search_results(keyword)  # Get search results for the keyword

        if any(address in result for result in results):
            return "Match"

        return "No match"

    except TimeoutError:
        print("Resolver identification test exceeded timeout.")
        return "N/A"
