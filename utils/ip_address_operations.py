# Name: ip_address_operations.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Functions for information about ip addresses.
# Python Version: 3.12.3


# Import necessary libraries
from scapy.all import *  # Import all from scapy.all module for packet manipulation


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


def calculate_checksum(data):
    """
    Calculates checksum for the given data.

    Args:
        data (bytes): The data for which the checksum is to be calculated.

    Returns:
        int: The calculated checksum.
    """
    ch_sum = 0
    count = len(data)
    idx = 0

    # Add the data to the checksum in 16-bit chunks
    while count > 1:
        ch_sum += (data[idx + 1] << 8) + data[idx]
        idx += 2
        count -= 2

    # If there's a byte left, then add it to the checksum
    if count:
        ch_sum += data[idx]

    # Fold the checksum to 16 bits and add carry if any
    ch_sum = (ch_sum >> 16) + (ch_sum & 0xffff)
    ch_sum += (ch_sum >> 16)

    # Complement and mask to 16 bits
    ch_sum = ~ch_sum & 0xffff

    return ch_sum


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
