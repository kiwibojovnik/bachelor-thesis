import requests

def test_http_header_manipulation():
    # Define the URL of the backend control server
    backend_url = "https://linkedein.com"

    # Define headers with variations in capitalization
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        # Send the HTTP request with headers to the backend control server
        response = requests.get(backend_url, headers=headers)

        # Check if received headers match the sent headers
        if response.headers == headers:
            print("No network components responsible for manipulation detected.")
        else:
            print("Network components responsible for manipulation may be present.")
    except requests.RequestException as e:
        print(f"Error: {e}")

# Call the function to test HTTP header manipulation
test_http_header_manipulation()
