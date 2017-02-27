# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 22:28:04 2017

@author: Zhengyi
"""

import urlparse
import requests

from bs4 import BeautifulSoup

def getGoogle(query, max_result=100):
    return WebRanker(query, max_result).getGoogle()


def getUcl(query, max_result=100):
    return WebRanker(query, max_result).getUcl()


class WebRanker(object):

    def __init__(self, query, max_result=100):
        self.query = query
        self.max_result = max_result

    def getGoogle(self):
        results = []

        url = "https://www.google.co.uk/search?q=" + \
            self.query.replace(' ', '+') + \
            '+site:ucl.ac.uk' + \
            "&start=%d" + '&num=' + str(self.max_result)

        useragent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        for i in xrange((self.max_result + 99) / 100):
            r = requests.get(url % (i * 100), timeout=10,
                             headers={'User-agent': useragent})
            data = r.text
            soup = BeautifulSoup(data, "lxml")

            for result in soup.select('.g .r a'):
                domain = result.attrs['href']
                parsedDomain = urlparse.urlparse(domain)
                results.append(parsedDomain.netloc + parsedDomain.path)
            
            if i==0 and len(results)>100:
                results=results[len(results)-100:]

        return results[:self.max_result]

    def getUcl(self):
        results = []

        url = 'https://search2.ucl.ac.uk/s/search.html?query=' + \
            self.query.replace(' ', '+') +  \
            '&collection=website-meta&profile=_website&tab=websites&submit=Go' + \
            '&start_rank=%d'

        useragent = 'Mozilla/5.0'
        for i in xrange((self.max_result + 9) / 10):

            r = requests.get(url % (i * 10 + 1),
                             timeout=10, headers={'User-agent': useragent})
            data = r.text
            soup = BeautifulSoup(data, "lxml")

            for result in soup.findAll('a', {'class': 'result__link'}):
                domain = result.text
                parsedDomain = urlparse.urlparse(domain)
                results.append(parsedDomain.netloc + parsedDomain.path)

        return results[:self.max_result]
