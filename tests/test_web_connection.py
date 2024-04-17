# -*- coding: utf-8 -*-
# Name: test_web_connection.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description:
# Python Version: 3.9
import socket

# Importing necessary libraries
import requests

from scapy.layers.inet import TCP, IP
from timeout_decorator import timeout
from scapy.all import *
from utils import reformat_url, icmp_test

function_timeout = 200
function_timeout_long = 200


@timeout(function_timeout)
def ping_test_old(address):
    try:
        ping_response = subprocess.check_output(["ping", "-c", "1", reformat_url.remove_http(address)])
        ping_response_str = ping_response.decode("utf-8")

        ip_address_match = re.search(r'\((.*?)\)', ping_response_str)
        ip_address = ip_address_match.group(1) if ip_address_match else "N/A"

        if ip_address != "N/A":
            return 'OK', ip_address
        else:
            return 'Fail', "N/A"

    except TimeoutError:
        print("Ping test exceeded timeout.")
        return "N/A", "N/A"
    except Exception as e:
        print("PING TEST ERROR: " + str(e))
        return "PING TEST ERROR: " + str(e), "N/A"


# TODO: otestit
@timeout(function_timeout_long)
def perform_trace_old(address):
    try:
        result = subprocess.run(['traceroute', '-I', address], capture_output=True, text=True)

        result = subprocess.check_output(["traceroute", "-I", reformat_url.remove_http(address)])
        result_str = result.decode("utf-8")

        lines = result_str.split('\n')
        hop_ips = []
        for line in lines[1:]:  # Skip header line
            if line.strip():
                hop_ip = line.split()[2]  # Assuming the IP address is at the fourth column
                hop_ips.append(hop_ip)

        return 'OK', hop_ips

    except TimeoutError:
        print("Trace test exceeded timeout.")
        return "N/A", "N/A"
    except Exception as e:
        print("PERFORM TRACE ERROR: " + str(e))
        return "PERFORM TRACE ERROR: " + str(e), "N/A"


@timeout(function_timeout)
def dns_lookup(website):
    try:
        ip_addresses = socket.gethostbyname_ex(
            reformat_url.remove_http(website))[2]
        return 'OK', ip_addresses
    except TimeoutError:
        print("DNS lookup test exceeded timeout.")
        return "N/A", "N/A"
    except socket.gaierror as e:
        print("DNS LOOKUP ERROR: " + str(e))
        return "DNS LOOKUP ERROR: " + str(e), "N/A"


# TODO: ještě otestovat...
@timeout(function_timeout)
def http_get_request(url):
    try:
        # Zkusíme HTTP variantu
        response = requests.get(reformat_url.add_https(url))
        return response.status_code, len(response.content), response.headers, response.text

    except requests.exceptions.RequestException as e:
        print(f"HTTP GET request to {url} failed: {e}")
        return str(e), "N/A", "N/A", "N/A"
    except TimeoutError:
        print("HTTP GET request exceeded timeout.")
        return "N/A", "N/A", "N/A", "N/A"
    except Exception as e:
        print("HTTP GET ERROR: " + str(e))
        return "HTTP GET ERROR: " + str(e), "N/A", "N/A", "N/A"


@timeout(function_timeout)
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


# TODO: proč to padá - asi sere pes
def tcp_connect(ip_address, port=80):
    try:
        response = sr1(IP(dst=ip_address) / TCP(dport=port, flags="S"), timeout=100, verbose=False)
        if response and response.haslayer(TCP) and response[TCP].flags == 18:
            remote_ip = response[IP].src
            return "Established", remote_ip
        else:
            return "Failed", "N/A"
    except TimeoutError:
        print("TCP connection test to {}:{} exceeded timeout of 5 seconds".format(ip_address, port))
        return "N/A", "N/A"
    except PermissionError as pe:
        print("TCP connection test to {}:{} failed due to permission error: {}".format(ip_address, port, pe))
        return "Permission Error", "N/A"
    except Exception as e:
        print("TCP ERROR: " + str(e))
        return "TCP ERROR: " + str(e), "N/A"


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
                ping_result = icmp_test.ping_test(reformat_url.remove_http(website))          #ping_test(website)

               # if ping_result[0] != "OK":
                trace_hop = icmp_test.perform_trace(reformat_url.remove_http(website))
               # else:
               #     trace_hop = "NOT RUN", "N/A"
                http_status, content_length, headers, html_content = http_get_request(website)

                end_time = time.time()
                duration = round(end_time - start_time, 2)

                output_content = reformat_url.remove_http(website) + '_content.html'

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
                    #'Trace hop Status': trace_hop[0],
                    'Trace hop IP': trace_hop,
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
