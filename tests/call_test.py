from datetime import datetime
import os
import time
from requests.structures import CaseInsensitiveDict
from tests import tests_IPv6, test_middle_box
from utils import reformat_url


class WebConnectivityTester:
    def __init__(self, url_list, output_content_folder, address):
        """
        Initializes the WebConnectivityTester.

        Args:
            url_list (list): List of URLs to test.
            output_content_folder (str): Folder where HTML content will be saved.
            address (str): Preferred Ip address (IPv4 or IPv6)
        """
        self.urls = url_list
        self.output_content_folder = output_content_folder
        self.address = address

    def save_html_content(self, filename, content):
        """
        Saves HTML content to a file.

        Args:
            filename (str): Name of the output file.
            content (str): HTML content to save.
        """
        # Create the output folder if it doesn't exist
        os.makedirs(self.output_content_folder, exist_ok=True)

        with open(os.path.join(self.output_content_folder, filename), 'w', encoding='utf-8') as content_file:
            content_file.write(content)

    def test_website(self, website):
        """
        Tests a website for connectivity.

        Args:
            website (str): The website URL to test.

        Returns:
            CaseInsensitiveDict: A dictionary containing test results.
        """
        print(f"Testing {website}...")
        try:
            start_time = time.time()
            resolver_ip = tests_IPv6.resolver_identification()
            dns_result = tests_IPv6.dns_lookup(website)

            if dns_result[0] == "OK":
                ip_address = dns_result[1][0]
                tcp_result = tests_IPv6.tcp_handshake(ip_address)
                ping_result = tests_IPv6.ping_test(ip_address)
                trace_hop = tests_IPv6.perform_trace(ip_address)
                redirect = tests_IPv6.detect_redirect(website)
                http_status, content_length, headers, html_content = tests_IPv6.http_get_request(website)
                certificate = tests_IPv6.get_https_certificate(ip_address, website)

                end_time = time.time()
                duration = round(end_time - start_time, 2)
                output_content = reformat_url.remove_http(website) + '_content.html'
                self.save_html_content(output_content, html_content)

                middle_box_header = test_middle_box.http_header_manipulation(website)
                middle_box_request_score, middle_box_request_attempts = test_middle_box.invalid_request_line(website)

                return CaseInsensitiveDict({
                    'Time': duration,
                    'URL': str(website),
                    'Resolver Status': resolver_ip[0],
                    'Resolver IP': resolver_ip[1],
                    'DNS Status': dns_result[0],
                    'DNS IPs': dns_result[1],
                    'TCP Status': tcp_result[0],
                    'TCP Remote IP': tcp_result[1],
                    'PING Status': ping_result[0],
                    'PING IP': ping_result[1],
                    'Trace hop IP': trace_hop,
                    'Redirected Status': redirect[0],
                    'Redirected Location': redirect[1],
                    'HTTP Status': http_status,
                    'Content Length': content_length,
                    'Headers': headers,
                    'HTML Content': output_content,
                    'Cert Status': certificate[0],
                    'Cert Content': certificate[1],
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Http header manipulation': middle_box_header,
                    'Invalid request manipulation score': middle_box_request_score,
                    'Invalid request manipulation attempts': middle_box_request_attempts
                })

        except Exception as e:
            print(f"Error testing {website}: {e}")
            return {
                'URL': str(website),
                'Error': str(e)
            }

    def run_tests(self):
        """
        Runs connectivity tests for all specified URLs.

        Returns:
            list: A list of dictionaries containing test results.
        """
        results = []
        for website in self.urls:
            results.append({'URL': str(website)})
            results.append(self.test_website(website))

        return results
