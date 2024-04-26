from googlesearch import search     #balíček google
from utils import reformat_url


def get_search_results(query):
    results = []

    for result in search(query, num=10, stop=10, pause=2):
        results.append(result)

    return results


def is_domain_in_results(address):

    domain = reformat_url.extract_domain(address)
    keyword = reformat_url.get_keyword(domain)

    results = get_search_results(keyword)

    if any(address in result for result in results):
        return "Match"

    return "No match"
