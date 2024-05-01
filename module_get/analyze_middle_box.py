# Name: analyze_middle_box.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Functions for analyzing middle boxs presence in network.
# Python Version: 3.12.3


# Import necessary libraries
import requests  # Import requests module for making HTTP requests
from utils import reformat_url  # Import reformat_url function from the utils module
from timeout_decorator import timeout  # Import the timeout decorator for setting execution timeout

function_timeout = 60  # Timeout value for function execution in seconds


@timeout(function_timeout)
def http_header_manipulation(url):
    """
    Check for HTTP header manipulation by sending a request with modified headers.

    Args:
        url (str): The URL to test.

    Returns:
        str: "Manipulated" if HTTP header manipulation is detected, otherwise "No manipulation".
    """
    detector = "Manipulated"  # Default value for the manipulation detector

    # Define custom headers for the HTTP request
    headers = {
        "UsEr-AgEnT": "MoZiLLa/5.0 (WinDoWW NT 10.0; Win64; x64) AppleWEbKIT/537.36 (KHTML, like GeCko) "
                      "ChROmE/58.0.3029.110 SaFAri/537.3"
    }

    try:
        # Send a GET request with custom headers to the specified URL
        response = requests.get(reformat_url.add_http(url), headers=headers)

        # TODO: je to dobře?
        # Convert original and received headers to lowercase for comparison
        original_headers = {key.lower(): value for key, value in headers.items()}
        received_headers = {key.lower(): value for key, value in response.request.headers.items()}

        # Iterate through sent headers and compare with received ones
        for key, value in original_headers.items():
            if key in received_headers and received_headers[key] == value:
                detector = "No manipulation"  # If the received header matches the sent one, no manipulation is detected

        return detector

    except TimeoutError:
        print("Resolver identification test exceeded timeout.")
        return "N/A"

    except requests.exceptions.RequestException as e:
        print(f"Error occurred during HTTP header manipulation test.")
        return "N/A"


@timeout(function_timeout)
def invalid_request_line(url):
    """
    Check for invalid request line by sending requests with invalid HTTP methods.

    Args:
        url (str): The URL to test.

    Returns:
        float: The manipulation score indicating the proportion of requests resulting in 400 Bad Request status.
    """
    invalid_methods = ['FOO', 'BAR', 'BAZ', 'QUX']  # List of invalid HTTP methods
    manipulation_score = 0  # Initialize manipulation score counter

    try:
        # Iterate through invalid methods and send requests with each method
        for method in invalid_methods:
            response = requests.request(method, reformat_url.add_http(url))

            # If the response status code is 400 Bad Request, increment manipulation score
            if response.status_code == 400:
                manipulation_score += 1

        # Calculate manipulation score as the proportion of requests resulting in 400 status code
        score = manipulation_score / len(invalid_methods)
        return score

    except TimeoutError:
        print("Resolver identification test exceeded timeout.")
        return "N/A"

    except requests.exceptions.RequestException as e:
        print(f"Error occurred during invalid request line test.")
        return "Fail"
