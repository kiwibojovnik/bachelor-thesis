import json

def compare_files(file1, file2, ignore_keys=None, ignore_header_items=None):
    if ignore_keys is None:
        ignore_keys = ['Time']
    if ignore_header_items is None:
        ignore_header_items = ['Date', 'expires']

    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    differences = {}

    for url, details1 in data1.items():
        if url in data2:
            details2 = data2[url]
            # Filtrujeme klíče, které chceme ignorovat
            details1_filtered = {key: value for key, value in details1.items() if key not in ignore_keys}
            details2_filtered = {key: value for key, value in details2.items() if key not in ignore_keys}

            # Special handling for 'Headers' to ignore specific items and deserialize JSON strings if needed
            if 'Headers' in details1_filtered and 'Headers' in details2_filtered:
                headers1 = details1_filtered['Headers']
                headers2 = details2_filtered['Headers']
                for header_key in headers1:
                    if header_key in ignore_header_items or header_key not in headers2:
                        continue
                    # Deserialize JSON strings if they are present
                    if isinstance(headers1[header_key], str) and headers1[header_key].startswith('{'):
                        headers1[header_key] = json.loads(headers1[header_key])
                    if isinstance(headers2[header_key], str) and headers2[header_key].startswith('{'):
                        headers2[header_key] = json.loads(headers2[header_key])
                    # Compare the header values
                    if headers1[header_key] != headers2[header_key]:
                        if url not in differences:
                            differences[url] = {}
                        if 'Headers' not in differences[url]:
                            differences[url]['Headers'] = {}
                        differences[url]['Headers'][header_key] = {'File1': headers1[header_key], 'File2': headers2[header_key]}

            # Porovnáváme zbylé klíče
            for key in details1_filtered:
                if key == 'Headers' or key not in details2_filtered:
                    continue
                if details1_filtered[key] != details2_filtered[key]:
                    if url not in differences:
                        differences[url] = {}
                    differences[url][key] = {'File1': details1_filtered[key], 'File2': details2_filtered[key]}

    # Ukládáme rozdíly do souboru
    with open('differences.json', 'w') as diff_file:
        json.dump(differences, diff_file, ensure_ascii=False, indent=4)

    return differences

# Názvy souborů, které chcete porovnat
file1 = 'results_belarusAll-80_18-04-2024_17-15.json'
file2 = 'results_czechAll-80_19-04-2024_00-36.json'

# Volání funkce
compare_files(file1, file2)
