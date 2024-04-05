import requests
import socket
import time
import os
import subprocess
import re
from timeout_decorator import timeout


@timeout(5)
def ping_test(address):
    try:

        ping_response = subprocess.check_output(["ping", "-c", "1", address])
        ping_response_str = ping_response.decode("utf-8")

        ip_address_match = re.search(r'\((.*?)\)', ping_response_str)
        ip_address = ip_address_match.group(1) if ip_address_match else "N/A"
        return 'OK_(' + ip_address + ')' if "1 packets transmitted, 1 packets received" in ping_response_str else 'Fail'

    except TimeoutError:
        print("Ping test exceeded timeout of 5 seconds")
        return "N/A"
    except Exception as e:
        return "N/A", str(e)


@timeout(5)
def perform_trace(address):
    try:
        # Run traceroute with the -I switch to determine the path to the destination server
        result = subprocess.run(['traceroute', '-I', address], capture_output=True, text=True)

        output = result.stdout
        lines = output.split('\n')
        last_hop = lines[-2] if len(lines) > 1 else "N/A"

        return last_hop

    except TimeoutError:
        print("Ping test exceeded timeout of 5 seconds")
        return "N/A"
    except Exception as e:
        return "N/A", str(e)


@timeout(5)
def dns_lookup(website):
    try:
        # Can return more ip_addresses in the tuple
        ip_addresses = socket.gethostbyname_ex(website)[2]
        return ip_addresses
    except TimeoutError:
        print("Ping test exceeded timeout of 5 seconds")
        return "N/A"
    except socket.gaierror:
        return "N/A", str(socket.gaierror)


# TODO: opravit
@timeout(5)
def http_get_request(url):
    try:
        if is_url(url):
            get_url = requests.get(url)

        elif is_domain(url):
            get_url = requests.get('https://' + url)

        elif is_ip(url):
            # Perform DNS lookup to get the domain associated with the IP address
            domain = socket.gethostbyaddr(url)[0]
            get_url = requests.get(domain)  # Assuming HTTP here for IP address
        else:
            raise ValueError("Invalid input format")

        response = get_url
        return response.status_code, len(response.content), response.headers, response.text
    except TimeoutError:
        print("Ping test exceeded timeout of 5 seconds")
        return "N/A"
    except Exception as e:
        return "N/A", "N/A", "N/A", str(e)


# Used to identify the resolver that is used to resolve domain names to IP addresses.
@timeout(5)
def resolver_identification():
    try:
        resolver_ip = socket.gethostbyname('whoami.akamai.com')
        return resolver_ip
    except TimeoutError:
        print("Ping test exceeded timeout of 5 seconds")
        return "N/A"
    except socket.gaierror:
        return "N/A", str(socket.gaierror)


@timeout(5)
def tcp_connect(ip_address, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            if sock.connect_ex((ip_address, port)) == 0:
                response = 'Established'
            else:
                response = 'Failed'

            sock.close()
            return response
    except TimeoutError:
        print("Ping test exceeded timeout of 5 seconds")
        return "N/A"
    except Exception as e:
        return "N/A", str(e)


def is_url(url):
    # Regular expression pattern for URL validation
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'  # Scheme
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # Domain...
        r'localhost|'  # localhost...
        r'(?::\d+)?'  # Optional port
        r')(?:/?|[/?]\S+)$', re.IGNORECASE)  # Close the port subpattern and continue the URL pattern
    return re.match(url_pattern, url) is not None


def is_domain(url):
    # Regular expression pattern for domain validation
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,}\.?)$', re.IGNORECASE)

    return re.match(domain_pattern, url) is not None


def is_ip(url):
    # Regular expression pattern for IP validation
    ip_pattern = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')

    return re.match(ip_pattern, url) is not None


class WebConnectivityTester:
    def __init__(self, url_list, output_content_folder, output_file):
        self.urls = url_list
        self.output_content_folder = output_content_folder
        self.output_file = output_file

    def save_html_content(self, filename, content):
        # Create the output folder if it doesn't exist
        os.makedirs(self.output_content_folder, exist_ok=True)

        with open(os.path.join(self.output_content_folder, filename), 'w', encoding='utf-8') as content_file:
            content_file.write(content)

    def test_website(self, website):
        print(f"Testing {website}...")
        try:
            start_time = time.time()

            trace_hop = None

            resolver_ip = resolver_identification()
            dns_result = dns_lookup(website)

            if dns_result == "N/A":
                pass

            tcp_result = tcp_connect(dns_result[0], 80)
            ping_result = ping_test(website)

            if ping_result == "fail" or ping_result == "N/A":
                trace_hop = perform_trace(website)

            http_status, content_length, headers, html_content = http_get_request(website)

            end_time = time.time()

            duration = round(end_time - start_time, 2)

            output_content = website + '_content.html'
            self.save_html_content(output_content, html_content)
            return {
                'Time': duration,
                'URL': str(website),
                'Resolver IP': resolver_ip,
                'DNS Result': dns_result,
                'TCP Status': tcp_result,
                'PING Result': ping_result,
                'Trace hop': trace_hop,
                'HTTP Status': http_status,
                'Content Length': content_length,
                'Headers': headers,
                'HTML Content': output_content
            }


        except Exception as e:
            print(f"Error testing {website}: {e}")
            return {
                'URL': website,
                'Error': str(e)
            }

    def run_tests(self):
        results = []
        for website in self.urls:
            results.append(self.test_website(website))

        return results
