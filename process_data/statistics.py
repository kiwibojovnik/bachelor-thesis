#TODO: dodělat tohle nedělá to co má, ja chci at mi funkce vypisuje statistiky o cenzuře

def count_censorship_occurrences(data):
    # Initialize a dictionary to hold counts of each censorship type
    censorship_counts = {}

    # Iterate over the JSON data
    for file, content in data.items():
        for url, details in content.items():
            # Check for HTTP Status as an indicator of censorship
            if 'HTTP Status' in details:
                file1_status = details['HTTP Status']['File1']
                file2_status = details['HTTP Status']['File2']
                # Define censorship based on HTTP status code
                if file1_status != file2_status:
                    censorship_type = 'HTTP Status Code Mismatch'
                    censorship_counts[censorship_type] = censorship_counts.get(censorship_type, 0) + 1

            # Add other checks for different types of censorship here
            # ...

    # Print the statistics
    for censorship_type, count in censorship_counts.items():
        print(f"{censorship_type}: {count}")