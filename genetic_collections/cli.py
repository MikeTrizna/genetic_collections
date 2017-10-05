import argparse
import genetic_collections as gc
import json


def ncbi_inst_search():
    parser = argparse.ArgumentParser(description='Search NCBI BioCollections database.')
    parser.add_argument('search_term',
                        help='Term to search database with.')
    options = parser.parse_args()
    search_results = gc.ncbi_inst_search(options.search_term)
    print(json.dumps(search_results, indent=2))
    return

def gb_search():
    parser = argparse.ArgumentParser(description='Search NCBI GenBank database.')
    parser.add_argument('-f', dest='format',
                        choices=['result_count', 'id_list'],
                        default='result_count',
                        help='Format to return search results.')
    parser.add_argument('-r', dest='raw_query',
                        help='Full query already prepared')
    parser.add_argument('-inst_code', dest='inst_code',
                        help='Institution code to seach in GenBank.')
    parser.add_argument('-taxon', dest='taxon',
                        help='Taxonomic name to seach in GenBank.')
    options = vars(parser.parse_args())
    search_term_keywords = ['raw_query','inst_code','taxon']
    search_terms = {}
    for term in search_term_keywords:
        if options[term] is not None:
            search_terms[term] = options[term]
    gc.gb_search(format=options['format'], **search_terms)
    return


if __name__ == "__main__":
    print('ok')
