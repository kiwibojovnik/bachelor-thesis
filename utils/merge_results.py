import json

def merge_records(records):
    merged_records = {}

    for record in records:
        page = record["page"]
        if page not in merged_records:
            merged_records[page] = record
        else:
            merged_records[page]["test_scripts"].extend(record["test_scripts"])

    return {"results": list(merged_records.values())}


with open("/Users/daliborkyjovsky/Documents/VUTFIT23/BP-2.0/bachelor-thesis/data/output_data/website_test_results0.json", "r") as file:
    data = json.load(file)


merged_data = merge_records(data["results"])

# Uložení sloučených dat zpět do souboru
with open("/Users/daliborkyjovsky/Documents/VUTFIT23/BP-2.0/bachelor-thesis/data/output_data/website_test_results0.json", "w") as file:
    json.dump(merged_data, file, indent=4)