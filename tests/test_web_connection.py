import requests

from scapy.layers.inet import TCP, IP
from timeout_decorator import timeout
from scapy.all import *


@timeout(30)
def ping_test(address):
    try:
        ping_response = subprocess.check_output(["ping", "-c", "1", address])
        ping_response_str = ping_response.decode("utf-8")

        ip_address_match = re.search(r'\((.*?)\)', ping_response_str)
        ip_address = ip_address_match.group(1) if ip_address_match else "N/A"

        return 'OK', ip_address if "1 packets transmitted, 1 packets received" in ping_response_str else 'Fail', "N/A"

    except TimeoutError:
        print("Ping test exceeded timeout of 5 seconds")
        return "N/A", "N/A", "N/A"
    except Exception as e:
        print("PING TEST ERROR: " + str(e))
        return "PING TEST ERROR: " + str(e), "N/A", "N/A"


# TODO: Otestovat tuhle funkci
@timeout(100)
def perform_trace(address):
    try:
        result = subprocess.run(['traceroute', '-I', address], capture_output=True, text=True)
        output = result.stdout
        lines = output.split('\n')
        hop_ips = []
        for line in lines[1:]:  # Skip header line
            if line.strip():
                hop_ip = line.split()[3]  # Assuming the IP address is at the fourth column
                hop_ips.append(hop_ip)

        return 'OK', hop_ips


    except TimeoutError:
        print("Trace test exceeded timeout of 5 seconds")
        return "N/A", "N/A"
    except Exception as e:
        print("PERFORM TRACE ERROR: " + str(e))
        return "PERFORM TRACE ERROR: " + str(e), "N/A"


@timeout(30)
def dns_lookup(website):
    try:
        ip_addresses = socket.gethostbyname_ex(website)[2]
        return 'OK', ip_addresses
    except TimeoutError:
        print("DNS lookup test exceeded timeout of 5 seconds")
        return "N/A", "N/A"
    except socket.gaierror as e:
        print("DNS LOOKUP ERROR: " + str(e))
        return "DNS LOOKUP ERROR: " + str(e), "N/A"


@timeout(30)
def http_get_request(url):
    try:
        if is_url(url):
            get_url = requests.get(url)

        elif is_domain(url):
            try:
                get_url = requests.get('https://' + url)
            except requests.exceptions.RequestException as e:
                print(f"HTTP GET request to {url} failed: {e}")
                return "N/A", "N/A", "N/A", "N/A"

        elif is_ip(url):
            domain = socket.gethostbyaddr(url)[0]
            get_url = requests.get('http://' + domain)
        else:
            raise ValueError("Invalid input format")

        response = get_url
        return response.status_code, len(response.content), response.headers, response.text
    except TimeoutError:
        print("HTTP GET request exceeded timeout of 5 seconds")
        return "N/A", "N/A", "N/A", "N/A"
    except Exception as e:
        print("HTTP GET ERROR: " + str(e))
        return "HTTP GET ERROR: " + str(e), "N/A", "N/A", "N/A"



@timeout(30)
def resolver_identification():
    try:
        resolver_ip = socket.gethostbyname('whoami.akamai.com')
        return 'OK', resolver_ip
    except TimeoutError:
        print("Resolver identification test exceeded timeout of 5 seconds")
        return "N/A", "N/A"
    except socket.gaierror as e:
        print("RESOLVER ERROR: " + str(e))
        return "RESOLVER ERROR: " + str(e), "N/A"


@timeout(30)
def tcp_connect(ip_address, port=80):
    try:
        response = sr1(IP(dst=ip_address) / TCP(dport=port, flags="S"), timeout=5, verbose=False)
        if response and response.haslayer(TCP) and response[TCP].flags == 18:
            remote_ip = response[IP].src
            return "Established", remote_ip
        else:
            return "Failed", "N/A"
    except TimeoutError:
        print("TCP connection test exceeded timeout of 5 seconds")
        return "N/A", "N/A"
    except Exception as e:
        print("TCP ERROR: " + str(e))
        return "TCP ERROR: " + str(e), "N/A"


def is_url(url):
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'(?::\d+)?'
        r')(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(url_pattern, url) is not None


def is_domain(url):
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,}\.?)$', re.IGNORECASE)
    return re.match(domain_pattern, url) is not None


def is_ip(url):
    ip_pattern = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    return re.match(ip_pattern, url) is not None


class WebConnectivityTester:
    def __init__(self, url_list, output_content_folder):
        self.urls = url_list
        self.output_content_folder = output_content_folder

    def save_html_content(self, filename, content):
        # Create the output folder if it doesn't exist
        os.makedirs(self.output_content_folder, exist_ok=True)

        with open(os.path.join(self.output_content_folder, filename), 'w', encoding='utf-8') as content_file:
            content_file.write(content)

    def test_website(self, website):
        print(f"Testing {website}...")
        try:
            start_time = time.time()
            resolver_ip = resolver_identification()
            dns_result = dns_lookup(website)

            if dns_result[0] == "OK":
                tcp_result = tcp_connect(dns_result[1][0])
                ping_result = ping_test(website)

                if ping_result[0] != "OK":
                    trace_hop = perform_trace(website)
                else:
                    trace_hop = "NOT RUN", "N/A"

                http_status, content_length, headers, html_content = http_get_request(website)

                end_time = time.time()
                duration = round(end_time - start_time, 2)

                output_content = website + '_content.html'

                self.save_html_content(output_content, html_content)

                return {
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
                    'Trace hop Status': trace_hop[0],
                    'Trace hop IP': trace_hop[1],
                    'HTTP Status': http_status,
                    'Content Length': content_length,
                    'Headers': headers,
                    'HTML Content': output_content
                }

        except Exception as e:
            print(f"Error testing {website}: {e}")
            return {
                'URL': str(website),
                'Error': str(e)
            }

    def run_tests(self):
        results = []
        for website in self.urls:
            results.append({'URL': str(website)})
            results.append(self.test_website(website))

        return results
