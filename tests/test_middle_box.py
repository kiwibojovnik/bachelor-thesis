# -*- coding: utf-8 -*-
import requests

from utils import reformat_url
from timeout_decorator import timeout


function_timeout = 60


@timeout(function_timeout)
def http_header_manipulation(url):
    detector = "Manipulated"

    headers = {
        "UsEr-AgEnT": "MoZiLLa/5.0 (WinDoWW NT 10.0; Win64; x64) AppleWEbKIT/537.36 (KHTML, like GeCko) "
                      "ChROmE/58.0.3029.110 SaFAri/537.3"
    }

    try:
        response = requests.get(reformat_url.add_http(url), headers=headers)
        original_headers = {key.lower(): value for key, value in headers.items()}
        received_headers = {key.lower(): value for key, value in response.request.headers.items()}

        # Procházení poslaných hlaviček a porovnání pouze s těmi, které byly přijaty
        for key, value in original_headers.items():
            if key in received_headers and received_headers[key] == value:
                detector = "No manipulation"

        return detector


    except TimeoutError:
        print("Resolver identification test exceeded timeout.")
        return "N/A", "N/A"

    except requests.exceptions.RequestException as e:
        print(f"Error occurred during HTTP header manipulation test.")
        return "N/A"


@timeout(function_timeout)
def invalid_request_line(url):
    invalid_methods = ['FOO', 'BAR', 'BAZ', 'QUX']
    manipulation_score = 0

    try:
        for method in invalid_methods:
            response = requests.request(method, reformat_url.add_http(url))

            if response.status_code == 400:
                manipulation_score += 1

        score = manipulation_score / len(invalid_methods)
        return score


    except TimeoutError:
        print("Resolver identification test exceeded timeout.")
        return "N/A", "N/A"

    except requests.exceptions.RequestException as e:
        print(f"Error occurred during invalid request line test.")
        return "Fail"
