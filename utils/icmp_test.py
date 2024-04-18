import os
import struct
import socket
import select
import time


# Funkce pro výpočet kontrolního součtu
def calculate_checksum(data):
    checksum = 0
    count = len(data)
    idx = 0
    while count > 1:
        checksum += (data[idx + 1] << 8) + data[idx]
        idx += 2
        count -= 2
    if count:
        checksum += data[idx]
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum += (checksum >> 16)
    checksum = ~checksum & 0xffff
    return checksum


def ping_test(address):
    try:
        # Preferujeme IPv6, ale pokud adresa obsahuje tečku (typické pro IPv4), použijeme IPv4
        ip_version = socket.AF_INET6 if ':' in address else socket.AF_INET

        # Vytvoření socketu pro odesílání ICMP paketů
        icmp_socket = socket.socket(ip_version, socket.SOCK_RAW, socket.IPPROTO_ICMP)

        # Nastavení časovače pro případ, že by nebyl žádný odpověď
        icmp_socket.settimeout(1)

        # Vytvoření ICMP Echo Request paketu
        icmp_checksum = 0
        icmp_id = os.getpid() & 0xFFFF  # ID procesu pro identifikaci
        icmp_seq = 1  # Číslo sekvence paketu
        icmp_packet = struct.pack('!BBHHH', 8, 0, icmp_checksum, icmp_id, icmp_seq)
        icmp_checksum = calculate_checksum(icmp_packet)

        # Aktualizace paketu s vypočtenou kontrolní sumou
        icmp_packet = struct.pack('!BBHHH', 8, 0, socket.htons(icmp_checksum), icmp_id, icmp_seq)

        # Odeslání ICMP paketu na zadanou adresu
        icmp_socket.sendto(icmp_packet, (address, 1))

        # Přečtení odpovědi
        read_sockets, _, _ = select.select([icmp_socket], [], [], 1)
        if read_sockets:
            response, _ = icmp_socket.recvfrom(1024)
            icmp_type = response[20]
            if icmp_type == 0:  # ICMP Echo Reply
                ip_header = response[:20]
                ip_header_fields = struct.unpack("!BBHHHBBH4s4s", ip_header)
                ip_source_address = socket.inet_ntoa(ip_header_fields[8]) if ip_version == socket.AF_INET else socket.inet_ntop(socket.AF_INET6, ip_header_fields[8])
                return 'OK', ip_source_address
            else:
                return 'Fail', "N/A"
        else:
            return 'Fail', "N/A"

    except socket.timeout:
        print("Ping test exceeded timeout.")
        return "N/A", "N/A"
    except Exception as e:
        print("PING TEST ERROR: " + str(e))
        return "PING TEST ERROR: " + str(e), "N/A"


def ping_test6(address):
    try:
        # Vytvoření socketu pro odesílání ICMP paketů
        icmp_socket = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_ICMPV6)

        # Nastavení časovače pro případ, že by nebyl žádný odpověď
        icmp_socket.settimeout(1)

        # Vytvoření ICMPv6 Echo Request paketu
        icmp_checksum = 0
        icmp_id = os.getpid() & 0xFFFF  # ID procesu pro identifikaci
        icmp_seq = 1  # Číslo sekvence paketu
        icmp_packet = struct.pack('!BBHHH', 128, 0, icmp_checksum, icmp_id, icmp_seq)
        icmp_checksum = calculate_checksum(icmp_packet)

        # Aktualizace paketu s vypočtenou kontrolní sumou
        icmp_packet = struct.pack('!BBHHH', 128, 0, socket.htons(icmp_checksum), icmp_id, icmp_seq)

        # Odeslání ICMPv6 paketu na zadanou adresu
        icmp_socket.sendto(icmp_packet, (address, 0))

        # Přečtení odpovědi
        read_sockets, _, _ = select.select([icmp_socket], [], [], 1)
        if read_sockets:
            response, _ = icmp_socket.recvfrom(1024)
            icmp_type = response[0]
            if icmp_type == 129:  # ICMPv6 Echo Reply
                ip_source_address = socket.inet_ntop(socket.AF_INET6, response[8:24])
                return 'OK', ip_source_address
            else:
                return 'Fail', "N/A"
        else:
            return 'Fail', "N/A"

    except socket.timeout:
        print("Ping test exceeded timeout.")
        return "N/A", "N/A"
    except Exception as e:
        print("PING TEST ERROR: " + str(e))
        return "PING TEST ERROR: " + str(e), "N/A"


def perform_trace(address):
    max_hops = 30
    port = 33434
    icmp_echo_request = b'\x08\x00' + struct.pack('!HH', os.getpid() & 0xFFFF, 1)
    trace_result = []
    destination_address = socket.gethostbyname(address)  # Převedení hostname na IP adresu

    for ttl in range(1, max_hops + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as send_socket:
            send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
            send_socket.sendto(b'', (address, port))

        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as recv_socket:
            recv_socket.settimeout(1)
            try:
                start_time = time.time()
                packet, addr = recv_socket.recvfrom(512)
                end_time = time.time()
                trace_result.append((addr[0], end_time - start_time))

                # Kontrola, zda jsme dosáhli cílového serveru
                if addr[0] == destination_address:
                    print(f"Reached destination: {addr[0]}")
                    break  # Ukončení smyčky po dosažení cíle

            except socket.timeout:
                pass

    return trace_result


address = "idnes.cz"  # Nahraďte skutečnou IPv6 adresou
result, ip = ping_test(address)
print(f"Výsledek: {result}, Zdrojová IP: {ip}")


