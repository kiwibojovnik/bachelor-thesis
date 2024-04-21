import os
import json
import re

from process_data import compare, define_censorship, geolocation


def match_filename(file1, file2):
    pattern = r"results_([a-zA-Z]+-\d+)_.*\.json"

    match_pattern1 = re.match(pattern, file1)
    match_pattern2 = re.match(pattern, file2)

    if match_pattern1 and match_pattern2:
        country_identifier1 = match_pattern1.group(1)
        country_identifier2 = match_pattern2.group(1)
        print(country_identifier1, country_identifier2)

        if country_identifier1 == country_identifier2:
            return True
    return False


# Define a function to process the files in the given folders - vždycky dostanu dva fily
# se stejnymi strankami
def process_two_files(folder1, folder2):
    diffs = {}

    for file1 in os.listdir(folder1):
        for file2 in os.listdir(folder2):
            if match_filename(file1, file2):
                # Load JSON data from both files

                with open(os.path.join(folder1, file1), 'r', encoding='utf-8', errors='replace') as f1, \
                        open(os.path.join(folder2, file2), 'r', encoding='utf-8', errors='replace') as f2:
                    json_data1 = json.load(f1)
                    json_data2 = json.load(f2)

                    # Find differences
                    diffs = compare.compare_files(json_data1, json_data2)

    return diffs


def process(folder1, folder2):
    # To seznamu dostanu všechny rozdilny testy
    print("1")
    diffs = process_two_files(folder1, folder2)

    print("2")
    # Definovat typ cenzury na zakladě failů testů - přidám tam označení
    diffs = define_censorship.add_censorship_type_to_differences(diffs)

    print("3")
    # Get gps location na konkretni ipiny v traceroutu, asi jen na ty bělorusky ...
    diffs = geolocation.add_geolocation(diffs)

    print("4")
    # Ukládáme rozdíly do souboru
    with open('differencesKK.json', 'w') as diff_file:
        json.dump(diffs, diff_file, ensure_ascii=False, indent=4)
