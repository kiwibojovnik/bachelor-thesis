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
from utils import save_to_JSON, send_file, edit_csv_file, load_config


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some data.')
    parser.add_argument('-g', '--get', action='store_true', help='get data')
    parser.add_argument('-p', '--process', action='store_true', help='process data')
    parser.add_argument('-f', '--files', nargs='+', help='input files')
    parser.add_argument('-n', '--filename', help='name of the output file')
    parser.add_argument('-a', '--address', help='preferred ipv4 or ipv6')

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
            for input_file in args.files:
                # TODO: dodělat tenhle modul
                print("Processing data.")
        else:
            print("No input files specified.")


if __name__ == '__main__':
    main()
