#!/bin/bash

bin/nutch invertlinks crawl/linkdb -dir crawl/segments/

bin/nutch solrindex http://localhost:8983/solr/ucl crawl/crawldb -linkdb crawl/linkdb/ crawl/segments/* -normalize -deleteGone