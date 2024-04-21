# Tohle se bude dělat až v postprodukci, je zbytečné tohle dělat přímo v Bělorusku, alespon si to myslím.. ż

import ipinfo
import ipaddress

# Instantiate an IPInfo object with your API token
# TODO: Acces token dat do configu
access_token = '29334f89941369'
handler = ipinfo.getHandler(access_token)


def get_info(ip_address):
    try:
        details = handler.getDetails(ip_address)
        return {
            'Region': details.region,
            'Country': details.country,
            'GPS - latitude': details.latitude,
            'GPS - longitude': details.longitude
        }
    except Exception as e:
        return None


def add_geolocation(diffs):
    for url, diff in diffs.items():
        if 'Trace hop IP' in diff:
            for file, hops in diff['Trace hop IP'].items():
                for hop in hops:
                    ip_address = hop[0]
                    geolocation_info = get_info(ip_address)

                    if geolocation_info:
                        hop.extend(geolocation_info.values())

    return diffs
