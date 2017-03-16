# UCL Search Engine


We may use one of the following open source IR package: 
- [solr](https://lucene.apache.org/solr) and [nutch](https://nutch.apache.org/)

## LinkRank to PageRank

Insert the following code into nutch-site.xml 

```
<property>
  <name>link.ignore.internal.host</name>
  <value>false</value>
  <description>Ignore outlinks to the same hostname.</description>
</property>

<property>
  <name>link.ignore.internal.domain</name>
  <value>false</value>
  <description>Ignore outlinks to the same domain.</description>
</property>

```

## Integrate Solr with Nutch

Example: `bin/nutch solrindex http://localhost:8983/solr/<core_name> crawl/crawldb -linkdb crawl/linkdb/ crawl/segments/* -normalize -deleteGone` 


