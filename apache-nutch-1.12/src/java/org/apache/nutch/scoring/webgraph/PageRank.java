package org.apache.nutch.scoring.webgraph;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.List;
import java.util.ArrayList;

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
import org.apache.nutch.util.FSUtils;
import org.apache.nutch.protocol.Content;

public class PageRank extends Configured implements Tool {
  private static final Logger LOG = LoggerFactory
      .getLogger(PageRank.class);
    
  /**
   * Default constructor.
   */
  public PageRank() {
    super();
  }

  /**
   * Configurable constructor.
   */
  public PageRank(Configuration conf) {
    super(conf);
  }    

  private void readNodes(Path webGraphDb) throws IOException
  {
    Path linkRank = new Path(webGraphDb, "linkrank");
    Configuration conf = getConf();
    FileSystem fs = FileSystem.get(conf);

    Path wgNodeDb = new Path(webGraphDb, WebGraph.NODE_DIR);
    Path nodeFile = new Path(wgNodeDb, "part-00000/data");

    Path newNodeFile = new Path(wgNodeDb, "part-00000/data2");

    SequenceFile.Reader reader = new SequenceFile.Reader(fs, nodeFile, conf);

    SequenceFile.Writer writer = SequenceFile.createWriter(conf, 
      SequenceFile.Writer.file(newNodeFile), SequenceFile.Writer.keyClass(Text.class), 
      SequenceFile.Writer.valueClass(Node.class));

    Text key = new Text();
    Node node = new Node();

    Integer count = 0;

    while (reader.next(key, node)) {
        count += 1;

        System.out.println(key + ":");
        System.out.println("  inlink score: " + node.getInlinkScore());
        System.out.println("  outlink score: " + node.getOutlinkScore());
        System.out.println("  num inlinks: " + node.getNumInlinks());
        System.out.println("  num outlinks: " + node.getNumOutlinks());

        Node outNode = WritableUtils.clone(node, conf);
        outNode.setInlinkScore(1.0f);

        writer.append(new Text(key), outNode);
    }
    System.out.println("Total Nodes: " + count);
    reader.close();
    writer.close();

    FSUtils.replace(fs, nodeFile, newNodeFile, true);
    fs.close();
  }

  private void readOutlinks(Path webGraphDb) throws IOException
  {
    Configuration conf = getConf();
    FileSystem fs = FileSystem.get(conf);

    Path wgNodeDb = new Path(webGraphDb, WebGraph.OUTLINK_DIR);
    Path outlinkFile = new Path(wgNodeDb, "part-00000/data");

    SequenceFile.Reader reader = new SequenceFile.Reader(fs, outlinkFile, conf);

    Text key = new Text();
    LinkDatum outlinks = new LinkDatum();

    Integer count = 0;

    while (reader.next(key, outlinks)) {
        count += 1;

        System.out.println(key + ":");
        System.out.println(outlinks);
    }

    reader.close();
    fs.close();
  }


  private void readWebgraph(Path webGraphDb) throws IOException
  {
    readNodes(webGraphDb);
    readOutlinks(webGraphDb);
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
