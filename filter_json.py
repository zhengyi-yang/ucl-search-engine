#!/usr/bin/env python

import os
import requests
import json
import re
import argparse
from multiprocessing import Pool
from pprint import pprint
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
  except requests.exceptions.TooManyRedirects:
    return 'TooManyRedirects'
    # raise
  else:
    status_code = response.status_code
    if status_code == 200:
      if url == response.url:
        if re.match('^https?:\/\/.*\/$', url) != None:
          content = response.text
          soup  = BeautifulSoup.BeautifulSoup(content)
          meta=soup.find("meta",attrs={"http-equiv":"refresh"})
          if meta != None:
            m = re.search('((url)|(URL))=(.*)', meta['content'])
            new_url = m.group(4).strip()
            if 'http' not in new_url:
              new_url = url + new_url
            return new_url
      return response.url
    elif status_code == 301:
      return response.url
    else:
      return None

def update_dict(urls, json_dict):
  if os.path.exists(json_dict):
    with open(json_dict, 'r') as fp:
      dic = json.load(fp)
  else:
    dic = dict()

  get_urls = [url for url in urls if (url not in dic) or (dic[url] == 'TIMEOUT')]

  if get_urls:
    print len(get_urls)
    pool_size = len(get_urls)
    if pool_size > 100:
      pool_size = 100
    pool = Pool(pool_size)

    for i in range(0, len(get_urls), 100):
      url_slice = get_urls[i:i+100]
      new_urls = pool.map(get, url_slice)
      zip_url = zip(url_slice, new_urls)
      pprint(zip_url)
      for e in zip_url:
        dic[e[0]] = e[1]
      with open(json_dict, 'w') as fp:
        json.dump(dic, fp)

    pool.close()

  # with open(json_dict, 'w') as fp:
  #   json.dump(url_dict, fp)

  return dic

def main(file_name):
  json_dict = 'dict.json'

  with open(file_name, 'r') as fp:
    json_file = json.load(fp)

  unfiltered_urls = []
  for query in json_file:
    unfiltered_urls += [ ('http://%s' % url) for url in json_file[query] if not url.startswith('http')]

  url_dict = update_dict(unfiltered_urls, json_dict)

  inject_urls = []

  for query in json_file:
    original_number = len(json_file[query]) 
    filtered_urls = [url_dict[url] for url in json_file[query]]
    filtered_urls = [url for url in filtered_urls if url!=None and url!='TIMEOUT' and url!='TooManyRedirects']
    filtered_urls = [url for url in filtered_urls if re.match('^https?://([a-z0-9]*\.)*cs.ucl.ac.uk/', url)!= None]

    # filtered_urls = [ ('http://%s' % url) for url in filtered_urls if not url.startswith('http')]

    print query, 'Original: %d , Filtered: %d' % (original_number, len(json_file[query]))

    json_file[query] = filtered_urls[:100]
    inject_urls += filtered_urls


  with open('inject.txt','w') as fp:
    for url in inject_urls:
      fp.write('%s\n' % url)

  with open('%s_filtered.json' % file_name.split('.')[0], 'w') as fp:
    json.dump(json_file, fp)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('json', help='json file')
  args = parser.parse_args()
  file_name = args.json
  main(file_name)

  

