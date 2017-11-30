import requests
# import pandas as pd
from lxml import objectify
# import json
from collections import namedtuple
from operator import itemgetter
import re


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
    r = requests.get(search_url, params=search_params)
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

def gb_fetch_from_id_list(id_list, batch_size=500):
    """
    Orchestrates making calls to the NCBI efetch service, and passes off the 
    XML to the parse_fetch_results function. 
    
    Parameters
    ----------

    batch_size : int, the number of results to request at a time -- the higher
                      the better, but too large of a result set causes errors
    
    Returns
    -------
    parsed_results : list of dicts, all results
    """

    result_count = len(id_list)
    parsed_results = []
    i = 0
    while i < result_count:
        list_for_url = ','.join(id_list[i : i+batch_size])
        url_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {'db': 'nuccore',
                  'rettype': 'gb',
                  'retmode': 'xml',
                  'id': list_for_url}
        r = requests.get(url_base, params=params)
        result_list = gb_parse_xml_fetch_results(r.content)
        parsed_results += result_list

        i += batch_size
    return parsed_results

def gb_parse_xml_fetch_results(gb_xml):
    target_pieces = ['specimen_voucher','country','lat_lon','collection_date',
                     'collected_by','identified_by','bio_material',
                     'culture_collection','PCR_primers']
    result_list = []
    huge_parser = objectify.makeparser(huge_tree=True)
    xml_results = objectify.fromstring(gb_xml, huge_parser)
    for gb in xml_results.GBSeq:
        result = {}
        try:
            result['accession'] = gb['GBSeq_primary-accession'].text
            result['scientific_name'] = gb['GBSeq_organism'].text
            result['publish_date'] = gb['GBSeq_create-date'].text
            result['update_date'] = gb['GBSeq_update-date'].text
            result['keyword'] = ''
            if hasattr(gb, 'GBSeq_xrefs'):
                for xref in gb['GBSeq_xrefs']['GBXref']:
                    if xref['GBXref_dbname'].text == 'BioProject':
                        result['bioproject'] = xref['GBXref_id'].text
                    elif xref['GBXref_dbname'].text == 'Sequence Read Archive':
                        result['sra'] = xref['GBXref_id'].text
                    elif xref['GBXref_dbname'].text == 'BioSample':
                        result['biosample'] = xref['GBXref_id'].text
            if hasattr(gb, 'GBSeq_keywords'):
                for keyword in gb['GBSeq_keywords'].iterchildren():
                    if keyword.text == 'BARCODE':
                        result['keyword'] = 'BARCODE'
            result['seq_len'] = gb.GBSeq_length.text
            for ref in gb['GBSeq_references']['GBReference']:
                if hasattr(ref, 'GBReference_title'):
                    if ref['GBReference_title'] == 'Direct Submission':
                        if hasattr(ref, 'GBReference_authors'):
                            result['submit_authors'] = '; '.join([author.text for author in ref['GBReference_authors']['GBAuthor']])
                        submit_inst_text = ref['GBReference_journal'].text
                        inst_split = re.split('[\(\)]',submit_inst_text)
                        result['submit_date'] = inst_split[1]
                        result['submit_inst'] = inst_split[2]
            for feature in gb['GBSeq_feature-table'].iterchildren():
                if feature.GBFeature_key.text == 'source':
                    for feature_qual in feature.GBFeature_quals.iterchildren():
                        if feature_qual.GBQualifier_name.text == 'db_xref':
                            if 'taxon' in feature_qual.GBQualifier_value.text:
                                result['taxid'] = str(feature_qual.GBQualifier_value.text.split(":")[1])
                            elif 'BOLD' in feature_qual.GBQualifier_value.text:
                                result['bold_id'] = str(feature_qual.GBQualifier_value.text.split(":")[1])
                        elif feature_qual.GBQualifier_name.text in target_pieces:
                            if feature_qual.GBQualifier_name.text in result:
                                result[feature_qual.GBQualifier_name.text] += ';' + str(feature_qual.GBQualifier_value.text)
                            else:
                                result[feature_qual.GBQualifier_name.text] = str(feature_qual.GBQualifier_value.text)
        except:
            problem_child = gb['GBSeq_primary-accession'].text
            print('{} could not be parsed'.format(problem_child))
        result_list.append(result)
    return result_list

def ncbi_taxonomy(gb_fetch_results, batch_size=500):
    """
    Orchestrates making calls to the NCBI efetch service, querying the NCBI
    Taxonomy database for a list of NCBI taxids. Passes off the XML to the
    ncbi_parse_taxonomy_xml function.
    
    Parameters
    ----------
    gb_fetch_results : list of dicts, the unprocessed results of 
                                      a previous gb_fetch_from_id_list
    
    batch_size : int, the number of results to request at a time -- the higher
                      the better, but too large of a result set causes errors
    
    Returns
    -------
    parsed_results : list of dicts, all results
    """
    try:
        taxid_list = list(set([x['taxid'] for x in gb_fetch_results]))
    except KeyError:
        print('Must provide gb_fetch_from_id_list results.')
        return
    result_count = len(taxid_list)
    parsed_results = []
    i = 0
    while i < result_count:
        taxids = ','.join(taxid_list[i : i+batch_size])
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {'db': 'taxonomy',
                  'retmode': 'xml',
                  'id': taxids}
        r = requests.get(fetch_url, params=params)
        result_list = ncbi_parse_taxonomy_xml(r.content)
        parsed_results += result_list

        i += batch_size
    return parsed_results

def ncbi_parse_taxonomy_xml(tax_xml):
    result_keys = ['taxid', 'scientific_name', 'rank', 'kingdom', 'phylum', 
                   'class', 'order', 'family', 'genus', 'full_lineage']
    result_list = []
    huge_parser = objectify.makeparser(huge_tree=True)
    xml_results = objectify.fromstring(tax_xml, huge_parser)
    for tx in xml_results.Taxon:
        result = {}
        try:
            result['taxid'] = tx['TaxId'].text
            result['scientific_name'] = tx['ScientificName'].text
            result['rank'] = tx['Rank'].text
            if hasattr(tx, 'Lineage'):
                result['full_lineage'] = tx['Lineage'].text
            if hasattr(tx, 'LineageEx'):
                for child in tx['LineageEx'].iterchildren():
                    if child.Rank.text in result_keys:
                        result[child.Rank.text] = child.ScientificName.text       
        except:
            problem_child = tx['TaxId'].text
            print('{} could not be parsed'.format(problem_child))
        result_list.append(result)
    return result_list
