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
        for method in invalid_methods:
            if method == 'GET':
                invalid_request = f"{method} / HTTP/99.9\r\nHost: {self.url}\r\n\r\n"
            elif method == 'HEAD':
                invalid_request = f"{method} / HTTP/99.9\r\nHost: {self.url}\r\n\r\n"
            else:
                invalid_request = f"{method} / HTTP/1.1\r\nHost: {self.url}\r\n\r\n"
            print(f"\nSending invalid HTTP request line:")
            print(invalid_request)

            try:
                response = requests.request('GET', self.url, data=invalid_request)
                print("\nReceived response:")
                print(response.text)

                if response.status_code == 400:
                    print("\nHTTP manipulation detected.")
                else:
                    print("\nNo error received. No HTTP manipulation detected.")

            except requests.exceptions.RequestException as e:
                print(f"\nError received: {e}. HTTP manipulation detected.")