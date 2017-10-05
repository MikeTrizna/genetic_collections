import requests
import pandas as pd
from lxml import objectify
import json
from collections import namedtuple
from operator import itemgetter


def ncbi_inst_search(search_term):

    search_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    search_params = {'term': search_term,
                     'db': 'biocollections',
                     'usehistory': 'y',
                     'retmax': 10000000,
                     'email': 'triznam@si.edu'}
    r = requests.get(search_url, params=search_params)
    search_results = objectify.fromstring(r.content)
    web_env = search_results.WebEnv.text
    query_key = search_results.QueryKey.text
    result_count = int(search_results.Count.text)
    print('{} matching results found.'.format(result_count))

    parsed_results = []
    if result_count > 0:
        print('Fetching biocollection entries.')
        ret_start = 0
        batch_size = 500
        while ret_start < result_count:
            url_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            params = {'db': 'biocollections',
                      'rettype': 'docsum',
                      'retmode': 'xml',
                      'query_key': query_key,
                      'WebEnv': web_env,
                      'retstart': ret_start,
                      'retmax': batch_size}
            r = requests.get(url_base, params=params)
            result_list = parse_biocollection_xml(r.content)
            parsed_results += result_list
            ret_start += batch_size
        for inst in parsed_results:
            icode = inst['Institution Code']
            gb_results = gb_search(inst_code = icode)
            inst['gb_count'] = gb_results.result_count
        parsed_results = sorted(parsed_results, key=itemgetter('gb_count'),
                                reverse=True)

    return parsed_results

def parse_biocollection_xml(xml):
    biocoll_url_base = 'https://www.ncbi.nlm.nih.gov/biocollections'
    xml_results = objectify.fromstring(xml)
    result_list = []
    for inst in xml_results.DocumentSummarySet.DocumentSummary:
        parsed_result = {}
        parsed_result['NCBI Link'] = '{}/{}'.format(biocoll_url_base,
                                                    inst.idbid.text)
        parsed_result['Institution Name'] = inst.iname.text
        parsed_result['Institution Code'] = inst.icode.text
        parsed_result['Country'] = inst.country.text
        parsed_result['Collection Type'] = inst.coltype.text
        result_list.append(parsed_result)
    return result_list

def gb_search(format='variable', **kwargs):

    search_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'

    if 'raw_query' in kwargs:
        search_term = kwargs['raw_query']
    elif 'inst_code' in kwargs or 'taxon' in kwargs:
        search_term_list = []
        if 'inst_code' in kwargs:
            inst_search = '"collection {}"[prop]'.format(kwargs['inst_code'])
            search_term_list.append(inst_search)
        if 'taxon' in kwargs:
            taxon_search = '"{}"[organism]'.format(kwargs['taxon'])
            search_term_list.append(taxon_search)
        search_term = ' AND '.join(search_term_list)
    else:
        print('You must provide something to search on.')
        return

    search_params = {'term': search_term,
                     'db': 'nuccore',
                     'usehistory': 'y',
                     'retmax': 10000000,
                     'email': 'triznam@si.edu'}
    r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params=search_params)
    search_results = objectify.fromstring(r.content)
    id_list = [id_entry.text for id_entry in search_results.IdList.iterchildren()]
    web_env = search_results.WebEnv.text
    query_key = search_results.QueryKey.text
    result_count = int(search_results.Count.text)
    translated_query = search_results.QueryTranslation.text

    if format == 'variable':
        Result = namedtuple('SearchResults',['web_env','query_key',
                                             'result_count','id_list'])
        result = Result(web_env, query_key, result_count, id_list)
        return result
    elif format == 'result_count':
        base_url = 'https://www.ncbi.nlm.nih.gov/nuccore/?term='
        entrez_url = base_url + requests.compat.quote_plus(translated_query)
        report = 'Your search found {} hits in GenBank'.format(result_count)
        print(report)
        url_report = 'You can see you search results online at {}'.format(entrez_url)
        print(url_report)
    elif format == 'id_list':
        if 'id_list_file' in kwargs:
            id_list_file = kwargs['id_list_file']
        else:
            id_list_file = 'gb_search_result_ids.txt'
        with open(id_list_file, 'w') as outfile:
            for id in id_list:
                outfile.write(id + '\n')
            report = '{} matching GenBank ids saved in {}'.format(result_count,
                                                                  id_list_file)
            print(report)
    else:
        print('Not a valid format')

    return
