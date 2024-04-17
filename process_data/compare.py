import json

def compare_results(results1, results2):
    censored_content = []

    for i in range(len(results1['results'])):
        for key, value in results1['results'][i].items():
            if key != 'test_scripts':
                if value != results2['results'][i][key]:
                    censored_content.append({
                        'page': results1['results'][i]['page'],
                        'key': key,
                        'value1': value,
                        'value2': results2['results'][i][key]
                    })

    return censored_content

# Load results from JSON files
with open('results1.json', 'r') as f:
    results1 = json.load(f)

with open('results2.json', 'r') as f:
    results2 = json.load(f)

# Compare the results
censored_content = compare_results(results1, results2)

# Print the potentially censored content
for entry in censored_content:
    print(f"Page: {entry['page']}, Key: {entry['key']}, Value1: {entry['value1']}, Value2: {entry['value2']}")
