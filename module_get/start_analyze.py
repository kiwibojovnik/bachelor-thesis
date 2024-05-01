# Name: start_analyze.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Calling all scripts for analyzing network.
# Python Version: 3.12.3


# Import necessary libraries
from datetime import datetime  # Import datetime module for datetime operations
import os  # Import os module for operating system related functionalities
import random  # Import random module for generating random numbers
import time  # Import time module for time-related operations
from requests.structures import CaseInsensitiveDict  # Import CaseInsensitiveDict from requests.structures module
from module_get import analyze_web_connection, analyze_google_search, analyze_middle_box, analyze_dns  # Import
# functions for web connection analysis
from utils import reformat_url, ip_address_operations  # Import reformat_url function from the utils module


def timeout():
    """
    Simulates a timeout by waiting for a random amount of time between 25 and 70 seconds.
    """

    # Generate a random timeout value between 25 and 70 seconds
    timeout_random = random.randint(25, 70)

    # Wait for the randomly generated timeout
    time.sleep(timeout_random)


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
            dns_result = analyze_web_connection.dns_lookup(address, self.ip_type)

            if dns_result[0] == "OK":
                ip_address = ip_address_operations.get_ip_address(dns_result[1], self.ip_type)
                tcp_result = analyze_web_connection.tcp_handshake(ip_address)
                ping_result = analyze_web_connection.ping_test(ip_address)

                if ping_result[0] != "OK":
                    trace_hop = analyze_web_connection.perform_trace(ip_address)
                else:
                    trace_hop = "N/A"

                redirect = analyze_web_connection.detect_redirect(address, self.ip_type)

                http_status, content_length, headers, html_content = analyze_web_connection.http_get_request(address)
                certificate = analyze_web_connection.get_https_certificate(ip_address, address)

                middle_box_header = analyze_middle_box.http_header_manipulation(address)
                middle_box_invalid_request = analyze_middle_box.invalid_request_line(address)

                dns_manipulation1 = analyze_dns.detect_dns_repeated_query(address)
                dns_manipulation2 = analyze_dns.detect_dns_hijacking(address)

                search_results = analyze_google_search.is_domain_in_results(address)

                end_time = time.time()

                duration = round(end_time - start_time, 2)
                output_content = reformat_url.extract_domain(address) + '_content.html'
                self.save_html_content(output_content, html_content)

                return CaseInsensitiveDict({
                    'Time': duration,
                    'URL': str(address),
                    'DNS Status': dns_result[0],
                    'DNS IPs': dns_result[1],
                    'TCP Status': tcp_result[0],
                    'TCP Remote IP': tcp_result[1],
                    'PING Status': ping_result[0],
                    'PING IP': ping_result[1],
                    'Trace hop IP': trace_hop,
                    'Redirected Status': redirect[0],
                    'Redirected Location': redirect[1],
                    'Redirected Location IPs': redirect[2],
                    'HTTP Status': http_status,
                    'Content Length': content_length,
                    'Headers': headers,
                    'HTML Content': output_content,
                    'Cert Status': certificate[0],
                    'Cert Content': certificate[1],
                    'Middle box - header manipulation test': middle_box_header,
                    'Middle box - invalid request line': middle_box_invalid_request,
                    'DNS manipulation - repeated query': dns_manipulation1,
                    'DNS manipulation - hijacking detect': dns_manipulation2,
                    'Is domain in G search': search_results,
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

        timeout()

        for website in self.urls:
            timeout()
            results.append({'URL': str(website)})
            retry_count = 0
            while retry_count < 6:  # Retry for a maximum of 5 times
                result = self.test_website(website)
                # Check if result is not None before proceeding
                if result is not None and '429' in str(result.get('Error', '')):  # If 429 error occurred
                    retry_count += 1
                    print(f"Received 429 error, retrying in {5 ** retry_count} seconds...")
                    time.sleep(5 ** retry_count)  # Exponential backoff
                elif result is not None:
                    results.append(result)
                    break
                else:
                    # Handle the case where result is None
                    print(f"Failed to get a result for {website}, skipping...")
                    break
            else:
                print("Failed to test website after multiple retries.")
        return results
