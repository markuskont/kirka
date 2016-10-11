#!/usr/bin/env python3
# coding: utf-8
# see - http://ristov.github.io/logcluster/

import os, re, sys

class LogCluster():
    def __init__(self, support, source=None):
        # parameters
        self.support    = support
        self.source     = source

        # Data structures
        self.fwords     = {}
        self.candidates = {}

    # FIND FREQUENT WORDS
    def findFrequentWords(self, source=None):
        source = self.evalFileInput(source)
        self.findWordsFromFile(source)
        for word, count in self.fwords.copy().items():
            if count < self.support:
                del self.fwords[word]

    def findWordsFromFile(self, source=None):
        source = self.evalFileInput(source)
        with open(source) as f:
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
    def findCandidatesFromFile(self, source=None):
        source = self.evalFileInput(source)
        with open(source) as f:
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

    # Allow --input to be defined globally in init, or per method
    # Methods will use object global if left undefined by user
    # For example, generate words from one file and candidates from another
    def evalFileInput(self, source):
        return self.source if source == None else source
