package org.apache.nutch.scoring.webgraph;

import java.lang.invoke.MethodHandles;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.GnuParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionBuilder;
import org.apache.commons.cli.Options;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.util.StringUtils;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;
import org.apache.nutch.util.NutchConfiguration;


public class PageRank extends Configured implements Tool {
  private static final Logger LOG = LoggerFactory
      .getLogger(MethodHandles.lookup().lookupClass());
    
    
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
    
  /**
   * Runs the complete link analysis job. The complete job determins rank one
   * score. Then runs through a given number of invert and analyze iterations,
   * by default 10. And finally replaces the NodeDb in the WebGraph with the
   * link rank output.
   * 
   * @param webGraphDb
   *          The WebGraph to run link analysis on.
   * 
   * @throws IOException
   *           If an error occurs during link analysis.
   */
  public void analyze(Path webGraphDb) throws IOException {
    
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
      LOG.info("WebGraphDB: " + webGraphDb);
      //analyze(new Path(webGraphDb));
      return 0;
    } catch (Exception e) {
      LOG.error("LinkAnalysis: " + StringUtils.stringifyException(e));
      return -2;
    }
  }
}
