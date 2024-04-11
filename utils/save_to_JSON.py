import json
from collections import defaultdict
import re

import requests
from datetime import datetime


def get_ip_from_ping(ping):
    ip_regex = r'\((\d+\.\d+\.\d+\.\d+)\)'
    match = re.search(ip_regex, ping)
    if match:
        ip_address = match.group(1)
        return ip_address
    else:
        return None


def update_json_results(results, filename):
    try:
        # Načtení obsahu stávajícího souboru, pokud existuje
        with open(filename, 'r') as json_file:
            existing_data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Pokud soubor neexistuje nebo neobsahuje platný JSON obsah, inicializujte prázdný slovník
        existing_data = {"results": []}

    # Přidání nových dat nebo aktualizace existujících
    for result in results:
        page = result['page']
        ip_address = result['ip_address']
        test_scripts = result['test_scripts']

        # Kontrola existence záznamu s danou adresou
        found = False
        for entry in existing_data["results"]:
            if entry["page"] == page and entry["ip_address"] == ip_address:
                entry["test_scripts"].extend(test_scripts)
                found = True
                break

        # Pokud záznam s adresou neexistuje, vytvořte nový
        if not found:
            existing_data["results"].append(result)

    # Uložení aktualizovaných dat zpět do souboru
    with open(filename, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)


def parse_results(results):
    parsed_results = defaultdict(list)

    for result in results:
        page = result['URL']
        if 'PING Status' in result and str(result['PING Status']) != "N/A":
            ip_address = result['PING IP']
        else:
            ip_address = "N/A"

        # Vytvoření kopie původního slovníku a odstranění položky 'URL'
        test_script = result.copy()
        del test_script['URL']

        # Přidání aktuálního data a času
        test_script['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        parsed_results[(page, ip_address)].append(test_script)

    return parsed_results


def save_to_json(parsed_results, filename):
    try:
        # Načtení obsahu stávajícího souboru, pokud existuje
        with open(filename, 'r') as json_file:
            existing_data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Pokud soubor neexistuje nebo neobsahuje platný JSON obsah, inicializujte prázdný slovník
        existing_data = {"results": []}

    # Přidání nových dat
    for (page, ip_address), test_scripts in parsed_results.items():
        result_entry = {
            "page": page,
            "ip_address": ip_address,
            "test_scripts": []
        }
        for test_script in test_scripts:
            test_script_dict = {}
            for key, value in test_script.items():
                # Convert CaseInsensitiveDict to regular dict
                if isinstance(value, requests.structures.CaseInsensitiveDict):
                    value = dict(value)
                test_script_dict[key] = value
            result_entry["test_scripts"].append(test_script_dict)

        existing_data["results"].append(result_entry)

    # Uložení aktualizovaných dat zpět do souboru
    with open(filename, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)


def process_results(results, output_file):
    # Filtrujeme výsledky, aby se zbavili None hodnot
    filtered_results = [result for result in results if result is not None]
    parsed_results = parse_results(filtered_results)
    save_to_json(parsed_results, output_file)
