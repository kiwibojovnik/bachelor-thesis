import requests

def check_website_via_tor(url):
    # Adresa veřejného Tor proxy serveru
    tor_proxy = {
        'http': 'socks5h://51.161.62.197:9050',
        'https': 'socks5h://51.161.62.197:9050'
    }

    try:
        # Provedení HTTP požadavku přes veřejné Tor proxy
        response = requests.get(url, proxies=tor_proxy)

        # Kontrola, zda byl požadavek úspěšný
        if response.ok:
            print("Stránka je dostupná přes Tor.")
        else:
            print("Stránka není dostupná přes Tor.")
    except Exception as e:
        print("Chyba při připojování přes Tor:", e)


url = "https://www.idnes.cz"  # Změňte na požadovanou URL
check_website_via_tor(url)