import dns.resolver


class DNSAttackDetector:
    def __init__(self):
        self.resolver = dns.resolver.Resolver()

    def detect_dns_repeated_query(self, hostname):
        try:
            # První dotaz na neexistující hostname
            self.resolver.resolve(hostname, 'A')
            return False  # Pokud nevyvolá chybu, není detekován útok
        except dns.resolver.NXDOMAIN:
            try:
                # Opakovaný dotaz na stejný neexistující hostname
                self.resolver.resolve(hostname, 'A')
                return True  # Pokud je vrácena NXDOMAIN, je detekován útok
            except dns.resolver.NXDOMAIN:
                return False  # Pokud i druhý dotaz vyvolá NXDOMAIN, není detekován útok
            except Exception as e:
                print("Chyba při druhém dotazu:", e)
                return False
        except Exception as e:
            print("Chyba při detekci opakovaného DNS dotazu:", e)
            return False

    def detect_dns_hijacking(self, hostname):
        try:
            # Dotaz na existující hostname, cenzorovaný DNS server by neměl vrátit odpověď
            self.resolver.resolve(hostname, 'A')
            return False  # Pokud server vrátí odpověď, je detekován útok
        except dns.resolver.NoAnswer:
            return True  # Pokud server nevrátí odpověď, není detekován útok
        except Exception as e:
            print("Chyba při detekci DNS hijackingu:", e)
            return False

    def detect_dns_injection(self, ip_address):
        try:
            # Dotaz na neexistující hostname na identifikované IP adrese
            self.resolver.resolve(ip_address + '.example.com', 'A')
            return False  # Pokud nevyvolá chybu, není detekován útok
        except dns.resolver.NXDOMAIN:
            return True  # Pokud je vrácena NXDOMAIN, je detekován útok
        except Exception as e:
            print("Chyba při detekci DNS injection:", e)
            return False


# Příklad použití
detector = DNSAttackDetector()

# Detekce opakovaného DNS dotazu
hostname = "www.idnes.cz"
repeated_query_detected = detector.detect_dns_repeated_query(hostname)
print("Detekce opakovaného DNS dotazu:", repeated_query_detected)

# Detekce DNS hijackingu
hijacking_detected = detector.detect_dns_hijacking("example.com")
print("Detekce DNS hijackingu:", hijacking_detected)

# Detekce DNS injection
ip_address = "192.0.2.1"
injection_detected = detector.detect_dns_injection(ip_address)
print("Detekce DNS injection:", injection_detected)
