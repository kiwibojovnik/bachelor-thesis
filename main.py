import argparse
import csv
from tests import test_web_connection, test_middle_box, test_DNS
from utils import save_to_JSON, sendFile


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

                with open(input_file, 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)
                    website_list = [row[1] for row in reader]

                output_file = f'data/output_data/website_test_results'  # {input_file.split(".")[0]}_results.json'
                output_content_folder = f'data/output_data/content_folder'

                # Rozdělení seznamu URL na skupiny po 10
                for index, i in enumerate(range(0, len(website_list), 10), start=1):
                    batch = website_list[i:i + 10]


                    # Tady nechci posilat cely batch, ale chci tam strakt vždycky jen jednu strankku
                    tester = test_web_connection.WebConnectivityTester(batch, output_content_folder)
                    results = tester.run_tests()

                    tester_middle_box = test_middle_box.CensorshipDetector(batch)
                    results_middle_box = tester_middle_box.run_tests

                    tester_dns = test_DNS.DNSAttackDetector(batch)
                    results_dns = tester_dns.run_tests()


                    # Uložení výsledků do JSON souboru po každé skupině 10 URL
                    print("Saving to JSON")

                    # !! Nebudu to řešit a appendnu ty results do jednoho ze všech funkcí...!!

                    save_to_JSON.process_results(results, output_file+str(i)+'.json')
                    save_to_JSON.process_results(results_middle_box, output_file+str(i)+'.json')
                    save_to_JSON.process_results(results_dns, output_file+str(i)+'.json')


                # TODO: posílát file do česka
                #  sendFile.sendFile(results_content)

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
