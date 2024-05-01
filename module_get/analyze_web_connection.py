# Name: analyze_web_connection.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Main functions for analyzing web connection.
# Python Version: 3.12.3


# Import necessary libraries
import requests  # Import requests module for making HTTP requests
import ssl  # Import ssl module for SSL-related functionalities
from scapy.all import *  # Import all from scapy.all module for packet manipulation
from timeout_decorator import timeout  # Import timeout decorator for setting execution timeout

from utils import reformat_url, ip_address_operations  # Import reformat_url function from utils module

function_timeout = 60  # Timeout value for function execution in seconds


@timeout(function_timeout)
def dns_lookup(address, ip_type):
    """
    Performs DNS lookup for a given website.

    First attempts to retrieve IPv6 addresses (if choose IPv6). If IPv6 addresses are available,
    they are preferred and returned. Otherwise, falls back to retrieving IPv4 addresses.

    Args:
        address (str): Website to perform DNS lookup for.
        ip_type (str): Type of the ip (IPv4 or IPv6)

    Returns:
        tuple: A tuple containing the status ('OK' or 'N/A') and a list of IP addresses (both IPv4 and IPv6).
    """
    try:
        domain = reformat_url.extract_domain(address)

        # Retrieve IPv4 addresses
        ip_addresses_ipv4 = socket.gethostbyname_ex(domain)[2]

        # Attempt to retrieve IPv6 addresses
        if ip_type == "ipv6":
            ip_addresses_ipv6 = socket.getaddrinfo(domain, None, socket.AF_INET6)
            ipv6_addresses = [addr[4][0] for addr in ip_addresses_ipv6]

            # Combine both IPv4 and IPv6 addresses
            all_addresses = ip_addresses_ipv4 + ipv6_addresses
        else:
            all_addresses = ip_addresses_ipv4

        # If any addresses are available, return 'OK'
        if all_addresses:
            return 'OK', all_addresses
        else:
            return 'N/A', 'N/A'

    except Exception as e:
        # Print an error message if there is an issue with DNS lookup
        print("DNS lookup error:" + str(e))
        return "N/A", "N/A"

    except TimeoutError:
        print("DNS lookup test exceeded timeout.")
        return "N/A", "N/A"


@timeout(function_timeout)
def get_https_certificate(ip_address, address, port=443):
    """
    Retrieves the HTTPS certificate for a given IP address and domain.

    Args:
        ip_address (str): The IP address to check (IPv4).
        address (str): The domain associated with the IP address.
        port (int, optional): The port number to connect to. Defaults to 443 for HTTPS.

    Returns:
        tuple: A tuple containing the status ('OK', 'Failed', or 'N/A') and the certificate or error message.
    """
    try:
        # Extract IPv4 address from a mapped IPv6 address if necessary
        ip_address = ip_address_operations.extract_ipv4_from_mapped_ipv6(ip_address)

        # Determine the IP address type
        ip_type = ip_address_operations.check_ip_address_type(ip_address)

        if ip_type == "ipv4":
            sock_type = socket.AF_INET
        else:
            sock_type = socket.AF_INET6

        # Create a default SSL context
        context = ssl.create_default_context()

        # Create a socket connection to the specified IP address
        with socket.socket(sock_type, socket.SOCK_STREAM) as sock:
            # If the port is 443 (default for HTTPS), attempt to retrieve the certificate
            if port == 443:
                sock.settimeout(10)

                sock.connect((ip_address, port))

                with context.wrap_socket(sock, server_hostname=reformat_url.extract_domain(address)) as ssock:
                    # Obtain the certificate from the socket
                    cert = ssock.getpeercert()
                    return "OK", cert
            else:
                # If the port is not 443, the site does not use HTTPS and no certificate is available
                print("The site does not use HTTPS, no certificate available.")
                return "Failed", "N/A"

    except Exception as e:
        # Print an error message if there is an issue retrieving the certificate
        print("Error retrieving certificate" + str(e))
        return "N/A", "N/A"

    except TimeoutError:
        print("Retrieving certificate exceeded timeout.")
        return "N/A", "N/A"


