#!/usr/bin/env python3
# coding: utf-8
# see - http://ristov.github.io/logcluster/

import os, re, argparse, sys
import hashlib

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

class LogCluster():
    def __init__(self, support):
        # parameters
        self.support = support

        # Data structures
        self.fwords = {}
        self.candidates = {}

    # FIND FREQUENT WORDS
    def findFrequentWords(self, source):
        self.findWordsFromFile(source)
        for word, count in self.fwords.copy().items():
            if count < self.support:
                del self.fwords[word]

    def findWordsFromFile(self, inFile):
        with open(inFile) as f:
            for line in f:
                self.fwords = self.wordsFromLine(line)

    def wordsFromLine(self, line):
        return self.incrementCounter(self.splitLine(line), self.fwords)

    def incrementCounter(self, array, counts):
        for item in array:
            if not item in counts:
                counts[item] = 1
            else:
                counts[item] += 1
        return counts

    # FIND CANDIDATES
    def findCandidatesFromFile(self, inFile):
        with open(inFile) as f:
            for line in f:
                self.candidateFromLine(line)

    def candidateFromLine(self, line):
        candidate, wildcards, varnum = self.compareLineWithFrequentWords(line)
        if candidate:
            candidate_id = '\n'.join(candidate)
            if not candidate_id in self.candidates:
                self.candidates[candidate_id] = self.initiateCandidate(candidate, wildcards)
            else:
                self.modifyCandidate(candidate_id, wildcards)

    def compareLineWithFrequentWords(self, line):
        candidate = []
        wildcards = []
        varnum = 0
        words = self.splitLine(line)
        for word in words:
            if word in self.fwords:
                candidate.append(word)
                wildcards.append(varnum)
                varnum = 0
            else:
                varnum += 1
        return candidate, wildcards, varnum

    def initiateCandidate(self, words, wildcards):
        structure = {}
        structure['words'] = words
        structure['wordCount'] = len(words)
        structure['count'] = 1
        structure['wildcards'] = []
        for wildcard in wildcards:
            structure['wildcards'].append([wildcard, wildcard])
        return structure

    def modifyCandidate(self, ID, wildcards):
        total = len(wildcards)
        i = 0
        while i < total:
            w_from  = self.candidates[ID]['wildcards'][i][0]
            w_to    = self.candidates[ID]['wildcards'][i][1]
            if w_from > wildcards[i]:
                self.candidates[ID]['wildcards'][i][0] = wildcards[i]
            elif w_to < wildcards[i]:
                self.candidates[ID]['wildcards'][i][1] = wildcards[i]
            i += 1
        self.candidates[ID]['count'] += 1

    # FIND CLUSTERS
    def findFrequentCandidates(self):
        for key, candidate in self.candidates.copy().items():
            if candidate['count'] < self.support:
                del self.candidates[key]

    # GLOBAL HELPERS
    def splitLine(self, line):
        return line.split()

    def returnFrequentWords(self):
        return self.fwords

    def returnCandidates(self):
        return self.candidates

def main():
    cluster = LogCluster(SUPPORT)
    cluster.findFrequentWords(INPUT)
    cluster.findCandidatesFromFile(INPUT)
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
