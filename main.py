import csv

from tests import test_web_connection
# from tests import test_middle_box
# from tests import test_network_throttling
from utils import save_to_JSON


def main():
    # TODO:  Udělat pro každy vstup extra vystup
    urls_file = 'data/input_data/alexa_top_500_websites.csv'
    input_file = "alexa_top_500_websites.csv"
    output_file = 'data/output_data/website_test_results'#+'_'+input_file+'.json'
    output_content_folder = 'data/output_data/content_folder'

    with open(urls_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        website_list = [row[1] for row in reader]

    # Rozdělení seznamu URL na skupiny po 20
    for i in range(0, len(website_list), 10):
        batch = website_list[i:i + 10]
        print(batch)

        tester = test_web_connection.WebConnectivityTester(batch, output_content_folder, output_file)
        results = tester.run_tests()

        # Uložení výsledků do JSON souboru po každé skupině 20 URL
        print("Saving to JSon")
        save_to_JSON.process_results(results, output_file)

    # Testing the presence of the middle box

    # Vyzkoušení Yarrpbox


if __name__ == '__main__':
    main()