@timeout(function_timeout)
def tcp_handshake(destination_ip, destination_port=80):
    """
    Performs a TCP handshake with the specified IP address and port.

    Args:
        destination_ip (str): The IP address to connect to.
        destination_port (int, optional): The port number to connect to.
        Defaults to 80.

    Returns:
        tuple: A tuple containing the status ('Established', 'N/A', or 'Failed')
        and the remote IP address.
    """
    try:
        if ip_address_operations.check_ip_address_type(destination_ip) == "ipv6":
            socket_type = socket.AF_INET6
        else:
            socket_type = socket.AF_INET

        # Create a socket for TCP connection
        tcp_socket = socket.socket(socket_type, socket.SOCK_STREAM)

        # Set a timeout in case the connection is not successful
        tcp_socket.settimeout(20)

        # Initiate a connection to the specified IP address and port
        tcp_socket.connect((destination_ip, destination_port))

        # Get the remote IP address to which the connection was established
        remote_ip = tcp_socket.getpeername()[0]

        # Close the connection
        tcp_socket.close()

        return "Established", remote_ip

    except Exception as e:
        # Print an error message if there is an issue during the handshake
        print("TCP handshake error: " + str(e))
        return "Failed", "N/A"

    except TimeoutError:
        print("TCP connection test exceeded timeout.")
        return "N/A", "N/A"


@timeout(function_timeout)
def http_get_request(url):
    """
    Performs an HTTP GET request to the specified URL.

    Args:
        url (str): The URL to send the HTTP GET request to.

    Returns:
        tuple: A tuple containing the HTTP status code, content length,
        response headers, and response text.
        If an error occurs, it returns the error message followed by three 'N/A' strings.
    """
    try:
        # Define headers for the HTTP request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) '
                          'Chrome/97.0.4692.99 Safari/537.36'
        }

        session = requests.Session()
        # Send a GET request to the formatted URL with the defined headers
        response = session.get(reformat_url.add_http(url),
                               headers=headers)

        return (response.status_code, len(response.content),
                response.headers, response.text)

    except requests.exceptions.RequestException as e:
        print("HTTP GET request failed: " + str(e))
        return str(e), "N/A", "N/A", "N/A"

    except TimeoutError:
        print("HTTP GET request exceeded timeout.")
        return "N/A", "N/A", "N/A", "N/A"


@timeout(function_timeout)
def detect_redirect(url, ip_type):
    """
    Detects whether an HTTP request to the specified URL results in a redirect.

    Args:
        url (str): The URL to test for redirection.
        ip_type (str):

    Returns: tuple: A tuple containing the status ('Redirected' or 'Not redirected') and the redirection target URL
    and IP address. If an error occurs, it returns three 'N/A' strings.
    """
    try:
        # Perform an HTTP GET request without following redirects
        response = requests.get(reformat_url.add_http(url), allow_redirects=False, timeout=function_timeout)

        # Check if the request was redirected
        if response.is_redirect:
            ip_redirection = dns_lookup(response.headers['Location'], ip_type)
            return "Redirected", response.headers['Location'], ip_redirection
        else:
            return "Not redirected", "N/A", "N/A"

    except Exception as e:
        print("Redirect test error: " + str(e))
        return "N/A", "N/A", "N/A"

    except TimeoutError:
        print("Redirect test exceeded timeout.")
        return "N/A", "N/A", "N/A"


