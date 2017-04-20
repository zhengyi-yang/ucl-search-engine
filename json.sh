METHOD="TF-IDF"

reindex()
{
  curl "http://localhost:8983/solr/ucl/update?stream.body=<delete><query>*:*</query></delete>&commit=true"

  bin/nutch solrindex http://localhost:8983/solr/ucl crawl/crawldb crawl/segments/* -deleteGone

  curl "http://localhost:8983/solr/ucl/update?optimize=true"
}


curl -X POST -H 'Content-type:application/json' --data-binary '{
  "replace-field-type":{
     "name":"text_general",
     "class":"solr.TextField",
     "positionIncrementGap":"100",
     "multiValued":"true",
     "indexAnalyzer":{
        "tokenizer":{ 
           "class":"solr.StandardTokenizerFactory" },
        "filters":[
           { "class":"solr.StopFilterFactory",
             "words":"stopwords.txt",
             "ignoreCase":"true" },
           { "class":"solr.LowerCaseFilterFactory"},
           { "class":"solr.PorterStemFilterFactory" }]},
     "queryAnalyzer":{
        "tokenizer":{ 
           "class":"solr.StandardTokenizerFactory" },
        "filters": [
          { "class":"solr.StopFilterFactory",
            "words":"stopwords.txt",
            "ignoreCase":"true" },
          { "class":"solr.SynonymFilterFactory",
            "expand":"true",
            "ignoreCase":"true",
            "synonyms":"synonyms.txt" },
          { "class":"solr.LowerCaseFilterFactory"},
          { "class":"solr.PorterStemFilterFactory"}]}}
}' http://localhost:8983/solr/ucl/schema

reindex

python utils.py queries.txt -o ${METHOD}.json -r 100

curl -X POST -H 'Content-type:application/json' --data-binary '{
  "replace-field-type":{
     "name":"text_general",
     "class":"solr.TextField",
     "positionIncrementGap":"100",
     "multiValued":"true",
     "indexAnalyzer":{
        "tokenizer":{ 
           "class":"solr.StandardTokenizerFactory" },
        "filters":[
           { "class":"solr.StopFilterFactory",
             "words":"stopwords.txt",
             "ignoreCase":"true" },
           { "class":"solr.LowerCaseFilterFactory"}]},
     "queryAnalyzer":{
        "tokenizer":{ 
           "class":"solr.StandardTokenizerFactory" },
        "filters": [
          { "class":"solr.StopFilterFactory",
            "words":"stopwords.txt",
            "ignoreCase":"true" },
          { "class":"solr.SynonymFilterFactory",
            "expand":"true",
            "ignoreCase":"true",
            "synonyms":"synonyms.txt" },
          { "class":"solr.LowerCaseFilterFactory"}]}}
}' http://localhost:8983/solr/ucl/schema

reindex

python utils.py queries.txt -o ${METHOD}_no_stem.json -r 100

curl -X POST -H 'Content-type:application/json' --data-binary '{
  "replace-field-type":{
     "name":"text_general",
     "class":"solr.TextField",
     "positionIncrementGap":"100",
     "multiValued":"true",
     "indexAnalyzer":{
        "tokenizer":{ 
           "class":"solr.StandardTokenizerFactory" },
        "filters":[
           { "class":"solr.LowerCaseFilterFactory"},
           { "class":"solr.PorterStemFilterFactory" }]},
     "queryAnalyzer":{
        "tokenizer":{ 
           "class":"solr.StandardTokenizerFactory" },
        "filters": [
          { "class":"solr.SynonymFilterFactory",
            "expand":"true",
            "ignoreCase":"true",
            "synonyms":"synonyms.txt" },
          { "class":"solr.LowerCaseFilterFactory"},
          { "class":"solr.PorterStemFilterFactory"}]}}
}' http://localhost:8983/solr/ucl/schema

reindex

python utils.py queries.txt -o ${METHOD}_no_stop.json -r 100

curl -X POST -H 'Content-type:application/json' --data-binary '{
  "replace-field-type":{
     "name":"text_general",
     "class":"solr.TextField",
     "positionIncrementGap":"100",
     "multiValued":"true",
     "indexAnalyzer":{
        "tokenizer":{ 
           "class":"solr.StandardTokenizerFactory" },
        "filters":[
           { "class":"solr.LowerCaseFilterFactory"}]},
     "queryAnalyzer":{
        "tokenizer":{ 
           "class":"solr.StandardTokenizerFactory" },
        "filters": [
          { "class":"solr.SynonymFilterFactory",
            "expand":"true",
            "ignoreCase":"true",
            "synonyms":"synonyms.txt" },
          { "class":"solr.LowerCaseFilterFactory"}]}}
}' http://localhost:8983/solr/ucl/schema

reindex

python utils.py queries.txt -o ${METHOD}_no_stop_no_stem.json -r 100