#!/usr/bin/env python3
# coding: utf-8
# see - http://ristov.github.io/logcluster/

import hashlib
import argparse
from algorithms.LogCluster import *

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

def logMsg(message, level):
    if(level=='error'):
        print(message)
        print("Please refer to --help")
        sys.exit(1)
    else:
        print(message)

def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--support', type=int, help=MAN_SUPPORT)
    parser.add_argument('-i', '--input', help=MAN_INPUT)
    parser.add_argument('-as', '--aggrsup', action='store_true', help=MAN_AGGRSUP)
    args = parser.parse_args()

    return args

ARGS = parse_arguments()
try:
    INPUT=os.path.abspath(ARGS.input)
except Exception as e:
    logMsg("Unable to parse input as OS path, verify that file exists", "error")
SUPPORT=ARGS.support
AGGRSUP=ARGS.aggrsup

if not INPUT:
    logMsg("Input file not defined", "error")
if not SUPPORT:
    logMsg("Support value not defined", "error")

def main():
    cluster = LogCluster(SUPPORT, INPUT, AGGRSUP)
    cluster.findFrequentWords()
    cluster.findCandidatesFromFile()
    cluster.populatePrefixTree()
    cluster.findFrequentCandidates()

    # DEBUG
    words = cluster.returnFrequentWords()
    candidates = cluster.returnCandidates()
    ptree = cluster.returnPTree()
    for key, value in ptree.items():
        #ID_HASH = hashlib.md5(key.encode()).hexdigest()
        print('-------KEY--------')
        print(key)
        print('-------VALUE------')
        print(value)


if __name__ == "__main__":
    main()
