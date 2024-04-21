# -*- coding: utf-8 -*-
# Name: main.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: This script execute of various classes and functions for testing network connectivity and others.
# Python Version: 3.9


# Importing necessary libraries
import argparse
import csv
from datetime import datetime
from tests import call_test
from utils import save_to_JSON, send_file, load_config
from process_data import process

# TODO: opravit tyhle když je -p tak jsou vstupen jen dvě složky
def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some data.')
    parser.add_argument('-g', '--get', action='store_true', help='Retrieve data from a specified source. Use this '
                                                                 'flag to initiate data fetching.')
    parser.add_argument('-p', '--process', action='store_true', help='Process the retrieved data. This flag triggers '
                                                                     'the data processing operations.')
    parser.add_argument('-f', '--files', nargs='+', help='List of input files to be processed. Separate multiple file '
                                                         'paths with spaces.')
    parser.add_argument('-n', '--filename', help='Define the filename for the output file. The results will be saved '
                                                 'to this file.')
    parser.add_argument('-a', '--address', type=str, choices=['ipv4', 'ipv6'],
                        help='Specify the preferred IP version to use. Choose "ipv4" or "ipv6".')

    return parser.parse_args()


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

                # Rozdělení seznamu URL na skupiny po 10
                for index, i in enumerate(range(0, len(website_list), 10), start=1):
                    batch = website_list[i:i + 10]

                    if not args.address:
                        args.address = "ipv4"

                    tester = call_test.WebConnectivityTester(batch, output_content_folder, args.address.lower())
                    results = tester.run_tests()

                    date_time = datetime.now().strftime("%d-%m-%Y_%H-%M")

                    if args.filename:
                        name = str(args.filename) + "-"
                    else:
                        name = ""

                    output_filename = "results_" + name + str(i) + "_" + date_time + ".json"

                    print("Saving to JSON file: " + output_filename)

                    save_to_JSON.save_test_results(results, output_filepath + output_filename)

                    # Save file to this path with name of output file.
                    remote_file_path = load_config.load_credentials("server_path_for_files") + output_filename

                    # Posilani souboru na server do česka
                    send_file.send_file_via_ssh(output_filepath + output_filename, remote_file_path)

        else:
            print("No input files specified.")

    elif args.process:
        if args.files:
            # TODO: maximalni počet vstupu je 2 -- dvě složky na porovnani.
            process.process(args.files[0], args.files[1])

        else:
            print("No input files specified.")


if __name__ == '__main__':
    main()
