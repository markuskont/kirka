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
    args = parser.parse_args()

    return args

ARGS = parse_arguments()
try:
    INPUT=os.path.abspath(ARGS.input)
except Exception as e:
    logMsg("Unable to parse input as OS path, verify that file exists", "error")
SUPPORT=ARGS.support

if not INPUT:
    logMsg("Input file not defined", "error")
if not SUPPORT:
    logMsg("Support value not defined", "error")
def main():
    cluster = LogCluster(SUPPORT, INPUT)
    cluster.findFrequentWords()
    cluster.findCandidatesFromFile()
    cluster.findFrequentCandidates()

    # DEBUG
    words = cluster.returnFrequentWords()
    candidates = cluster.returnCandidates()
    for key, value in candidates.items():
        ID_HASH = hashlib.md5(key.encode()).hexdigest()
        print('---------------------')
        print(ID_HASH)
        print('---------------------')
        print(value)


if __name__ == "__main__":
    main()
