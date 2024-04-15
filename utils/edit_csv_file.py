# Název: edit_csv_file.py
# Autor: Dalibor Kyjovský (xkyjov03)
# Datum: 11. dubna 2024
# Popis: Tento skript upravuje csv soubor tak, aby vždi jako první argument byla uvedena url adresa.
# Verze Pythonu: 3.9

# Importování potřebných knihoven
import csv

# TODO: Někde je chyba. Na daddy to hazelo chypu s pop.
def move_url_to_first_column(input_file):
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

        with open(input_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)

            # Zapiš novou hlavičku
            writer.writerow(header)

            # Procházej řádky a přesuň URL nebo doménu na první pozici v každém řádku
            for row in reader:
                if row:  # Kontrola, zda řádek není prázdný
                    row.insert(0, row.pop(url_or_domain_index))
                writer.writerow(row)
