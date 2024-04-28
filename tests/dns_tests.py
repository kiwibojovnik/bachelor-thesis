import dns.resolver

from utils import reformat_url
from timeout_decorator import timeout

function_timeout = 60


@timeout(function_timeout)
def detect_dns_repeated_query(address):
    domain = reformat_url.extract_domain(address)

    try:
        resolver = dns.resolver.Resolver()
        # První dotaz na neexistující hostname
        resolver.resolve(domain, 'A')
        return "No manipulation"  # Pokud nevyvolá chybu, není detekován útok
    except dns.resolver.NXDOMAIN:
        try:
            # Opakovaný dotaz na stejný neexistující hostname
            resolver.resolve(domain, 'A')
            return "Manipulate"  # Pokud je vrácena NXDOMAIN, je detekován útok
        except dns.resolver.NXDOMAIN:
            return "No manipulation"  # Pokud i druhý dotaz vyvolá NXDOMAIN, není detekován útok
        except Exception as e:
            print("Chyba při druhém dotazu:", e)
            return "No manipulation"

    except TimeoutError:
        print("Resolver identification test exceeded timeout.")
        return "N/A"

    except Exception as e:
        print("Chyba při detekci opakovaného DNS dotazu:", e)
        return "No manipulation"


@timeout(function_timeout)
def detect_dns_hijacking(address):
    domain = reformat_url.extract_domain(address)

    try:
        resolver = dns.resolver.Resolver()

        # Dotaz na existující hostname, cenzorovaný DNS server by měl vrátit neočekávanou odpověď nebo žádnou
        answers = resolver.resolve(domain, 'A')
        if answers:
            return "No manipulation"  # Pokud server vrátí platnou odpověď, není detekován útok
        else:
            return "Manipulate"  # Pokud server nevrátí žádnou odpověď, může být detekován útok
    except dns.resolver.NoAnswer:
        return True  # Pokud server nevrátí odpověď, může být detekován útok

    except TimeoutError:
        print("Resolver identification test exceeded timeout.")
        return "N/A"

    except Exception as e:
        print("Chyba při detekci DNS hijackingu:", e)
        return "No manipulation"  # V případě jiné výjimky se předpokládá, že útok není detekován
