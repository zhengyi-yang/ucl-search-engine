package org.apache.nutch.scoring.webgraph;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.GnuParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionBuilder;
import org.apache.commons.cli.Options;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.util.StringUtils;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;
import org.apache.nutch.util.NutchConfiguration;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.SequenceFile;
import org.apache.hadoop.io.Writable;
import org.apache.hadoop.io.WritableUtils;
import org.apache.hadoop.io.ObjectWritable;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.nutch.util.FSUtils;
import org.apache.nutch.protocol.Content;

public class PageRank extends Configured implements Tool {
  private static final Logger LOG = LoggerFactory.getLogger(PageRank.class);
    
  public PageRank() {
    super();
  }

  public PageRank(Configuration conf) {
    super(conf);
  }    

  private HashMap<Text, Node> readNodes(Path webGraphDb) throws IOException
  {
    HashMap<Text, Node> nodeMap = new HashMap<Text, Node>();
    Configuration conf = getConf();
    FileSystem fs = FileSystem.get(conf);

    Path wgNodeDb = new Path(webGraphDb, WebGraph.NODE_DIR);
    Path nodeFile = new Path(wgNodeDb, "part-00000/data");

    SequenceFile.Reader reader = new SequenceFile.Reader(fs, nodeFile, conf);

    Text key = new Text();
    Node node = new Node();

    while (reader.next(key, node)) {
        LOG.debug(key + ":");
        LOG.debug("  inlink score: " + node.getInlinkScore());
        LOG.debug("  outlink score: " + node.getOutlinkScore());
        LOG.debug("  num inlinks: " + node.getNumInlinks());
        LOG.debug("  num outlinks: " + node.getNumOutlinks());

        Node outNode = WritableUtils.clone(node, conf);
        nodeMap.put(new Text(key), outNode);
    }

    reader.close();
    fs.close();
    return nodeMap;
  }

  private HashMap<Text, List<LinkDatum>> readOutlinks(Path webGraphDb) throws IOException
  {
    HashMap<Text, List<LinkDatum>> outlinkMap = new HashMap<Text, List<LinkDatum>>();
    Configuration conf = getConf();
    FileSystem fs = FileSystem.get(conf);

    Path wgNodeDb = new Path(webGraphDb, WebGraph.OUTLINK_DIR);
    Path outlinkFile = new Path(wgNodeDb, "part-00000/data");

    SequenceFile.Reader reader = new SequenceFile.Reader(fs, outlinkFile, conf);

    Text key = new Text();
    LinkDatum outlink = new LinkDatum();

    while (reader.next(key, outlink)) {
      if(!outlinkMap.containsKey(key)){
        outlinkMap.put(new Text(key), new ArrayList<LinkDatum>());
      }

      outlinkMap.get(key).add(WritableUtils.clone(outlink, conf));
    }

    reader.close();
    fs.close();
    return outlinkMap;
  }

  private void saveNodeDB(Path webGraphDb, HashMap<Text, Node> nodeMap) throws IOException
  {
    Configuration conf = getConf();
    FileSystem fs = FileSystem.get(conf);

    Path wgNodeDb = new Path(webGraphDb, WebGraph.NODE_DIR);
    Path nodeFile = new Path(wgNodeDb, "part-00000/data");
    Path newNodeFile = new Path(wgNodeDb, "part-00000/data2");

    SequenceFile.Writer writer = SequenceFile.createWriter(conf, 
        SequenceFile.Writer.file(newNodeFile), SequenceFile.Writer.keyClass(Text.class), 
        SequenceFile.Writer.valueClass(Node.class));

    for(Map.Entry<Text, Node> entry : nodeMap.entrySet())
    {
        Text key = entry.getKey();
        Node node = entry.getValue();

        writer.append(key, node);
    }
    writer.close();

    FSUtils.replace(fs, nodeFile, newNodeFile, true);
    fs.close();
  }