@timeout(function_timeout)
def ping_test(ip_address):
    """
    Performs a ping test to the specified IP address.

    Args:
        ip_address (str): The IP address to ping.

    Returns:
        tuple: A tuple containing the status ('OK', 'Fail', or 'N/A') and the source IP address.
        If an error occurs, it returns the error message followed by 'N/A'.
    """
    try:
        # Extract IPv4 address from a mapped IPv6 address if necessary
        ip_address = ip_address_operations.extract_ipv4_from_mapped_ipv6(ip_address)

        # Determine the IP address type
        ip_type = ip_address_operations.check_ip_address_type(ip_address)

        # Set socket parameters based on IP address type
        socket_type = socket.AF_INET6 if ip_type == "ipv6" else socket.AF_INET
        socket_proto = socket.getprotobyname('ipv6-icmp') if ip_type == "ipv6" else socket.IPPROTO_ICMP

        # Create a socket for sending ICMP packets
        with (socket.socket(socket_type, socket.SOCK_RAW, socket_proto) as sock):
            # Set a timeout
            sock.settimeout(3)

            # Create and send the ICMP packet based on IP address type
            if ip_type == "ipv6":
                icmp_packet = ip_address_operations.create_icmp6_echo_request()
            else:
                ip_address_operations.create_icmp4_echo_request()

            sock.sendto(icmp_packet, (ip_address, 0) if ip_type == "ipv6" else (ip_address, 1))

            # Wait for a response
            read_sockets, _, _ = select.select([sock], [], [], 1)
            if read_sockets:
                response, addr = sock.recvfrom(1024)

                # Process the response based on IP address type
                if ip_type == "ipv4":
                    icmp_type = response[20]
                    if icmp_type == 0:  # ICMP Echo Reply
                        ip_header = response[:20]
                        ip_header_fields = struct.unpack("!BBHHHBBH4s4s", ip_header)
                        ip_source_address = socket.inet_ntoa(ip_header_fields[8])
                        return 'OK', ip_source_address
                else:
                    icmp_header = response[:8]
                    icmp_type, _, _, icmp_id, _ = struct.unpack('!BBHHH', icmp_header)
                    if icmp_type == 129 and icmp_id == os.getpid() & 0xFFFF:  # Echo Reply
                        return 'OK', addr[0]

                return 'Fail', "N/A"
            else:
                return 'Fail', "N/A"

    except socket.timeout:
        print("Ping test exceeded timeout.")
        return "N/A", "N/A"

    except Exception as e:
        print("PING TEST ERROR: " + str(e))
        return "N/A", "N/A"


def perform_trace(ip_address):
    """
    Performs a traceroute to the specified IPv4 or IPv6 address.

    Args:
        ip_address (str): The IPv6 or IPv4 address to trace the route to.

    Returns:
        list: A list of tuples containing the IP address of each hop and the round-trip time.
    """
    max_hops = 30
    port = 33434
    trace_result = []

    # Extract IPv4 address from a mapped IPv6 address if necessary
    ip_address = ip_address_operations.extract_ipv4_from_mapped_ipv6(ip_address)

    # Determine the IP address type
    ip_type = ip_address_operations.check_ip_address_type(ip_address)

    # Define settings based on IP type
    settings = {
        "ipv4": {
            "socket_type": socket.AF_INET,
            "socket_proto": socket.IPPROTO_IP,
            "socket_uni": socket.IP_TTL,
            "icmp_echo_request": b'\x08\x00' + struct.pack('!HH', os.getpid() & 0xFFFF, 1),
            "sock_sock": socket.IPPROTO_ICMP
        },
        "ipv6": {
            "socket_type": socket.AF_INET6,
            "socket_proto": socket.IPPROTO_IPV6,
            "socket_uni": socket.IPV6_UNICAST_HOPS,
            "icmp_echo_request": b'',
            "sock_sock": socket.getprotobyname('ipv6-icmp')
        }
    }

    # Get the correct settings for the current IP type
    current_settings = settings[ip_type]

    for ttl in range(1, max_hops + 1):
        with socket.socket(current_settings["socket_type"], socket.SOCK_DGRAM, socket.IPPROTO_UDP) as send_socket:
            # Set the time-to-live for the packet
            send_socket.setsockopt(current_settings["socket_proto"], current_settings["socket_uni"], ttl)
            # Send an empty packet to the address and port
            send_socket.sendto(current_settings["icmp_echo_request"], (ip_address, port))

        with socket.socket(current_settings["socket_type"], socket.SOCK_RAW,
                           current_settings["sock_sock"]) as recv_socket:
            # Set a timeout for the receive operation
            recv_socket.settimeout(1)
            try:
                start_time = time.time()
                # Receive the packet
                pkt, addr = recv_socket.recvfrom(512)
                end_time = time.time()
                # Append the address and round-trip time to the result
                trace_result.append((addr[0], end_time - start_time))

                # Check if we have reached the destination server
                if addr[0] == ip_address:
                    break  # Exit the loop upon reaching the destination

            except socket.timeout:
                # If no response is received, continue to the next hop
                pass

    return trace_result
