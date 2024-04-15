import re
import requests
from urllib.parse import urlparse


# TODO: Opravdu tohle potřebuju? Asi je tento soubor na odstranění?
def is_url(url):
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'(?::\d+)?'
        r')(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(url_pattern, url) is not None


def is_domain(url):
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,}\.?)$', re.IGNORECASE)
    return re.match(domain_pattern, url) is not None


def is_ip(url):
    ip_pattern = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    return re.match(ip_pattern, url) is not None


def add_https(url):
    # Pokud adresa neobsahuje prefix "http://", přidej ho
    if not url.startswith("http"):
        url = "http://" + url

    return url


def remove_http(url):
    # Odstranění prefixu "http://"
    if url.startswith("http://"):
        url = url[len("http://"):]
    # Odstranění prefixu "https://"
    elif url.startswith("https://"):
        url = url[len("https://"):]

    return url
