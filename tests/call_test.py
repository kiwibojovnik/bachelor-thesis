from datetime import datetime
import os
import time
from requests.structures import CaseInsensitiveDict
from tests import tests_IPv6, google_search, test_middle_box, dns_tests
from utils import reformat_url

sleeping_time = 10


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
                tcp_result = tests_IPv6.tcp_handshake(ip_address)
                ping_result = tests_IPv6.ping_test(ip_address)

                if ping_result[0] != "OK":
                    trace_hop = tests_IPv6.perform_trace(ip_address)
                else:
                    trace_hop = "N/A"

                redirect = tests_IPv6.detect_redirect(address, self.ip_type)
                http_status, content_length, headers, html_content = tests_IPv6.http_get_request(address)
                certificate = tests_IPv6.get_https_certificate(ip_address, address)

                middle_box_header = test_middle_box.http_header_manipulation(address)
                middle_box_invalid_request = test_middle_box.invalid_request_line(address)

                dns_manipulation1 = dns_tests.detect_dns_repeated_query(address)
                dns_manipulation2 = dns_tests.detect_dns_hijacking(address)

                search_results = google_search.is_domain_in_results(address)

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
                    'Redirected Location IPs': redirect[2],
                    'HTTP Status': http_status,
                    'Content Length': content_length,
                    'Headers': headers,
                    'HTML Content': output_content,
                    'Cert Status': certificate[0],
                    'Cert Content': certificate[1],
                    'Middle box - header manipulation test': middle_box_header,
                    'Middle box - invalid request line': middle_box_invalid_request,
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
        for website in self.urls:
            time.sleep(sleeping_time)
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
