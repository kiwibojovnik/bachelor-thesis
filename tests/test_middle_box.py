import requests
import random
import string


def http_header_manipulation(website):
    headers = {
        "UsEr-AgEnT": "MoZiLLa/5.0 (WinDoWW NT 10.0; Win64; x64) AppleWEbKIT/537.36 (KHTML, like GeCko) ChROmE/58.0.3029.110 SaFAri/537.3"
    }

    try:
        response = requests.get("https://" + website, headers=headers)
        original_headers = {key.lower(): value for key, value in headers.items()}
        received_headers = {key.lower(): value for key, value in response.request.headers.items()}

        # Procházení poslaných hlaviček a porovnání pouze s těmi, které byly přijaty
        for key, value in original_headers.items():
            if key in received_headers and received_headers[key] == value:
                detector = "No manipulation"
            else:
                detector = "Manipulated"

        return {
            'URL': str(website),
            'http_header_manipulation': detector
        }

    except requests.exceptions.RequestException as e:
        print(f"Error occurred during HTTP header manipulation test for {website}: {e}")
        return {
            'URL': str(website),
            'http_header_manipulation': 'Error'
        }


def invalid_request_line(website):
    invalid_methods = ['FOO', 'BAR', 'BAZ', 'QUX']
    manipulation_count = 0

    try:
        for method in invalid_methods:
            response = requests.request(method, 'https://'+website)

            if response.status_code == 400:
                manipulation_count += 1

        return {
            'URL': str(website),
            'Invalid_request_line score': manipulation_count,
            'Invalid_request_line test count ': len(invalid_methods)
        }

    except requests.exceptions.RequestException as e:
        print(f"Error occurred during invalid request line test for {website}: {e}")
        return {
            'URL': str(website),
            'Invalid_request_line score': 'Error',
            'Invalid_request_line test count ': len(invalid_methods)
        }


class CensorshipDetector:
    def __init__(self, batch):
        self.batch = batch

    @property
    def run_tests(self):
        results = []
        for website in self.batch:
            results.append({'URL': str(website)})
            results.append(invalid_request_line(website))
            results.append(http_header_manipulation(website))

        return results
