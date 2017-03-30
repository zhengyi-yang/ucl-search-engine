# UCL Search Engine



We are using both of the open source IR packages below: 
- [solr](https://lucene.apache.org/solr) and [nutch](https://nutch.apache.org/)


## Nutch Crawling

1. Insert the following code into **nutch-site.xml** 

```xml
<property>
 <name>http.agent.name</name>
 <value>My UCL Spider</value>
</property>

<property>
  <name>fetcher.threads.per.queue</name>
  <value>5</value>
  <description>This number is the maximum number of threads that
    should be allowed to access a queue at one time. Setting it to 
    a value > 1 will cause the Crawl-Delay value from robots.txt to
    be ignored and the value of fetcher.server.min.delay to be used
    as a delay between successive requests to the same server instead 
    of fetcher.server.delay.
   </description>
</property>

```

2. Replace the last line in **regex-urlfilter.txt** to

```
+^http://([a-z0-9]*\.)*ucl.ac.uk/
```


3. Create **<NUTCH_HOME>/urls/seed.txt** and add `http://www.ucl.ac.uk/`.

4. Set `JAVA_HOME`.

5. Run `bin/crawl urls/ crawl/ <NUM_OF_ROUNDS>`


## LinkRank to PageRank

Insert the following code into **nutch-site.xml**

```xml
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


