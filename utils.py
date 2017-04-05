# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 22:28:04 2017

@author: Zhengyi, Yuan
"""

import urlparse
import requests
import argparse

from bs4 import BeautifulSoup
from tabulate import tabulate


def get_google(query, max_rows=10, num=None):

    results = []
    num = min(max_rows, 100)

    url = "https://www.google.co.uk/search?q=" + query.replace(' ', '+') + \
          "+site:cs.ucl.ac.uk&start={start}&num=" + str(num)

    useragent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    for i in xrange((max_rows - 1) / num + 1):
        r = requests.get(url.format(start=i * num),
                         headers={'User-agent': useragent})
        data = r.text
        soup = BeautifulSoup(data, "lxml")

        found = soup.select('.g .r a')
        if not found:
            break

        for result in found:
            domain = result.attrs['href']
            results.append(url_normalize(domain))

        if i == 0 and len(results) > num:
            results = results[len(results) - num:]

    return results[:max_rows]


def get_ucl(query, max_rows=10):
    results = []

    url = 'https://search2.ucl.ac.uk/s/search.html?query=' + query.replace(' ', '+') +  \
        '&collection=website-meta&profile=_website&tab=websites&submit=Go&start_rank={start}'

    i = 1
    while 1:
        r = requests.get(url.format(start=i))
        data = r.text
        soup = BeautifulSoup(data, "lxml")

        found = soup.findAll('a', {'class': 'result__link'})
        if not found:
            break

        for result in found:
            domain = result.text
            if urlparse.urlparse(domain).netloc.endswith('cs.ucl.ac.uk'):
                results.append(url_normalize(domain))
                if len(results) >= max_rows:
                    return results
        i += 10

    return results


def get_solr(query, max_rows=10):
    url = 'http://138.68.161.137:8983/solr/ucl/select?wt=json&rows={max_rows}&fl=url&q=\"{query}\"'

    json_response = requests.get(url.format(
        max_rows=max_rows, query=query.replace(' ', '+'))).json()

    response = [url_normalize(r['url'][0])
                for r in json_response['response']['docs']]

    return response


def url_normalize(url):
    # TO DO
    return url


if __name__ == '__main__':
    import os
    import json
    from collections import defaultdict
    
    parser = argparse.ArgumentParser()
    parser.add_argument('query', help='query')
    parser.add_argument('-r', nargs='?', dest='rows', type=int, default=10,
                        help='the number of results')
    parser.add_argument('-o', nargs='?', dest='output', default=None,
                        help='output path to save the results in json')
    args = parser.parse_args()

    query = args.query
    rows = args.rows
    output = args.output

    if os.path.isfile(query):
        with open(query) as f:
            queries = f.readlines()
        queries = filter(lambda q: q and not q.startswith(
            '#'), map(str.strip, queries))
        print len(queries), ' queries'
    else:
        queries = [query]

    result_dict = defaultdict(dict)

    for i, q in enumerate(queries):
        result_dict[q]['solr'] = solr_result = get_solr(q, rows)
        result_dict[q]['google'] = google_result = get_google(q, rows)
        result_dict[q]['ucl'] = url_result = get_ucl(q, rows)

        result = zip(range(1, rows + 1), google_result,
                     url_result, solr_result)

        print 'search ', i, ': ', q
        print tabulate(result, headers=['', 'google', 'ucl', 'solr'], tablefmt='simple')
        print

    if output is not None:
        with open(output, 'w') as f:
            json.dump(result_dict, f)
