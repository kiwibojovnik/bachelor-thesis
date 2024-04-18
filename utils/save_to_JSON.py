import json
from requests.structures import CaseInsensitiveDict


# Převod CaseInsensitiveDict na standardní slovník
def convert_to_dict(case_insensitive_dict):
    if isinstance(case_insensitive_dict, CaseInsensitiveDict):
        return dict(case_insensitive_dict)
    return case_insensitive_dict


# Upravená funkce pro ukládání výsledků testu
def save_test_results(test_results, filename):
    # Vytvoření nového slovníku pro výsledky s převedenými hlavičkami
    results_dict = {result['URL']: {k: convert_to_dict(v) for k, v in result.items()} for result in test_results}

    # Uložení výsledků do souboru JSON
    with open(filename, 'w') as file:
        json.dump(results_dict, file, indent=4)
