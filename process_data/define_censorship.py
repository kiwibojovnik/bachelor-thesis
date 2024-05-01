import json


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
        'Podvržení obsahu HTTP': {
            'Content Length': {
                'CZ': lambda x: x,
                'BY': lambda y: y,
                'comparison': lambda x, y: abs(x - y) > 0.9 * max(x, y)
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

    keys = list(differences.keys())

    for key, diff in keys.items():
        for rule_name, conditions in censorship_rules:
            rule_matched = True
            for condition_set in conditions:
                condition_name = condition_set['condition_name']
                condition_values = condition_set['conditions']
                for country, condition in condition_values.items():
                    value = diff.get(condition_name, {}).get(country)
                    if value is None or not condition(value):
                        rule_matched = False
                        break
                if not rule_matched:
                    break
            if rule_matched:
                diff['CENSORSHIP TYPE'] = rule_name
                break

        if not rule_matched:
            diff['CENSORSHIP TYPE'] = 'No censorship found'

    return differences


def add_censorship_type_to_differences(differences):
    for url, diff in differences.items():
        determine_censorship(diff)

    return differences
