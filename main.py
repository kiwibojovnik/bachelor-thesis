# Name: main.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: This script execute of various classes and functions for testing network connectivity and others.
# Python Version: 3.9

# Importing necessary libraries
import argparse
import csv
from tests import test_web_connection, test_middle_box, test_DNS
from utils import save_to_JSON, send_file, edit_csv_file


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some data.')
    parser.add_argument('-g', '--get', action='store_true', help='get data')
    parser.add_argument('-p', '--process', action='store_true', help='process data')
    parser.add_argument('-f', '--files', nargs='+', help='input files')
    return parser.parse_args()


def main():
    args = parse_arguments()

    if not (args.get or args.process):
        print("Specify either '-g' to get data or '-p' to process data.")
        return

    if args.get:
        if args.files:
            for input_file in args.files:
                print(f"Processing {input_file}...")

                edit_csv_file.move_url_to_first_column(input_file)

                with open(input_file, 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)
                    website_list = [row[0] for row in reader]

                print(input_file)
                output_filepath = f'data/output_data/'
                output_content_folder = f'data/output_data/content_folder'

                # Rozdělení seznamu URL na skupiny po 10
                for index, i in enumerate(range(0, len(website_list), 10), start=1):
                    batch = website_list[i:i + 10]

                    tester = test_web_connection.WebConnectivityTester(batch, output_content_folder)
                    results = tester.run_tests()

                    tester_middle_box = test_middle_box.CensorshipDetector(batch)
                    results_middle_box = tester_middle_box.run_tests

                    tester_dns = test_DNS.DNSAttackDetector(batch)
                    results_dns = tester_dns.run_tests()

                    # TODO: doupravit výstupní soubor a přidat čas a datum
                    output_filename = "results_{typ_testu}_dd-mm-rrrr_hh-mm"+str(i)+'.json'

                    print("Saving to JSON")
                    save_to_JSON.process_results(results, output_filepath+output_filename)
                    save_to_JSON.process_results(results_middle_box, output_filepath+output_filename)
                    save_to_JSON.process_results(results_dns, output_filepath+output_filename)


                    # Save file to this path with name of output file.
                    # TODO: Dat tu cestu do config souboru - muže se měnit podle serveru
                    remote_file_path = "/home/ms772qzljerv/bp/data/"+output_filename

                    # Posilani souboru na server do česka
                    send_file.send_file_via_ssh(output_filepath+output_filename, remote_file_path)

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
