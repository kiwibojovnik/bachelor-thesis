import os
import json
import re

from process_data import compare, define_censorship, geolocation


def match_filename(CZ, BY):
    pattern = r"results_([a-zA-Z]+_\d+)_.*\.json"

    match_pattern1 = re.match(pattern, CZ)
    match_pattern2 = re.match(pattern, BY)

    if match_pattern1 and match_pattern2:
        country_identifier1 = match_pattern1.group(1)
        country_identifier2 = match_pattern2.group(1)

        # Split the country and number to compare them separately
        country1, number1 = country_identifier1.split('_')
        country2, number2 = country_identifier2.split('_')

        # Check if both the country and number match
        if country1 == country2 and number1 == number2:
            print(country1, number1, country2, number2)
            return True
    return False


# Define a function to process the files in the given folders - vždycky dostanu dva fily
# se stejnymi strankami
def process_two_files(folder1, folder2):
    diffs = {}

    for CZ in os.listdir(folder1):
        for BY in os.listdir(folder2):
            if match_filename(CZ, BY):
                # Load JSON data from both files
                with open(os.path.join(folder1, CZ), 'r', encoding='utf-8', errors='replace') as f1, \
                        open(os.path.join(folder2, BY), 'r', encoding='utf-8', errors='replace') as f2:
                    json_data1 = json.load(f1)
                    json_data2 = json.load(f2)

                    # Find differences
                    file_diffs = compare.compare_files(json_data1, json_data2)

                    # Add differences to diffs dictionary
                    diffs[CZ] = file_diffs

    return diffs


def process(folder1, folder2):
    # To seznamu dostanu všechny rozdilny testy
    print("Finding differences in each tests.")
    diffs = process_two_files(folder1, folder2)
    print(diffs)

    print("Definition of censorship type.")
    # Definovat typ cenzury na zakladě failů testů - přidám tam označení
    diffs = define_censorship.add_censorship_type_to_differences(diffs)

    print("Adding geolocation informations to traceroute informations.")
    # Get gps location na konkretni ipiny v traceroutu, asi jen na ty bělorusky ...
    diffs = geolocation.add_geolocation(diffs)

    print("Printing statistics about censorship")


    print("Saving results of each test with additional information to file.")
    # Ukládáme rozdíly do souboru
    with open('differenceshh.json', 'w') as diff_file:
        json.dump(diffs, diff_file, ensure_ascii=False, indent=4)
