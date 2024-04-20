# Název: edit_csv_file.py
# Autor: Dalibor Kyjovský (xkyjov03)
# Datum: 11. dubna 2024
# Popis: Tento skript upravuje csv soubor tak, aby vždi jako první argument byla uvedena url adresa.
# Verze Pythonu: 3.9

# Importing necessary libraries
import requests, ssl
from scapy.all import *
from timeout_decorator import timeout
from utils import reformat_url

function_timeout = 300


@timeout(function_timeout)
def resolver_identification():
    """
    Identifies the DNS resolver IP used by the local machine by querying 'whoami.akamai.com'.

    Returns:
        tuple: A tuple containing the status ('OK' or 'N/A') and the resolver IP address.
    """
    try:
        resolver_ip = socket.gethostbyname('whoami.akamai.com')
        return 'OK', resolver_ip

    except TimeoutError:
        print("Resolver identification test exceeded timeout.")
        return "N/A", "N/A"

    except socket.gaierror as e:
        print("RESOLVER ERROR: " + str(e))
        return "RESOLVER ERROR", "N/A"


@timeout(function_timeout)
def dns_lookup(address, ip_type):
    """
    Performs DNS lookup for a given website.

    First attempts to retrieve IPv6 addresses. If IPv6 addresses are available,
    they are preferred and returned. Otherwise, falls back to retrieving IPv4 addresses.

    Args:
        address (str): Website to perform DNS lookup for. Either in the format www.example.com or example.com.
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


def check_ip_address_type(ip_address):
    """
    Checks the type of the given IP address.

    Args:
        ip_address (str): The IP address to check.

    Returns:
        str: 'ipv4' if the address is IPv4, 'ipv6' if the address is IPv6, or 'Unknown' if neither.
    """
    try:
        # Attempt to create a socket for the given IP address
        socket.inet_pton(socket.AF_INET, ip_address)
        # If it's a valid IPv4 address, return "IPv4"
        return "ipv4"
    except socket.error:
        try:
            # Attempt to create a socket for the given IP address
            socket.inet_pton(socket.AF_INET6, ip_address)
            # If it's a valid IPv6 address, return "IPv6"
            return "ipv6"
        except socket.error:
            # If a socket cannot be created for either IPv4 or IPv6 address, return "Unknown"
            return "Unknown"


def get_ip_address(ip_list, ip_type):
    """
    Returns a sample IP address from the list based on the type specified.

    Args:
        ip_list (list): The list of IP addresses.
        ip_type (str): The type of IP address to return ('IPv4' or 'IPv6').

    Returns:
        str: A IP address of the specified type from the list, or 'No match' if none found.
    """
    # Filter the list based on the IP type using the check_ip_address_type function
    filtered_list = [ip for ip in ip_list if check_ip_address_type(ip) == ip_type]

    # Return a random sample from the filtered list, or 'No match' if the list is empty
    return random.choice(filtered_list) if filtered_list else 'No match'


def calculate_checksum(data):
    """
    Calculates checksum for the given data.

    Args:
        data (bytes): The data for which the checksum is to be calculated.

    Returns:
        int: The calculated checksum.
    """
    checksum = 0
    count = len(data)
    idx = 0

    # Add the data to the checksum in 16-bit chunks
    while count > 1:
        checksum += (data[idx + 1] << 8) + data[idx]
        idx += 2
        count -= 2

    # If there's a byte left, then add it to the checksum
    if count:
        checksum += data[idx]

    # Fold the checksum to 16 bits and add carry if any
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum += (checksum >> 16)

    # Complement and mask to 16 bits
    checksum = ~checksum & 0xffff

    return checksum


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
        ip_address = extract_ipv4_from_mapped_ipv6(ip_address)

        # Determine the IP address type
        ip_type = check_ip_address_type(ip_address)

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
        if check_ip_address_type(destination_ip) == "ipv6":
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

        # If the connection was successfully established and closed,
        # the handshake was successful
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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
        }

        session = requests.Session()
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

    Returns:
        tuple: A tuple containing the status ('Redirected' or 'Not redirected') and the redirection target URL.
        If an error occurs, it returns two 'N/A' strings.
    """
    try:
        # Perform an HTTP GET request without following redirects
        response = requests.get(reformat_url.add_http(url), allow_redirects=False)

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


