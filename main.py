# Name: main.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Main file of application.
# Python Version: 3.12.3


# Import necessary libraries
import argparse  # Import argparse module for parsing command-line arguments
import csv  # Import csv module for reading CSV files
import re  # Import re module for regular expressions
import os  # Import os module for operating system related functionalities
from datetime import datetime  # Import datetime class from datetime module
from module_get import start_analyze  # Import start_analyze module for starting the analysis
from utils import save_to_JSON, send_file, load_config  # Import necessary functions from utils module
from module_process import process_data  # Import process function from module_process module


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
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
                        help='Specify the index from which to start analyze. The value represents the number of cycles'
                             '(each cycle corresponds to a group of 10 URLs) to be skipped before testing begins.')
    parser.add_argument('-n', '--not_sending', action='store_true',  help='Specify if the results should not be sent '
                                                                          'to the server.')

    return parser.parse_args()


def extract_and_clean_filename(file_path):
    """
    Extracts the filename from the given path and removes special characters and spaces.

    Args:
        file_path (str): The path of the file.

    Returns:
        str: The cleaned filename.
    """
    # Extract filename without extension
    file_name_with_extension = os.path.basename(file_path)
    file_name = re.sub(r'\..*$', '', file_name_with_extension)

    # Remove special characters and spaces
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', file_name)

    return clean_name


def main():
    """
    Main function to execute the script.

    Parses command-line arguments and performs actions based on the provided arguments.
    If neither '-g' (get data) nor '-p' (process data) flags are specified, prompts the user to provide one.
    If '-g' is specified, retrieves data. If '-p' is specified, processes data.
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Check if neither '-g' nor '-p' is specified
    if not (args.get or args.process):
        print("Specify either '-g' to get data or '-p' to process data.")
        return

    # If '-g' is specified, retrieve data
    if args.get:
        # Check if input files are provided
        if args.files:
            for input_file in args.files:
                # Print the name of the input file being processed
                print("Processing " + input_file + "...")

                # Read website URLs from the input file
                with open(input_file, 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)
                    website_list = [row[0] for row in reader]

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

                    # Initialize WebConnectivityTester and run tests
                    tester = start_analyze.WebConnectivityTester(batch, output_content_folder, args.address.lower())
                    results = tester.run_tests()

                    date_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

                    # Print the name of the first input file again
                    print(args.files[0])
                    name = extract_and_clean_filename(args.files[0])

                    # Construct output filename
                    output_filename = "results_" + name + "_" + str(i) + "_" + date_time + ".json"

                    # Print message indicating saving to JSON file
                    print("Saving to JSON file: " + output_filename)

                    # Save test results to JSON file
                    save_to_JSON.save_test_results(results, output_filepath + output_filename)

                    # If sending is not disabled, send the file to the server
                    if not args.not_sending:
                        remote_file_path = load_config.load_credentials("server_path_for_files") + output_filename
                        send_file.send_file_via_ssh(output_filepath + output_filename, remote_file_path)

        else:
            # Print a message indicating no input files specified
            print("No input files specified.")

    # If '-p' is specified, process data
    elif args.process:
        if args.files and len(args.files) == 2:
            fold1, fold2 = args.files
            process_data.run_processing_data(fold1, fold2)
        else:
            # Print a message indicating incorrect number of folders specified
            print("Please specify exactly two folders (First is CZ, second is BY) for processing.")


if __name__ == '__main__':
    main()
