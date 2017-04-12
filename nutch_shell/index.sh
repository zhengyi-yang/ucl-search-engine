#!/bin/bash

export NUTCH_HOME=../apache-nutch-1.12/runtime/local/
pushd $NUTCH_HOME

bin/nutch invertlinks crawl/linkdb -dir crawl/segments/

bin/nutch solrindex http://localhost:8983/solr/ucl crawl/crawldb -linkdb crawl/linkdb/ crawl/segments/* -normalize -deleteGone

popd