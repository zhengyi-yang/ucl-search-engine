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


def get_google(query, rows=10, num=None):

    results = []
    num = min(rows, 100)

    url = "https://www.google.co.uk/search?q=" + query.replace(' ', '+') + \
          "+site:ucl.ac.uk&start={start}&num=" + str(num)

    useragent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    for i in xrange((rows - 1) / num + 1):
        r = requests.get(url.format(start=i * num),
                         headers={'User-agent': useragent})
        data = r.text
        soup = BeautifulSoup(data, "lxml")

        for result in soup.select('.g .r a'):
            domain = result.attrs['href']
            results.append(url_normalize(domain))

    if i == 0 and len(results) > num:
        results = results[len(results) - num:]

    return results[:rows]


def get_ucl(query, rows=10):
    results = []

    url = 'https://search2.ucl.ac.uk/s/search.html?query=' + query.replace(' ', '+') +  \
        '&collection=website-meta&profile=_website&tab=websites&submit=Go&start_rank={start}'

    i = 1
    while 1:
        r = requests.get(url.format(start=i))
        data = r.text
        soup = BeautifulSoup(data, "lxml")

        for result in soup.findAll('a', {'class': 'result__link'}):
            domain = result.text
            if urlparse.urlparse(domain).netloc.endswith('ucl.ac.uk'):
                results.append(url_normalize(domain))
                if len(results) >= rows:
                    return results
        i += 10


def get_solr(query, rows=10):
    url = 'http://138.68.161.137:8983/solr/files/select?wt=json&rows={rows}&fl=url&q=\"{query}\"'

    json_response = requests.get(url.format(
        rows=rows, query=query.replace(' ', '+'))).json()

    response = [url_normalize(r['url'][0])
                for r in json_response['response']['docs']]

    return response


def url_normalize(url):
    # TO DO
    return url


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('query', help='query')
    parser.add_argument('-r', nargs='?', dest='rows', type=int, default=10,
                        help='the number of results')
    args = parser.parse_args()

    query = args.query
    rows = args.rows

    solr_result = get_solr(query, rows)
    google_result = get_google(query, rows)
    url_result = get_ucl(query, rows)

    result = zip(range(1,rows+1),google_result, url_result, solr_result)

    print tabulate(result, headers=['','google', 'ucl', 'solr'], tablefmt='simple')
