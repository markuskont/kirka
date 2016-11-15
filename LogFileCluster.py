#!/usr/bin/env python3
# coding: utf-8
# see - http://ristov.github.io/logcluster/

import hashlib
import argparse
import json
from algorithms.LogCluster import *
from common.print import *

MAN_SUPPORT = """
Find clusters (line patterns) that match at least <support> lines in input
file(s). Each line pattern consists of word constants and variable parts,
where individual words occur at least <support> times in input files(s).
For example, --support=1000 finds clusters (line patterns) which consist
of words that occur at least in 1000 log file lines, with each cluster
matching at least 1000 log file lines.
"""

MAN_INPUT = """
Find clusters from files matching the <file_pattern>, where each cluster
corresponds to some line pattern, and print patterns to standard output.
For example, --input=/var/log/remote/*.log finds clusters from all files
with the .log extension in /var/log/remote.
"""

MAN_AGGRSUP = """
If this option is given, for each cluster candidate other candidates are
identified which represent more specific line patterns. After detecting such
candidates, their supports are added to the given candidate. For example,
if the given candidate is 'Interface * down' with the support 20, and
candidates 'Interface eth0 down' (support 10) and 'Interface eth1 down'
(support 5) are detected as more specific, the support of 'Interface * down'
will be set to 35 (20+10+5).
This option can not be used with --csize option.
"""

MAN_WWEIGHT = """
--wweight=<word_weight_threshold>
This option enables word weight based heuristic for joining clusters.
The option takes a positive real number not greater than 1 for its value.
With this option, an additional pass over input files is made, in order
to find dependencies between frequent words.
For example, if 5% of log file lines that contain the word 'Interface'
also contain the word 'eth0', and 15% of the log file lines with the word
'unstable' also contain the word 'eth0', dependencies dep(Interface, eth0)
and dep(unstable, eth0) are memorized with values 0.05 and 0.15, respectively.
Also, dependency dep(eth0, eth0) is memorized with the value 1.0.
Dependency information is used for calculating the weight of words in line
patterns of all detected clusters. The function for calculating the weight
can be set with --weightf option.
For instance, if --weightf=1 and the line pattern of a cluster is
'Interface eth0 unstable', then given the example dependencies above,
the weight of the word 'eth0' is calculated in the following way:
(dep(Interface, eth0) + dep(eth0, eth0)
  + dep(unstable, eth0)) / number of words = (0.05 + 1.0 + 0.15) / 3 = 0.4
If the weights of 'Interface' and 'unstable' are 1, and the word weight
threshold is set to 0.5 with --wweight option, the weight of 'eth0'
remains below threshold. If another cluster is identified where all words
appear in the same order, and all words with sufficient weight are identical,
two clusters are joined. For example, if clusters 'Interface eth0 unstable'
and 'Interface eth1 unstable' are detected where the weights of 'Interface'
and 'unstable' are sufficient in both clusters, but the weights of 'eth0'
and 'eth1' are smaller than the word weight threshold, the clusters are
joined into a new cluster 'Interface (eth0|eth1) unstable'.
In order to quickly evaluate different word weight threshold values and
word weight functions on the same set of clusters, clusters and word
dependency information can be dumped into a file during the first run of
the algorithm, in order to reuse these data during subsequent runs
(see --readdump and --writedump options).
"""

MAN_WEIGHTF = """
This option takes an integer for its value which denotes a word weight
function, with the default value being 1. The function is used for finding
weights of words in cluster line patterns if --wweight option has been given.
If W1,...,Wk are words of the cluster line pattern, value 1 denotes the
function that finds the weight of the word Wi in the following way:
(dep(W1, Wi) + ... + dep(Wk, Wi)) / k
Value 2 denotes the function that will first find unique words U1,...Up from
W1,...Wk (p <= k, and if Ui = Uj then i = j). The weight of the word Ui is
then calculated as follows:
if p>1 then (dep(U1, Ui) + ... + dep(Up, Ui) - dep(Ui, Ui)) / (p - 1)
if p=1 then 1
Value 3 denotes a modification of function 1 which calculates the weight
of the word Wi as follows:
((dep(W1, Wi) + dep(Wi, W1)) + ... + (dep(Wk, Wi) + dep(Wi, Wk))) / (2 * k)
Value 4 denotes a modification of function 2 which calculates the weight
of the word Ui as follows:
if p>1 then ((dep(U1, Ui) + dep(Ui, U1)) + ... + (dep(Up, Ui) + dep(Ui, Up)) - 2*dep(Ui, Ui)) / (2 * (p - 1))
if p=1 then 1
"""

