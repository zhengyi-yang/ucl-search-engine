#!/bin/bash

bin/nutch mergesegs crawl/merged_segments crawl/segments/20170404* -normalize -filter
rm -r crawl/segments/20170404*
mv crawl/merged_segments/* crawl/segments/
rmdir crawl/merged_segments/