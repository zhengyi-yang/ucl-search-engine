#!/usr/bin/env python

import os
import requests
import json
import re
from multiprocessing import Pool
import BeautifulSoup

def get(url):
  try:
    response = requests.get(url, timeout=20, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'})
  except requests.exceptions.Timeout:
    return 'TIMEOUT'
  except requests.exceptions.SSLError:
    return None
  except requests.exceptions.ConnectionError:
    return 'TIMEOUT'
  else:
    status_code = response.status_code
    if status_code == 200:
      if url == response.url:
        content = response.text
        soup  = BeautifulSoup.BeautifulSoup(content)
        meta=soup.find("meta",attrs={"http-equiv":"refresh"})
        if meta != None:
          m = re.search('((url)|(URL))=(.*)', meta['content'])
          new_url = m.group(4).strip()
          if 'http' not in new_url:
            new_url = url + new_url
          return new_url
        else:
          return response.url
      else:
        return response.url
    elif status_code == 301:
      return response.url
    else:
      return None

def update_dict(urls, dic):
  get_urls = []
  for url in urls:
    if (url not in dic) or (dic[url] == 'TIMEOUT'):
      get_urls.append(url)
  if get_urls:
    print len(get_urls)
    pool = Pool(len(get_urls))
    new_urls = pool.map(get, get_urls)
    zip_url = zip(get_urls, new_urls)

    from pprint import pprint
    pprint(zip_url)

    for e in zip_url:
      dic[e[0]] = e[1]

    pool.close()

  return dic

if __name__ == '__main__':
  if os.path.exists('dict.json'):
    with open('dict.json', 'r') as fp:
      url_dict = json.load(fp)
  else:
    url_dict = dict()

  file_name = 'BM25.json'
  with open(file_name, 'r') as fp:
    json_file = json.load(fp)

  google_urls = []
  for query in json_file:
    google_urls += json_file[query]['google']

  url_dict = update_dict(google_urls, url_dict)

  
  with open('dict.json', 'w') as fp:
    json.dump(url_dict, fp)

  for query in json_file:
    filtered_urls = [url_dict[url] for url in json_file[query]['google']]
    filtered_urls = [url for url in filtered_urls if url!=None and url!='TIMEOUT']
    filtered_urls = [url for url in filtered_urls if re.match('^https?://([a-z0-9]*\.)*cs.ucl.ac.uk/', url)!= None]
    json_file[query]['google'] = filtered_urls

  with open('%s_filtered.json' % file_name.split('.')[0], 'w') as fp:
    json.dump(json_file, fp)

