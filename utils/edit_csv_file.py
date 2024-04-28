# Název: edit_csv_file.py
# Autor: Dalibor Kyjovský (xkyjov03)
# Datum: 11. dubna 2024
# Popis: Tento skript upravuje csv soubor tak, aby vždi jako první argument byla uvedena url adresa.
# Verze Pythonu: 3.9

# Importování potřebných knihoven
import csv
import os
import filecmp


def move_url_to_first_column(input_file):
    # Získej jméno původního souboru
    base_name = os.path.basename(input_file)
    directory = os.path.dirname(input_file)

    # Vytvoř název pomocného souboru
    output_file = os.path.join(directory, "helper_" + base_name)

    # Pokud existuje pomocný soubor a shoduje se s původním souborem, použij původní soubor
    if os.path.exists(output_file) and filecmp.cmp(input_file, output_file):
        print("Pomocný soubor již existuje a shoduje se s původním souborem, použije se původní soubor.")
        return input_file

    with open(input_file, 'r') as infile:
        reader = csv.reader(infile)

        # Přečti hlavičku
        header = next(reader)

        # Zjisti sloupec, který obsahuje URL nebo domény
        url_or_domain_index = None
        for i, column in enumerate(header):
            if 'url' in column.lower() or 'domain' in column.lower():
                url_or_domain_index = i
                break

        # Pokud sloupec nebyl nalezen, vypiš chybu a vrať se
        if url_or_domain_index is None:
            print("Nenalezen sloupec s URL nebo doménou.")
            return

        # Přesuň sloupec s URL nebo doménou na první pozici
        header.insert(0, header.pop(url_or_domain_index))

        with open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)

            # Zapiš novou hlavičku
            writer.writerow(header)

            # Procházej řádky a přesuň URL nebo doménu na první pozici v každém řádku
            for row in reader:
                if row:  # Kontrola, zda řádek není prázdný
                    url = row[url_or_domain_index]
                    # Odstranění lomítka z URL adresy, pokud je na konci
                    url = url.rstrip('/')
                    row[url_or_domain_index] = url
                    row.insert(0, url)
                writer.writerow(row)

    # Vrať cestu k pomocnému souboru
    return output_file

move_url_to_first_column("/Users/daliborkyjovsky/Documents/VUTFIT23/BP-2.0/bachelor-thesis/data/input_data/download.csv")