MAN_SEPARATOR = """
Regular expression which matches separating characters between words.
Default value for <word_separator_regexp> is \\s+ (i.e., regular expression
that matches one or more whitespace characters).
"""

def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--support', type=int, help=MAN_SUPPORT)
    parser.add_argument('-i', '--input', help=MAN_INPUT)
    parser.add_argument('-as', '--aggrsup', action='store_true', help=MAN_AGGRSUP)
    parser.add_argument('-ww', '--wweight', type=float, help=MAN_WWEIGHT)
    parser.add_argument('-wf', '--weightf', type=int, help=MAN_WEIGHTF)
    parser.add_argument('-se', '--separator', help=MAN_SEPARATOR)
    args = parser.parse_args()

    return args

ARGS = parse_arguments()
try:
    INPUT=os.path.abspath(ARGS.input)
except Exception as e:
    logMsg("Unable to parse input as OS path, verify that file exists", "error")
SUPPORT=ARGS.support
AGGRSUP=ARGS.aggrsup
WWEIGHT=ARGS.wweight
WEIGHTF=ARGS.weightf
SEPARATOR=ARGS.separator
CEE_PARSE=True
CEE_PREFIX='@cee: '

if WWEIGHT:
    if WWEIGHT < 0 or WWEIGHT > 1:
        logMsg("--wweight must be a float between 0 and 1", "error")
    else:
        if not WEIGHTF:
            WEIGHTF=1
        else:
            if WEIGHTF > 4 or WEIGHTF < 1:
                logMsg("--weightf must be an integer between 1 and 4", "error")

if not INPUT:
    logMsg("Input file not defined", "error")
if not SUPPORT:
    logMsg("Support value not defined", "error")

if SEPARATOR:
    try:
        re.compile(SEPARATOR)
    except re.error:
        logMsg("Provided separator does not compile as valid regex", "error")

def main():
    cluster = LogCluster(
                        SUPPORT,
                        INPUT,
                        AGGRSUP,
                        WWEIGHT,
                        WEIGHTF,
                        SEPARATOR,
                        CEE_PARSE,
                        CEE_PREFIX
                        )
    print('Finding words')
    cluster.findWordsFromFile()
    dumpDataToFile(cluster.returnFrequentWords(), '/tmp/logcluster-wordcount.dmp')
    print('Done')
    print('Finding frequent words')
    cluster.findFrequentWords()
    dumpDataToFile(cluster.returnFrequentWords(), '/tmp/logcluster-fwords.dmp')
    print('Number of F Words: ', cluster.returnFrequentWordsLength())
    print('Done')
    print('Finding candidates')
    cluster.findCandidatesFromFile()
    dumpDataToFile(cluster.returnCandidates(), '/tmp/logcluster-candidates.dmp')
    print('Number of Candidates: ', cluster.returnCandidatesLength())
    print('Done')
    print('Aggregating supports')
    cluster.aggregateSupports()
    dumpDataToFile(cluster.returnPTree(), '/tmp/logcluster-ptree.dmp')
    dumpDataToFile(cluster.returnCandidates(), '/tmp/logcluster-agg-candidates.dmp')
    print('Ptree size: ', cluster.returnPTreeSize())
    print('Done')
    print('Finding clusters')
    cluster.findClusters()
    dumpDataToFile(cluster.returnClusters(), '/tmp/logcluster-clusters.dmp')
    print('Number of Clusters: ', cluster.returnClustersLength())
    print('Done')

if __name__ == "__main__":
    main()
