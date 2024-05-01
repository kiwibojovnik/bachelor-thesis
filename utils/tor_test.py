censorship_rules = {
    'Podvržení obsahu HTTP': {
        'Content Length': {
            'CZ': lambda x: x,
            'BY': lambda y: y,
            'comparison': lambda x, y: abs(x - y) > 0.9 * max(x, y),
        },
    }
}

# Předpokládáme hodnoty pro délky obsahu pro CZ a BY
content_length_CZ = 71608
content_length_BY = 71635

# Získání funkcí pro zpracování délek obsahu
func_CZ = censorship_rules['Podvržení obsahu HTTP']['Content Length']['CZ']
func_BY = censorship_rules['Podvržení obsahu HTTP']['Content Length']['BY']
comparison_func = censorship_rules['Podvržení obsahu HTTP']['Content Length']['comparison']

# Vypočtení x a y
x = func_CZ(content_length_CZ)
y = func_BY(content_length_BY)

# Výsledek porovnání
result = comparison_func(x, y)

# Vypsání x, y a výsledku porovnání
print("x =", x)
print("y =", y)
print("Porovnání výsledku:", result)
