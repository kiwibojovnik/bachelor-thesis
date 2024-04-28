import json


def compare_files(data1, data2, ignore_keys=None, ignore_header_items=None):
    if ignore_keys is None:
        ignore_keys = ['Time', 'Timestamp', 'HTML Content']
    if ignore_header_items is None:
        ignore_header_items = ['Date', 'expires', 'Server']

    differences = {}

    for url, details1 in data1.items():
        if url in data2:
            details2 = data2[url]
            # Filter out keys we want to ignore
            details1_filtered = {key: value for key, value in details1.items() if key not in ignore_keys}
            details2_filtered = {key: value for key, value in details2.items() if key not in ignore_keys}

            # Special handling for 'Headers' o ignore specific items and deserialize JSON strings if needed
            if 'Headers' in details1_filtered and 'Headers' in details2_filtered:
                headers1 = details1_filtered['Headers']
                headers2 = details2_filtered['Headers']

                # Check if headers1 is a dictionary, if not, skip to the next iteration
                if not isinstance(headers1, dict):
                    print(f"Warning: headers1 is not a dictionary. It's a {type(headers1)} with value: {headers1}")
                    continue

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
                        if url not in differences:
                            differences[url] = {}
                        if 'Headers' not in differences[url]:
                            differences[url]['Headers'] = {}
                        differences[url]['Headers'][header_key] = {'CZ': headers1[header_key],
                                                                   'BY': headers2[header_key]}

            # Compare the remaining keys
            for key in details1_filtered:
                if key == 'Headers' or key not in details2_filtered:
                    continue
                if details1_filtered[key] != details2_filtered[key]:
                    if url not in differences:
                        differences[url] = {}
                    differences[url][key] = {'CZ': details1_filtered[key], 'BY': details2_filtered[key]}

    return differences
