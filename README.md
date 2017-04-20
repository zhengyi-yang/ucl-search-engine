# UCL Search Engine

UCL IRDM 2017 Group Project - Option 1

We are using both of the open source IR packages below: 
- [solr](https://lucene.apache.org/solr) and [nutch](https://nutch.apache.org/)


## Nutch Crawling

1. Build nutch with `ant`.

2. Create a `urls` directory under `apache-nutch-1.12/runtime/local`.

3. Create `seed.txt` file under `urls` and put `http://www.cs.ucl.ac.uk/` into the file.

4. Create new crawldb by executing `bin/nutch inject crawl/crawldb urls` under the `apache-nutch-1.12/runtime/local` folder.

5. Start crawling with our `fetch.sh` script which is under the `nutch_shell` folder in the format like `./fetch.sh <Iterations>`.

6. Dedup nutch by `bin/nutch dedup crawl/crawldb`.

## PageRank

1. Generate webgraph by `bin/nutch webgraph -webgraphdb crawl/webgraphdb -segment crawl/segments/*`.

2. Execute PageRank by `bin/nutch org.apache.nutch.scoring.webgraph.PageRank -webgraphdb crawl/webgraphdb`.

3. Update score in crawldb by `bin/nutch scoreupdater -crawldb crawl/crawldb -webgraphdb crawl/webgraphdb`.

4. Put `scoring-link` into the `<value>` tag of the property with `<name>plugin.includes</name>` in `apache-nutch-1.12/runtime/local/conf/nutch-site.xml`. Or put it in `apache-nutch-1.12/conf/nutch-site.xml` and rebuild with ant.

5. Reindex solr.

## Integrate Solr with Nutch

1. Start solr server. 

2. Create a new core `ucl` with `bin/solr create -c ucl`.

3. Modify the schema or ucl by modifying `managed-schema.xml` and restart server or throuth the solr api. Change type of `content` to `text_general`.

4. Index with nutch by `bin/nutch solrindex http://localhost:8983/solr/ucl crawl/crawldb crawl/segments/* -normalize -deleteGone`. 
