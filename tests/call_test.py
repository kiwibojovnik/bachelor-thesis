from datetime import datetime
import os
import time
from requests.structures import CaseInsensitiveDict
from tests import tests_IPv6
from utils import reformat_url


class WebConnectivityTester:
    def __init__(self, url_list, output_content_folder, ip_type):
        """
        Initializes the WebConnectivityTester.

        Args:
            url_list (list): List of URLs to test.
            output_content_folder (str): Folder where HTML content will be saved.
            ip_type (str): Preferred Ip address (IPv4 or IPv6)
        """
        self.urls = url_list
        self.output_content_folder = output_content_folder
        self.ip_type = ip_type

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

    def test_website(self, address):
        """
        Tests a website for connectivity.

        Args:
            address (str): The website URL to test.

        Returns:
            CaseInsensitiveDict: A dictionary containing test results.
        """
        print(f"Testing {address}...")
        try:
            start_time = time.time()
            resolver_ip = tests_IPv6.resolver_identification()
            dns_result = tests_IPv6.dns_lookup(address, self.ip_type)

            if dns_result[0] == "OK":
                ip_address = tests_IPv6.get_ip_address(dns_result[1], self.ip_type)
                print(ip_address)
                tcp_result = tests_IPv6.tcp_handshake(ip_address)
                ping_result = tests_IPv6.ping_test(ip_address)
                trace_hop = tests_IPv6.perform_trace(ip_address)
                redirect = tests_IPv6.detect_redirect(address)
                http_status, content_length, headers, html_content = tests_IPv6.http_get_request(address)
                certificate = tests_IPv6.get_https_certificate(ip_address, address)

                end_time = time.time()
                duration = round(end_time - start_time, 2)
                output_content = reformat_url.extract_domain(address) + '_content.html'
                self.save_html_content(output_content, html_content)

                return CaseInsensitiveDict({
                    'Time': duration,
                    'URL': str(address),
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
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        except Exception as e:
            print(f"Error testing {address}: {e}")
            return {
                'URL': str(address),
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
