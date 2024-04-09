import requests
import random
import string


class CensorshipDetector:
    def __init__(self, url):
        self.url = url



    def http_header_manipulation(self):
        headers = {
            "UsEr-AgEnT": "MoZiLLa/5.0 (WinDoWW NT 10.0; Win64; x64) AppleWEbKIT/537.36 (KHTML, like GeCko) ChROmE/58.0.3029.110 SaFAri/537.3"
        }

        response = requests.get(self.url, headers=headers)
        original_headers = {key.lower(): value for key, value in headers.items()}
        received_headers = {key.lower(): value for key, value in response.request.headers.items()}

        print("\nOriginal headers sent:")
        print(original_headers)

        print("\nReceived headers:")
        print(received_headers)

        # Procházení poslaných hlaviček a porovnání pouze s těmi, které byly přijaty
        for key, value in original_headers.items():
            if key in received_headers and received_headers[key] == value:
                print(f"\nHeader '{key}' matches.")
            else:
                print(f"\nHeader '{key}' does not match. HTTP header manipulation detected.")
                return

        print("\nNo HTTP header manipulation detected.")

    def invalid_request_line(self):
        invalid_methods = ['FOO', 'BAR', 'BAZ', 'QUX']
        manipulation_count = 0

        for method in invalid_methods:
            try:
                response = requests.request(method, self.url)

                if response.status_code == 400:
                    manipulation_count += 1

            except requests.exceptions.RequestException:
                manipulation_count += 1

        return manipulation_count, len(invalid_methods)


detector = CensorshipDetector("https://linkedin.com")
detector.http_header_manipulation()

print(detector.invalid_request_line())