  private HashMap<Text, List<LinkDatum>> invertOutLinks(HashMap<Text, Node> nodeMap, HashMap<Text, List<LinkDatum>> outlinkMap)
  {
    Configuration conf = getConf();
    HashMap<Text, List<LinkDatum>> inlinkMap = new HashMap<Text, List<LinkDatum>>();
    for(Map.Entry<Text, Node> entry : nodeMap.entrySet())
    {
      Text key = entry.getKey();
      Node node = entry.getValue();

      List<LinkDatum> outlinks = outlinkMap.get(key);
      String fromUrl = key.toString();
      if(outlinks != null)
      {
        for(LinkDatum link : outlinks)
        {
          LinkDatum inlink = WritableUtils.clone(link, conf);
          inlink.setUrl(fromUrl);
          inlink.setScore(node.getOutlinkScore());

          Text toUrl = new Text(link.getUrl());

          LOG.debug("Inlink to " + toUrl);
          LOG.debug("from " + inlink);

          if(!inlinkMap.containsKey(toUrl))
          {
            inlinkMap.put(toUrl, new ArrayList<LinkDatum>());
          }
          inlinkMap.get(toUrl).add(inlink);
        }
      }
    }
    return inlinkMap;
  }

  private void calculateScore(HashMap<Text, Node> nodeMap, HashMap<Text, List<LinkDatum>> inlinkMap)
  {
    Configuration conf = getConf();
    Float dampingFactor = 0.85f;
    Integer totalNodes = nodeMap.size();

    for(Map.Entry<Text, Node> entry : nodeMap.entrySet())
    {
      Text key = entry.getKey();
      Node node = entry.getValue();

      Float score = (1 - dampingFactor)/totalNodes;

      List<LinkDatum> inlinks = inlinkMap.get(key);
      if(inlinks != null)
      {
        for(LinkDatum link : inlinks)
        {
          score += dampingFactor*link.getScore();
        }
      }

      node.setInlinkScore(score);
    }
  }

  private void readWebgraph(Path webGraphDb) throws IOException
  {
    HashMap<Text, Node> nodeMap = readNodes(webGraphDb);
    HashMap<Text, List<LinkDatum>> outlinkMap = readOutlinks(webGraphDb);

    Integer totalNodes = nodeMap.size();
    LOG.info("Total nodes: " + nodeMap.size());

    for(Map.Entry<Text, Node> entry : nodeMap.entrySet())
    {
        Node node = entry.getValue();
        node.setInlinkScore(1.0f / totalNodes);
    }

    LOG.info("Initialised the score of all nodes to " + 1.0f/totalNodes);

    for(int i=0 ; i<10 ; i++)
    {
      HashMap<Text, List<LinkDatum>> inlinkMap = invertOutLinks(nodeMap, outlinkMap);
      calculateScore(nodeMap, inlinkMap);
    }

    for(Map.Entry<Text, Node> entry : nodeMap.entrySet())
    {
        Node node = entry.getValue();
        LOG.debug(entry.getKey() + ":");
        LOG.debug("  inlink score: " + node.getInlinkScore());
        LOG.debug("  outlink score: " + node.getOutlinkScore());
        LOG.debug("  num inlinks: " + node.getNumInlinks());
        LOG.debug("  num outlinks: " + node.getNumOutlinks());
    }

    saveNodeDB(webGraphDb, nodeMap);
  }
    
  public static void main(String[] args) throws Exception {
    int res = ToolRunner.run(NutchConfiguration.create(), new PageRank(), args);
    System.exit(res);
  }

  /**
   * Runs the PageRank tool.
   */
  public int run(String[] args) throws Exception {

    Options options = new Options();
    OptionBuilder.withArgName("help");
    OptionBuilder.withDescription("show this help message");
    Option helpOpts = OptionBuilder.create("help");
    options.addOption(helpOpts);

    OptionBuilder.withArgName("webgraphdb");
    OptionBuilder.hasArg();
    OptionBuilder.withDescription("the web graph db to use");
    Option webgraphOpts = OptionBuilder.create("webgraphdb");
    options.addOption(webgraphOpts);

    CommandLineParser parser = new GnuParser();
    try {

      CommandLine line = parser.parse(options, args);
      if (line.hasOption("help") || !line.hasOption("webgraphdb")) {
        HelpFormatter formatter = new HelpFormatter();
        formatter.printHelp("PageRank", options);
        return -1;
      }

      String webGraphDb = line.getOptionValue("webgraphdb");

      readWebgraph(new Path(webGraphDb));
      return 0;
    } catch (Exception e) {
      LOG.error("LinkAnalysis: " + StringUtils.stringifyException(e));
      return -2;
    }
  }
}
