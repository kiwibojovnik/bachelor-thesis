import json


def compare_files(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    for url, details1 in data1.items():
        if url in data2:
            details2 = data2[url]

            dns_status1 = details1.get("DNS IPs")
            dns_status2 = details2.get("DNS IPs")
            print("1", dns_status1)
            print("2", dns_status2)

           # details1_filtered = {key: value for key, value in details1.items() if key != "Time"}
           # details2_filtered = {key: value for key, value in details2.items() if key != "Time"}

            if dns_status1 == dns_status2:
                print("1D", dns_status1)
                print("2D", dns_status2)

                print(f"Differences for URL: {url}")
                print("Details in File 1:")
              #  print(details1_filtered)
                print("Details in File 2:")
              #  print(details2_filtered)
                print()


file1 = 'results_belarusAll-80_18-04-2024_17-15.json'
file2 = 'results_czechAll-80_19-04-2024_00-36.json'

compare_files(file1, file2)
