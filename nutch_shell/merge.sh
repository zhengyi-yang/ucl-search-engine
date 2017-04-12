#!/bin/bash

export NUTCH_HOME=../apache-nutch-1.12/runtime/local/
pushd $NUTCH_HOME

bin/nutch mergesegs crawl/merged_segments crawl/segments/20170404* -normalize -filter
rm -r crawl/segments/20170404*
mv crawl/merged_segments/* crawl/segments/
rmdir crawl/merged_segments/

popd