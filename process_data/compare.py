import json


def count_keys_with_no_results(data1, data2):
    keys_with_no_results_count = 0

    for url, details1 in data1.items():
        if url in data2:
            details2 = data2[url]
            for key in details1:
                if key not in details2:
                    keys_with_no_results_count += 1

    return keys_with_no_results_count


def filter_details(details, ignore_keys):
    return {key: value for key, value in details.items() if key not in ignore_keys}


def compare_headers(headers1, headers2, ignore_header_items):
    differences = {}
    for header_key in list(headers1):  # Convert to list to avoid RuntimeError
        if header_key in ignore_header_items or header_key not in headers2:
            continue
        # Deserialize JSON strings if they are present
        if isinstance(headers1[header_key], str) and headers1[header_key].startswith('{'):
            try:
                headers1[header_key] = json.loads(headers1[header_key])
            except json.JSONDecodeError:
                print(f"Warning: Error decoding JSON from headers1['{header_key}']")
                continue
        if isinstance(headers2[header_key], str) and headers2[header_key].startswith('{'):
            try:
                headers2[header_key] = json.loads(headers2[header_key])
            except json.JSONDecodeError:
                print(f"Warning: Error decoding JSON from headers2['{header_key}']")
                continue
        # Compare the header values
        if headers1[header_key] != headers2[header_key]:
            differences[header_key] = {'CZ': headers1[header_key], 'BY': headers2[header_key]}
    return differences


def compare_files(data1, data2, ignore_keys=None, ignore_header_items=None):
    if ignore_keys is None:
        ignore_keys = ['Time', 'Timestamp', 'HTML Content']
    if ignore_header_items is None:
        ignore_header_items = ['Date', 'expires', 'Server']

    differences = {}
    url_in_data = 0
    different_sites_count = 0  # Počet stránek s rozdíly
    same_sites_count = 0  # Počet stránek bez rozdílů nebo s ignorovanými klíči

    for url, details1 in data1.items():
        if url in data2:
            url_in_data += 1
            details2 = data2[url]
            details1_filtered = filter_details(details1, ignore_keys)
            details2_filtered = filter_details(details2, ignore_keys)

            headers_differences = {}
            if 'Headers' in details1_filtered and 'Headers' in details2_filtered:
                headers1 = details1_filtered['Headers']
                headers2 = details2_filtered['Headers']
                if not isinstance(headers1, dict):
                    print(f"Warning: headers1 is not a dictionary. It's a {type(headers1)} with value: {headers1}")
                    continue

                headers_differences = compare_headers(headers1, headers2, ignore_header_items)

            # Compare the remaining keys
            key_differences = False
            for key in details1_filtered:
                if key == 'Headers' or key not in details2_filtered:
                    continue
                if details1_filtered[key] != details2_filtered[key]:
                    if url not in differences:
                        differences[url] = {}
                    differences[url][key] = {'CZ': details1_filtered[key], 'BY': details2_filtered[key]}
                    key_differences = True

            if headers_differences or key_differences:
                if url not in differences:
                    differences[url] = {}
                if headers_differences:
                    differences[url]['Headers'] = headers_differences
                different_sites_count += 1  # Přidáme počet stránek s rozdíly
            else:
                same_sites_count += 1  # Přidáme počet stránek bez rozdílů

    return differences, different_sites_count, same_sites_count
