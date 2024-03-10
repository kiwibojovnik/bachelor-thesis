import requests
import socket  # Add this line to import the socket module
import time
import csv
import os


def dns_lookup(website):
    try:
        ip_address = socket.gethostbyname(website)
        return ip_address
    except socket.gaierror:
        return "N/A"


def tcp_connection(ip_address):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        if sock.connect_ex((ip_address, 80)) == 0:
            return 'Response received'
        else:
            return 'No response'
        sock.close()
    except:
        return "N/A"


def ping_test(url):
    try:
        ping_response = os.system("ping -c 1 " + url)
        return 'Success' if ping_response == 0 else 'Failure'
    except:
        return "N/A"


class WebsiteTester:
    def __init__(self, url_list, output_file):
        self.output_folder = "html_content"
        self.urls = url_list
        self.output_file = output_file

    def test_website_availability(self):
        with open(self.output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['TIME', 'URL', 'DNS', 'SYNADDR', 'PING', 'RESPONSE', 'CONTENT'])
            for website in self.urls:
                print(website + "\n")
                try:
                    start_time = time.time()

                    ip_address = dns_lookup(website)
                    syn_response = tcp_connection(ip_address)
                    ping_success = ping_test(website)

                    # Získání dokumentu pomocí metody GET
                    response = requests.get('http://' + website)

                    end_time = time.time()

                    duration = round(end_time - start_time, 2)

                    # Uložení obsahu stránky do souboru ve vedlejší složce
                    filename = website + "_content.html"
                    with open(os.path.join(self.output_folder, filename), 'w', encoding='utf-8') as content_file:
                        content_file.write(response.text)


                    # Uložení výsledků do souboru
                    writer.writerow([duration, website, ip_address, syn_response, ping_success, response, "html_content/"+filename])

                except Exception as e:
                    # Pokud dojde k chybě při testování dostupnosti
                    writer.writerow([website, "N/A", "N/A", "N/A"])
                    print(f"Chyba při testování {website}: {e}")


def main():
    urls_file = 'alexa_top_10_websites.csv'  # Replace with your file containing URLs
    output_file = 'website_test_results.csv'  # Replace with your desired output file

    with open(urls_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        website_list = [row[1] for row in reader]

    tester = WebsiteTester(website_list, output_file)
    tester.test_website_availability()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
