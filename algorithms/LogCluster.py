#!/usr/bin/env python3
# coding: utf-8
# see - http://ristov.github.io/logcluster/

import os, re, sys
import json

def dumpAsJSON(dictionary):
    return json.dumps(dictionary, sort_keys=False, indent=2)

class LogCluster():
    def __init__(
                self,
                support,
                source=None,
                aggrsup=False
                ):
        # parameters
        self.support    = support
        self.source     = source
        self.aggrsup    = aggrsup

        # Data structures
        self.fwords     = {}
        self.candidates = {}

        if self.aggrsup is True:
            self.ptree              = {}
            self.ptree['children']  = {}
            self.ptreesize          = 0

    # FIND FREQUENT WORDS
    def findWordsFromFile(self, source=None):
        source = self.evalFileInput(source)
        with open(source) as f:
            for line in f:
                self.fwords = self.wordsFromLine(line)

    def findFrequentWords(self):
        for word, count in self.fwords.copy().items():
            if count < self.support:
                del self.fwords[word]

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
        candidate, wildcards = self.compareLineWithFrequentWords(line)
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
        wildcards.append(varnum)
        return candidate, wildcards

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
            w_from, w_to = self.returnWildcardMinMax(ID, i)
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

    # AGGREGATE SUPPORTS
    def aggregateSupports(self):
        if self.aggrsup:
            for ID, candidate in self.candidates.items():
                self.insertIntoPrefixTree(self.ptree, ID, candidate, 0)
            for ID, candidate in self.candidates.items():
                self.initCandidateSubCluster(ID)
                self.populateCandidateSubCluster(self.ptree, ID, candidate, 0, 0, 0)
                #if self.candidates[ID]['SubClusters']:
                #    for key2, subcluster in self.candidates[ID]['SubClusters'].items():
                #        self.candidates[ID]['Count2'] += self.candidates[key2]['count']

    def initCandidateSubCluster(self, ID):
        count = self.candidates[ID]['count']
        self.candidates[ID]['OldCount'] = count
        self.candidates[ID]['Count2'] = count
        self.candidates[ID]['SubClusters'] = {}

    def populateCandidateSubCluster(self, data, ID, candidate, index, minimum, maximum):
        candmin, candmax = self.returnWildcardMinMax(ID, index)
        children = data['children']
        wordcount = candidate['wordCount']
        for child, data in children.items():
            totalmin = data['min'] + minimum
            totalmax = data['max'] + maximum

            if index == wordcount:
                if 'candidate' in data:
                    if candmin > totalmin or candmax < totalmax:
                        continue
                    cand2 = data['candidate']
                    if ID != cand2:
                        self.candidates[ID]['SubClusters'][cand2] = 1
                else:
                    self.populateCandidateSubCluster(data, ID, candidate, index, totalmin + 1, totalmax + 1)
                continue

            if 'candidate' in data:
                continue
            if candmax < totalmax:
                continue
            if candmin > totalmin or candidate['words'][index] != data['word']:
                self.populateCandidateSubCluster(data, ID, candidate, index, totalmin + 1, totalmax + 1)
                continue
            self.populateCandidateSubCluster(data, ID, candidate, index + 1, 0, 0)
            self.populateCandidateSubCluster(data, ID, candidate, index, totalmin + 1, totalmax + 1)

    def insertIntoPrefixTree(self, node, ID, candidate,  index):
        minimum, maximum = self.returnWildcardMinMax(ID, index)
        label = self.setLabel(ID, index, minimum, maximum)
        if not label in node['children']:
            node['children'][label] = self.initPrefixChildNode(ID, candidate, index, minimum, maximum)
        else:
            node = node['children'][label]
        if index < candidate['wordCount']:
            node = self.insertIntoPrefixTree(node, ID, candidate, index + 1)
        return node

    def initPrefixChildNode(self, ID, candidate, index, minimum, maximum):
        child = {}
        child['min'] = minimum
        child['max'] = maximum
        if index < candidate['wordCount']:
            child['children'] = {}
            child['word'] = candidate['words'][index]
        else:
            child['candidate'] = ID
        self.ptreesize += 1
        return child

    def setLabel(self, ID, index, minimum, maximum):
        label = "%s\n%s" % ( minimum, maximum )
        if index == self.candidates[ID]['wordCount']:
            return label
        else:
            return label + "\n%s" % ( self.candidates[ID]['words'][index] )

    def returnWildcardMinMax(self, ID, index):
        minimum = self.candidates[ID]['wildcards'][index][0]
        maximum = self.candidates[ID]['wildcards'][index][1]
        return minimum, maximum

    # GLOBAL HELPERS
    def returnWildcardData(self, ID, index, position):
        return self.candidates[ID]['wildcards'][index][position]

    def splitLine(self, line):
        return line.split()

    def returnFrequentWords(self):
        return self.fwords

    def returnCandidates(self):
        return self.candidates

    def returnPTree(self):
        return self.ptree if self.aggrsup == True else None

    def returnPTreeSize(self):
        return self.ptreesize if self.aggrsup == True else None

    # Allow --input to be defined globally in init, or per method
    # Methods will use object global if left undefined by user
    # For example, generate words from one file and candidates from another
    def evalFileInput(self, source):
        return self.source if source == None else source
