import requests
import stem
from stem import Signal
from stem.control import Controller

import requests
import random


def connect_to_tor():
    try:
        # TODO: spustit tor někde jinde - nejde
        with Controller.from_port(address='192.168.10.100', port=9050) as controller:
            controller.authenticate()
            print("Připojeno k řadiči Toru.")
            return controller

    except stem.SocketError as exc:
        print(f"Nepodařilo se připojit k řadiči Toru: {exc}")
        return None
    except stem.AuthenticationFailure as exc:
        print(f"Nepodařilo se autentizovat k řadiči Toru: {exc}")
        return None


def get_tor_session():
    controller = connect_to_tor()
    if controller:
        session = requests.session()
        session.proxies = {'http': 'socks5://127.0.0.1:9050',
                           'https': 'socks5://127.0.0.1:9050'}
        return session
    else:
        return None


def fetch_url_via_tor(url):
    session = get_tor_session()
    if session:
        try:
            response = session.get(url)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Chyba při získávání obsahu stránky: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Chyba při provádění HTTP požadavku: {e}")
            return None
    else:
        return None


# Změňte 'http://example.com' za adresu stránky, kterou chcete načíst.
# url = 'http://google.com'
# content = fetch_url_via_tor(url)
# if content:
#    print(content)
# else:
#    print("Chyba při získávání obsahu stránky přes Tor.")


def get_random_proxy():
    # Seznam proxy serverů, můžete použít jiný nebo najít online seznamy
    proxies = [
        'http://180.183.157.159:8080',
        'https://46.4.96.137:8080',
        'https://45.77.56.114:8080',
        # Přidejte další proxy servery podle potřeby
    ]
    return random.choice(proxies)


def make_request(url):
    proxy = get_random_proxy()
    try:
        response = requests.get(url, proxies={"http": proxy, "https": proxy})
        # Můžete přidat další zpracování odpovědi zde
        print("Úspěšně získáno")
        return response.text
    except Exception as e:
        print("Nepodařilo se získat:", e)
        return None


# Testovací URL, můžete jej změnit na cílovou stránku
url = 'https://www.idnes.com'
response_text = make_request(url)
if response_text:
    print(response_text)
else:
    print("Chyba při získávání obsahu.")