def extract_ipv4_from_mapped_ipv6(ipv6_address):
    """
    Check if the given IPv6 address is a mapped IPv4 address and extract the IPv4 part.

    Args:
        ipv6_address (str): The IPv6 address to check.

    Returns:
        str: The extracted IPv4 address if the IPv6 address is a mapped address, otherwise None.
    """
    # Check if the address starts with the IPv6 mapped IPv4 prefix
    if ipv6_address.startswith("::ffff:"):
        # Extract the IPv4 part after the prefix
        ipv4_part = ipv6_address.split(":")[-1]
        try:
            # Validate the extracted part is a valid IPv4 address
            socket.inet_aton(ipv4_part)
            return ipv4_part
        except socket.error:
            # The extracted part is not a valid IPv4 address
            return ipv6_address
    else:
        # The address is not a mapped IPv4 address
        return ipv6_address


def create_icmp4_echo_request():
    """
    Create an ICMPv4 Echo Request packet.
    """
    icmp_checksum = 0
    icmp_id = os.getpid() & 0xFFFF  # Process ID for identification
    icmp_seq = 1  # Packet sequence number
    icmp_packet = struct.pack('!BBHHH', 8, 0, icmp_checksum, icmp_id, icmp_seq)
    icmp_checksum = calculate_checksum(icmp_packet)
    return struct.pack('!BBHHH', 8, 0, socket.htons(icmp_checksum), icmp_id, icmp_seq)


def create_icmp6_echo_request():
    """
    Create an ICMPv6 Echo Request packet.
    """
    icmp6_type = 128  # Echo Request
    icmp6_code = 0
    icmp6_checksum = 0
    icmp6_id = os.getpid() & 0xFFFF
    icmp6_seq = 1
    payload = b'abcdefghijklmnopqrstuvwabcdefghi'  # Payload data
    pseudo_header = struct.pack('!BBHHH', icmp6_type, icmp6_code, icmp6_checksum, icmp6_id, icmp6_seq)
    icmp6_checksum = calculate_checksum(pseudo_header + payload)
    return struct.pack('!BBHHH', icmp6_type, icmp6_code, icmp6_checksum, icmp6_id, icmp6_seq) + payload


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
        ip_address = extract_ipv4_from_mapped_ipv6(ip_address)

        # Determine the IP address type
        ip_type = check_ip_address_type(ip_address)

        # Set socket parameters based on IP address type
        socket_type = socket.AF_INET6 if ip_type == "ipv6" else socket.AF_INET
        socket_proto = socket.getprotobyname('ipv6-icmp') if ip_type == "ipv6" else socket.IPPROTO_ICMP

        # Create a socket for sending ICMP packets
        with socket.socket(socket_type, socket.SOCK_RAW, socket_proto) as sock:
            # Set a timeout
            sock.settimeout(3)

            # Create and send the ICMP packet based on IP address type
            icmp_packet = create_icmp6_echo_request() if ip_type == "ipv6" else create_icmp4_echo_request()
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
    Performs a traceroute to the specified IPv6 address.

    Args:
        ip_address (str): The IPv6 or IPv4 address to trace the route to.

    Returns:
        list: A list of tuples containing the IP address of each hop and the round-trip time.
    """
    max_hops = 30
    port = 33434
    trace_result = []

    # Extract IPv4 address from a mapped IPv6 address if necessary
    ip_address = extract_ipv4_from_mapped_ipv6(ip_address)

    # Determine the IP address type
    ip_type = check_ip_address_type(ip_address)

    # Define settings based on IP type
    settings = {
        "ipv4": {
            "socket_type": socket.AF_INET,
            "socket_iproto": socket.IPPROTO_IP,
            "socket_uni": socket.IP_TTL,
            "icmp_echo_request": b'\x08\x00' + struct.pack('!HH', os.getpid() & 0xFFFF, 1),
            "sock_sock": socket.IPPROTO_ICMP
        },
        "ipv6": {
            "socket_type": socket.AF_INET6,
            "socket_iproto": socket.IPPROTO_IPV6,
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
            send_socket.setsockopt(current_settings["socket_iproto"], current_settings["socket_uni"], ttl)
            # Send an empty packet to the address and port
            send_socket.sendto(current_settings["icmp_echo_request"], (ip_address, port))

        with socket.socket(current_settings["socket_type"], socket.SOCK_RAW,
                           current_settings["sock_sock"]) as recv_socket:
            # Set a timeout for the receive operation
            recv_socket.settimeout(1)
            try:
                start_time = time.time()
                # Receive the packet
                packet, addr = recv_socket.recvfrom(512)
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
