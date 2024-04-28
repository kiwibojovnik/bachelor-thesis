
def determine_censorship_type(differences):
    # Definujeme pravidla pro určení typu cenzury
    censorship_rules = {
        'Manipulace s DNS': {  #Je pozměněn výsledný content stránky
            'DNS IPs': {
                'CZ': lambda x: x is not None,
                'BY': None
            },
            'DNS manipulation - repeated query': {
                'CZ': lambda x: x == "No manipulation",
                'BY': lambda y: y == "Manipulate"
            },
            'DNS manipulation - hijacking detect': {
                'CZ': lambda x: x == "No manipulation",
                'BY': lambda y: y == "Manipulate"
            },
        },

        'Manipulace s TCP': {
            'TCP Status': {
                'CZ': lambda x: x == "Established",
                'BY': lambda y: y == "Failed" or y == "N/A"
            }
        },

        'Přerušení PING': {
            'PING Status': {
                'CZ': lambda x: x == "OK",
                'BY': lambda y: y == "Fail" or y == "N/A"
            },
        },
        'Vynucené přesměrování': {
            'Redirected Status': {
                'CZ': lambda x: x == "Not redirected",
                'BY': lambda y: y == "Redirected"
            }
        },
        'Odmítnutí HTTP požadavku': {
            'HTTP Status': {
                'CZ': lambda x: x == 200,
                'BY': lambda y: y,
                'comparison': lambda x, y: x != y
            }
        },
        'Podvržení obsahu HTTP': {
            'Content Length': {
                'CZ': lambda x: x,
                'BY': lambda y: y,
                'comparison': lambda x, y: abs(x - y) > 100
            }
        },
        'Podvržení vyhledávání v Google vyhledávači': {
            'Is domain in G search': {
                'CZ': lambda x: x == "Match",
                'BY': lambda y: y == "No match"
            }
        },
        'Přítomnost middle boxu': {
            'Middle box - header manipulation test': {
                'CZ': lambda x: x == "No manipulation",
                'BY': lambda y: y == "Manipulated"
            },
            'Middle box - invalid request line': {
                'CZ': lambda x: x == 0,
                'BY': lambda y: y == 1
            },
        }
    }

    for rule_name, conditions in censorship_rules.items():
        for key, value in conditions.items():
            CZ_condition = value['CZ']
            BY_condition = value['BY']
            # Zkontrolujeme, zda je podmínka funkce, a pokud ano, zavoláme ji, jinak porovnáme hodnoty
            if callable(CZ_condition) and callable(BY_condition):
                if CZ_condition(differences.get(key, {}).get('CZ')) and BY_condition(
                        differences.get(key, {}).get('BY')):
                    return rule_name
                    # Přidáme přiřazení výsledného typu cenzury, pokud je nalezena odpovídající podmínka
                    differences['CENSORSHIP TYPE'] = rule_name
            elif differences.get(key, {}).get('CZ') == CZ_condition and differences.get(key, {}).get(
                    'BY') == BY_condition:
                return rule_name
                # Přidáme přiřazení výsledného typu cenzury, pokud je nalezena odpovídající podmínka
                differences['CENSORSHIP TYPE'] = rule_name
    return None


def add_censorship_type_to_differences(differences):
    for url, diff in differences.items():
        censorship_type = determine_censorship_type(diff)
        if censorship_type:
            diff['CENSORSHIP TYPE'] = censorship_type

    return differences

