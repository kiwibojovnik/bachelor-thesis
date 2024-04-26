
def determine_censorship_type(differences):
    # Definujeme pravidla pro určení typu cenzury
    censorship_rules = {
        'Manipulace s HTTP': {  #Je pozměněn výsledný content stránky
            'PING IP': {
                'File1': None,
                'File2': lambda x: x is not None
            }
        },
        'Manipulace s DNS': {   #Asi TODO ještě...
            'PING IP': {
                'File1': None,
                'File2': lambda x: x is not None
            }
        },
        'Přerušení TCP spojení': {  #nejde navázat TCP handshake
            'PING Status': {
                'File1': lambda x: x,
                'File2': lambda y: y,
                'comparison': lambda x, y: x != y
            },
        },
        'Omezená přístupnost k webové stránce': {      #tohle když nefungujje pingnuti se na stránku
            'DNS IPs': {
                'File1': lambda x: x,
                'File2': lambda y: y,
                'comparison': lambda x, y: x != y
            }
        },
        'Přesměrování stránky': {
            'HTTP Status': {
                'File1': lambda x: x,
                'File2': lambda y: y,
                'comparison': lambda x, y: x != y
            }
        },
        'Výskyt domény v google vyhledávání': {
            'HTTP Status': {
                'File1': lambda x: x,
                'File2': lambda y: y,
                'comparison': lambda x, y: x != y
            }
        },
        'Přítomnost middle boxu': {
            'HTTP Status': {
                'File1': lambda x: x,
                'File2': lambda y: y,
                'comparison': lambda x, y: x != y
            }
        }
    }

    for rule_name, conditions in censorship_rules.items():
        for key, value in conditions.items():
            file1_condition = value['File1']
            file2_condition = value['File2']
            # Zkontrolujeme, zda je podmínka funkce, a pokud ano, zavoláme ji, jinak porovnáme hodnoty
            if callable(file1_condition) and callable(file2_condition):
                if file1_condition(differences.get(key, {}).get('File1')) and file2_condition(
                        differences.get(key, {}).get('File2')):
                    return rule_name
            elif differences.get(key, {}).get('File1') == file1_condition and differences.get(key, {}).get(
                    'File2') == file2_condition:
                return rule_name
    return None


def add_censorship_type_to_differences(differences):
    for url, diff in differences.items():
        censorship_type = determine_censorship_type(diff)
        if censorship_type:
            diff['CENSORSHIP TYPE'] = censorship_type

    return differences

