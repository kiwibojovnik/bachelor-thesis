import dns.resolver


class DNSAttackDetector:
    def __init__(self, url_list):
        self.urls = url_list
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

    def test_website(self, website):

        dns_repeated = self.detect_dns_repeated_query(website)
        dns_hijacking = self.detect_dns_hijacking(website)
        dns_injection = self.detect_dns_injection(website)

        return {
            'URL': str(website),
            'DNS repeated': dns_repeated,
            'DNS Hijacking': dns_hijacking,
            'DNS Injection': dns_injection
        }

    def run_tests(self):
        results = []
        for website in self.urls:
            results.append(self.test_website(website))

        return results
