#!/bin/bash         

if [ -z "$1" ]; then
  count=1
else count=$1
fi

for i in $(seq 1 $count); do
  echo --- Iteration $i ---
  bin/nutch generate crawl/crawldb crawl/segments
  s1=`ls -d crawl/segments/2* | tail -1`
  bin/nutch fetch $s1
  bin/nutch parse $s1
  bin/nutch updatedb crawl/crawldb $s1
done