# Tohle se bude dělat až v postprodukci, je zbytečné tohle dělat přímo v Bělorusku, alespon si to myslím.. ż

import ipinfo

# Instantiate an IPInfo object with your API token
access_token = '29334f89941369'
handler = ipinfo.getHandler(access_token)


def get_info(ip_address):
    details = handler.getDetails(ip_address)

    return {
        'City': details.ip,
        'Region': details.region,
        'Country': details.country,
        'Hostname': details.hostname
    }


get_info('93.125.114.187')
