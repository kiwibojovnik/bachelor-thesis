# -*- coding: utf-8 -*-
# Name: main.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: This script executes various classes and functions for testing network connectivity and others.
# Python Version: 3.9

# Import necessary libraries
import argparse
import csv
import re
import os
from datetime import datetime
from tests import call_test
from utils import save_to_JSON, send_file, load_config
from process_data import process


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some data.')
    parser.add_argument('-g', '--get', action='store_true', help='Retrieve data from a specified source. Use this '
                                                                 'flag to initiate data fetching.')
    parser.add_argument('-p', '--process', action='store_true', help='Process the retrieved data. This flag triggers '
                                                                     'the data processing operations.')
    parser.add_argument('-f', '--files', nargs='+', help='List of input files to be processed. Separate multiple file '
                                                         'paths with spaces.')
    parser.add_argument('-a', '--address', type=str, choices=['ipv4', 'ipv6'],
                        help='Specify the preferred IP version to use. Choose "ipv4" or "ipv6".')
    parser.add_argument('-s', '--start', type=int,
                        help='Specify the index from which to start the testing. The value represents the number of cycles '
                             '(each cycle corresponds to a group of 10 URLs) to be skipped before testing begins.')

    return parser.parse_args()


# Funkce pro extrakci názvu souboru, odstranění speciálních znaků, mezer a přípony
def extract_and_clean_filename(file_path):
    # Extrahování názvu souboru bez přípony
    file_name_with_extension = os.path.basename(file_path)
    file_name = re.sub(r'\..*$', '', file_name_with_extension)

    # Odstranění speciálních znaků a mezer
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', file_name)

    return clean_name


def main():
    args = parse_arguments()

    if not (args.get or args.process):
        print("Specify either '-g' to get data or '-p' to process data.")
        return

    if args.get:
        if args.files:
            for input_file in args.files:
                print("Processing " + input_file + "...")

                with open(input_file, 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)
                    website_list = [row[0] for row in reader]

                print(input_file)
                output_filepath = 'data/output_data/'
                output_content_folder = 'data/output_data/content_folder'

                start_index = 0
                if args.start:
                    start_index = args.start * 10

                # Split the list of URLs into groups of 10
                for index, i in enumerate(range(start_index, len(website_list), 10), start=1):
                    batch = website_list[i:i + 10]

                    if not args.address:
                        args.address = "ipv4"

                    tester = call_test.WebConnectivityTester(batch, output_content_folder, args.address.lower())
                    results = tester.run_tests()

                    date_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

                    print(args.files[0])
                    name = extract_and_clean_filename(args.files[0])

                    output_filename = "results_" + name + "_" + str(i) + "_" + date_time + ".json"

                    print("Saving to JSON file: " + output_filename)

                    save_to_JSON.save_test_results(results, output_filepath + output_filename)

                    # Save file to this path with the name of the output file.
                    remote_file_path = load_config.load_credentials("server_path_for_files") + output_filename

                    # Send the file to the server in Czech Republic
                    send_file.send_file_via_ssh(output_filepath + output_filename, remote_file_path)

        else:
            print("No input files specified.")

    elif args.process:
        if args.files and len(args.files) == 2:
            fold1, fold2 = args.files
            process.process(fold1, fold2)
        else:
            print("Please specify exactly two folders (First is CZ, second is BY) for processing.")


if __name__ == '__main__':
    main()
