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


def run_merging(filename):
    with open(filename, "r") as f:
        data = json.load(f)

    merged_data = merge_records(data["results"])

    # Uložení sloučených dat zpět do souboru
    with open(filename, "w") as f:
        json.dump(merged_data, f, indent=4)
