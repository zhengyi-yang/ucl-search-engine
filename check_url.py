import logging
import requests
import json
from multiprocessing import Pool

def get(url, loop=0):
  if(loop > 5):
    return None
  try:
    response = requests.get(url, timeout=20, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'})
  except requests.exceptions.Timeout:
    logging.error('\tTimeout %d: \t%s' % (loop, url))
    return get(url, loop+1)
  except requests.exceptions.SSLError:
    logging.error('\tSSLError: \t%s' % url)
    return None
  except requests.exceptions.ConnectionError:
    logging.error('\tConnectionError %d: \t%s' % (loop, url))
    return get(url, loop+1)
  else:
    status_code = response.status_code
    if status_code == 200:
      if url != response.url:
        logging.warning('\tRedirection: \t%s %s %s' % (url, response.url, response.history))
      else:
        logging.info('\t200: \t%s' % (response.url))
      return response.url
    elif status_code == 301:
      logging.warning('\t301:\t%s %s %d' % (url, response.url, 301))
      return response.url
    else:
      logging.warning('\tUnknown: \t%s %d' % (url, status_code))
      return None

def get_url(url):
  response = get(url)
  status_code = response.status_code
  if status_code == 404:
    return status_code, url
  elif status_code == 302:
    return status_code, response.url
  return status_code, url

if __name__ == '__main__':
  logging.basicConfig(filename='log.log',level=logging.INFO)

  file_name = 'BM25.json'
  with open(file_name, 'r') as fp:
    json_file = json.load(fp)
  p = Pool(100)
  for query in json_file:
    google_urls = json_file[query]['google']
    urls2 = p.map(get, google_urls)
    json_file[query]['google'] = urls2

  with open('%s_filtered.json' % filename.split('.')[0], 'w') as outfile:
    json.dump(json_file, outfile)
    # print urls2