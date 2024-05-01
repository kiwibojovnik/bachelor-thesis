# Name: define_censorship.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Skript with rules for definition of censorship type.
# Python Version: 3.12.3


def determine_censorship(differences):
    # Definujeme pravidla pro určení typu cenzury
    censorship_rules = {
        'Manipulace s DNS': {  # Je pozměněn výsledný content stránky
            'DNS Status': {
                'CZ': lambda x: x == "OK",
                'BY': lambda y: y == "N/A"
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
            'TCP Remote IP': {
                'CZ': lambda x: x == "Established",
                'BY': lambda y: y == "Failed" or y == "N/A"
            }
        },

        'Přerušení PING': {
            'PING IP': {
                'CZ': lambda x: x == "OK",
                'BY': lambda y: y == "Fail" or y == "N/A"
            },
        },
        'Vynucené přesměrování': {
            'Redirected Location IPs': {
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
        },
        'Podvržení obsahu HTTP': {  # TODO opravit: už nevím jak
            'Contdent Length': {
                'CZ': lambda x: x > 10000,
                'BY': lambda y: y == 0,
                'comparison': lambda x, y: x != y and y != x
            }
        }
    }

    keys = list(differences.keys())

    for key in keys:
        rule_matched = False  # Příznak, zda bylo pravidlo shodné
        # Pro každé pravidlo zjišťujeme, zda vstupní data splňují podmínky
        for rule_name, conditions in censorship_rules.items():
            for condition_name, condition_values in conditions.items():
                for country, condition in condition_values.items():
                    value = differences[key].get(condition_name, {}).get(country)
                    if value is not None and condition(value):
                        rule_matched = True
                        differences[key]['CENSORSHIP TYPE'] = rule_name
                        break  # Přerušíme vnitřní cyklus, pokud bylo pravidlo shodné
                if rule_matched:
                    break  # Přerušíme vnější cyklus, pokud bylo pravidlo shodné
            if rule_matched:
                break  # Přerušíme nejvnější cyklus, pokud bylo pravidlo shodné

        if not rule_matched:
            differences[key]['CENSORSHIP TYPE'] = 'No censorship found'

    return differences


def add_censorship_type_to_differences(differences):
    for url, diff in differences.items():
        determine_censorship(diff)

    return differences
