import socket
from scapy.all import *


def tcp_handshake(destination_ip, destination_port):
    try:
        # Vytvoření socketu pro TCP spojení
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Nastavení časovače pro případ, že spojení nebude úspěšné
        tcp_socket.settimeout(1)

        # Zahájení spojení s cílovou adresou a portem
        tcp_socket.connect((destination_ip, destination_port))

        # Získání lokální IP adresy, na kterou bylo připojení navázáno
        local_ip = tcp_socket.getpeername()[0]

        # Uzavření spojení
        tcp_socket.close()

        # Pokud se spojení podařilo navázat a uzavřít, handshake byl úspěšný
        return True, local_ip

    except Exception as e:
        # Pokud došlo k chybě při navazování spojení, handshake se nezdařil
        print("TCP handshake error:", e)
        return False, None


def tcp_connect(ip_address, port=80):
    try:
        # Odeslání TCP SYN paketu a čekání na odpověď
        response = sr1(IP(dst=ip_address) / TCP(dport=port, flags="S"), timeout=100, verbose=False)

        # Zpracování odpovědi
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


def test_tcp_connection(server, port):
    try:
        # Vytvoření socketu pro TCP spojení
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Nastavení časovače pro případ, že spojení nebude úspěšné
        tcp_socket.settimeout(5)

        # Pokus o spojení s daným serverem a portem
        tcp_socket.connect((server, port))

        # Uzavření spojení
        tcp_socket.close()

        print("Spojení s {} na portu {} je úspěšné.".format(server, port))
    except Exception as e:
        print("Chyba při pokusu o spojení s {} na portu {}: {}".format(server, port, e))


def get_https_certificate(hostname, port=443):
    try:
        # Vytvoření spojení na zadané HTTPS stránce
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # Získání certifikátu ze socketu
                cert = ssock.getpeercert()
                return cert
    except Exception as e:
        print("Chyba při získávání certifikátu:", e)
        return None


# Příklad použití
destination_ip = "belarus.by"
destination_port = 80

print(get_https_certificate(destination_ip))

# tcph, ip = tcp_handshake(destination_ip, destination_port)
# print(tcph, ip)

# test_tcp_connection(destination_ip, destination_port)


# tcp, tcp2 = tcp_connect(destination_ip)
# print(tcp, tcp2)
