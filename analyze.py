import requests
import time


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


def test_website_availability(urls_file, output_file):
    try:
        with open(urls_file, 'r') as file:
            urls = file.read().splitlines()

        with open(output_file, 'a') as output:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            output.write(f"Results for {timestamp}:\n")

            for url in urls:
                try:
                    response = requests.get(url)
                    status_code = response.status_code
                    output.write(f"{url}: Status code {status_code}\n")
                except requests.RequestException:
                    output.write(f"{url}: Error - Unable to access\n")

    except FileNotFoundError:
        print(f"File {urls_file} not found.")





def main():
    urls_file = 'blocked_websites.txt'  # Replace with your file containing URLs
    output_file = 'website_test_results.txt'  # Replace with your desired output file

    test_website_availability(urls_file, output_file)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
