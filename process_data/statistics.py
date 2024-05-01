# TODO: dodělat tohle nedělá to co má, ja chci at mi funkce vypisuje statistiky o cenzuře

import json


def count_censorship_types(data):
    censorship_stats = {}

    for file_name, file_data in data.items():
        for url, url_data in file_data.items():
            censorship_type = url_data.get("CENSORSHIP TYPE", "No censorship found")
            censorship_stats[censorship_type] = censorship_stats.get(censorship_type, 0) + 1

    return censorship_stats

