#!/usr/bin/env python3
# coding: utf-8
# see - http://ristov.github.io/logcluster/

import os, re, sys
import json
import hashlib

def dumpAsJSON(dictionary):
    return json.dumps(dictionary, sort_keys=False, indent=2)

def hashString(string):
    return hashlib.md5(string.encode()).hexdigest()

class LogCluster():
    def __init__(
                self,
                support,
                source=None,
                aggrsup=False,
                wweight=None,
                weightf=1,
                separator=None,
                CEE_parse=False,
                CEE_prefix='@cee: '
                ):
        # parameters
        self.support    = support
        self.source     = source
        self.aggrsup    = aggrsup
        self.wweight    = wweight if isinstance(wweight, float) else None

        # Data structures
        self.fwords     = {}
        self.candidates = {}
        self.clusters   = {}

        if self.aggrsup is True:
            self.ptree              = {}
            self.ptree['children']  = {}
            self.ptreesize          = 0

        if isinstance(self.wweight, float):
            self.weightf            = weightf if isinstance(weightf, int) else 1
            self.fword_deps         = {}

        self.separator = separator
        if self.separator:
            try:
                self.separator = re.compile(separator)
            except re.error:
                raise

        self.CEE_parse = CEE_parse
        self.CEE_prefix = CEE_prefix

    # FIND FREQUENT WORDS
    def findWordsFromFile(self, source=None):
        source = self.evalFileInput(source)
        with open(source) as f:
            for line in f:
                self.fwords = self.wordsFromLine(line)
        return self

    def findFrequentWords(self):
        keys_list = list( self.fwords.keys())
        for key in keys_list:
            if self.fwords[key] < self.support:
                del self.fwords[key]
        return self

    def wordsFromLine(self, line):
        return self.incrementCounter(self.processLine(line), self.fwords)

    def incrementCounter(self, array, counts):
        for item in array:
            counts[item] = counts.get(item, 0) + 1
        return counts

    # FIND CANDIDATES
    def findCandidatesFromFile(self, source=None):
        source = self.evalFileInput(source)
        with open(source) as f:
            for line in f:
                self.candidateFromLine(line)
        if self.wweight:
            self.convertFwordDepsToDecimal()
        return self

    def candidateFromLine(self, line):
        candidate, wildcards = self.compareLineWithFrequentWords(line)
        if candidate:
            candidate_id = '\n'.join(candidate)
            if self.wweight:
                self.fillFwordDepTable(candidate)
            if not candidate_id in self.candidates:
                self.candidates[candidate_id] = self.initiateCandidate(candidate, 1)
                self.candidates[candidate_id] = self.populateWildcards(wildcards, self.candidates[candidate_id])
            else:
                self.modifyCandidate(candidate_id, wildcards)

    def compareLineWithFrequentWords(self, line):
        candidate = []
        wildcards = []
        varnum = 0
        words = self.processLine(line)
        for word in words:
            if word in self.fwords:
                candidate.append(word)
                wildcards.append(varnum)
                varnum = 0
            else:
                varnum += 1
        wildcards.append(varnum)
        return candidate, wildcards

    def initiateCandidate(self, words, count):
        return {
            'words'     : words,
            'wordCount' : len(words),
            'count'     : count,
            'wildcards' : []
        }

    def populateWildcards(self, wildcards, structure):
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
        keys_list = list( self.candidates.keys())
        for key in keys_list:
            if self.candidates[key]['count'] < self.support:
                del self.candidates[key]

    def findClusters(self):
        self.findFrequentCandidates()
        if self.wweight:
            self.joinCandidates()
        else:
            self.clusters = self.candidates
        return self

    # AGGREGATE SUPPORTS
    def aggregateSupports(self):
        if self.aggrsup:
            for ID, candidate in self.candidates.items():
                self.insertIntoPrefixTree(self.ptree, ID, candidate, 0)
            for ID, candidate in self.candidates.items():
                self.initCandidateSubCluster(ID)
                self.populateCandidateSubCluster(self.ptree, ID, candidate, 0, 0, 0)
                if self.candidates[ID]['SubClusters']:
                    for ID2 in self.candidates[ID]['SubClusters']:
                        self.candidates[ID]['Count2'] += self.candidates[ID2]['count']
            for ID in self.candidates:
                self.candidates[ID]['count'] = self.candidates[ID]['Count2']
                del self.candidates[ID]['Count2']
        return self

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

    # JOIN CLUSTERS
    # This is invoked in candidate creation phase
    def fillFwordDepTable(self, candidate):
        for word in candidate:
            if word in self.fword_deps:
                for word2 in candidate:
                    self.fword_deps[word][word2] = self.fword_deps[word].get(word2, 0) + 1
            else:
                self.fword_deps[word] = {}

    # divide word dependency count with overall word occurrence count
    def convertFwordDepsToDecimal(self):
        for word in self.fword_deps:
            for word2 in self.fword_deps[word]:
                self.fword_deps[word][word2] /= self.fwords[word]

    # This is invoked after candidate creation, in the final step for generating clusters
    def joinCandidates(self):
        if self.wweight:
            for ID, candidate in self.candidates.items():
                self.assessWordWeight(ID, candidate)
                self.joinCandidate(ID, candidate)

    def assessWordWeight(self, ID, candidate):
        switcher = {
            1: self.weightf1,
            2: self.weightf2,
            3: self.weightf3,
            4: self.weightf4
        }
        func = switcher.get(self.weightf)
        return func(ID, candidate)

    def weightf1(self, ID, candidate):
        words = candidate['words']
        total = candidate['wordCount']
        self.candidates[ID]['Weights'] = []
        for word in words:
            weight = 0
            for word2 in words:
                weight += self.fword_deps[word2][word]
            self.candidates[ID]['Weights'].append(weight/total)

    def weightf2(self, ID, candidate):
        words = candidate['words']
        total = candidate['wordCount']
        self.candidates[ID]['Weights'] = []
        weights = self.listToDict(words)
        for word in words:
            if not total:
                weights[word] = 1
                break
            for word2 in words:
                if word == word2:
                    break
                weights[word] += self.fword_deps[word2][word]
            weights[word] /= total
        for word in words:
            self.candidates[ID]['Weights'].append(weights[word])

    def weightf3(self, ID, candidate):
        words = candidate['words']
        total = candidate['wordCount']
        self.candidates[ID]['Weights'] = []

        for word in words:
            weight = 0
            for word2 in words:
                weight += (self.fword_deps[word2][word] + self.fword_deps[word][word2])
            self.candidates[ID]['Weights'].append(weight/(total*2))

    def weightf4(self, ID, candidate):
        words = candidate['words']
        total = candidate['wordCount']
        self.candidates[ID]['Weights'] = []
        weights = self.listToDict(words)
        for word in words:
            if not total:
                weights[word] = 1
                break
            for word2 in words:
                if word == word2:
                    break
                weights[word] += (self.fword_deps[word2][word] + self.fword_deps[word][word2])
            weights[word] /= (2*total)
        for word in words:
            self.candidates[ID]['Weights'].append(weights[word])

    def joinCandidate(self, ID, candidate):
        wordcount = candidate['wordCount']
        newCandidate = []
        i = 0
        for i in range(wordcount):
            if candidate['Weights'][i] >= self.wweight:
                newCandidate.append(candidate['words'][i])
            else:
                newCandidate.append("")
        candidate_id = '\n'.join(newCandidate)
        newCandidate = self.convertEmptyWords(newCandidate)
        if not candidate_id in self.clusters:
            self.clusters[candidate_id] = self.initiateCandidate(newCandidate, 0)
            self.clusters[candidate_id]['wildcards'] = candidate['wildcards']
        self.appendJoinedWord(candidate, newCandidate, candidate_id)
        for i in range(wordcount + 1):
            candmin, candmax = self.returnWildcardMinMax(ID, i)
            clustmin, clustmax = self.returnClusterWildcardMinMax(candidate_id, i)
            if clustmin > candmin:
                self.clusters[candidate_id]['wildcards'][i][0] = candmin
            if clustmax < candmax:
                self.clusters[candidate_id]['wildcards'][i][1] = candmax
        self.clusters[candidate_id]['count'] += candidate['count']

    def convertEmptyWords(self, candidate):
        i = 0
        for word in candidate:
            if len(word) == 0:
                candidate[i] = {}
            i +=1
        return candidate

    def appendJoinedWord(self, candidate, newCandidate, ID):
        i = 0
        for word in newCandidate:
            if isinstance(word, dict):
                self.clusters[ID]['words'][i][candidate['words'][i]] = 1
            i += 1

    # GLOBAL HELPERS
    def listToDict(self, list):
        return {x:0 for x in list}

    def returnWildcardData(self, ID, index, position):
        return self.candidates[ID]['wildcards'][index][position]

    def returnWildcardMinMax(self, ID, index):
        minimum = self.candidates[ID]['wildcards'][index][0]
        maximum = self.candidates[ID]['wildcards'][index][1]
        return minimum, maximum

    def returnClusterWildcardMinMax(self, ID, index):
        minimum = self.clusters[ID]['wildcards'][index][0]
        maximum = self.clusters[ID]['wildcards'][index][1]
        return minimum, maximum

    # Split lines with standard split() if separator left undefined (default to whitespace)
    # alternatively, use more expensive re.split() if separator is defined
    # process subsequent line as JSON if @cee cookie is found
    # TODO
    def processLine(self, line):
        if self.CEE_parse and self.CEE_prefix in line:
            processed = line.split(self.CEE_prefix)
            log = self.splitLine(processed[0])
            structured = []
            try:
                structured = self.nestedDictToList(json.loads(processed[1]))
            except ValueError:
                # just process as string if parse fails
                # NOTE! Maybe create debug here to find broken json logs?
                structured = self.splitLine(processed[1])
            log.extend(structured)
            return log
        else:
            return self.splitLine(line)

    def splitLine(self, line):
        if self.separator and self.separator != '':
            # re.split does return empty strings as '', unlike str.split
            return filter(None, self.separator.split(line))
        else:
            return line.split()

    def nestedDictToList(self, d):
        result = []
        for key, value in sorted(d.items()):
            result.append(key)
            if isinstance(value, dict):
                result.extend(self.nestedDictToList(value))
            elif isinstance(value, list):
                result.extend(str(value))
            else:
                result.append(str(value))
        return result

    # return instance data structure, mainly for debug
    def returnFrequentWords(self):
        return self.fwords

    def returnFrequentWordsLength(self):
        return len(self.fwords)

    def returnCandidates(self):
        return self.candidates

    def returnCandidatesLength(self):
        return len(self.candidates)

    def returnClusters(self):
        return self.clusters

    def returnClustersLength(self):
        return len(self.clusters)

    def returnPTree(self):
        return self.ptree if self.aggrsup == True else None

    def returnPTreeSize(self):
        return self.ptreesize if self.aggrsup == True else None

    def returnWweightParams(self):
        return self.wweight, self.weightf if self.wweight and self.weightf else None

    def returnFwordDeps(self):
        return self.fword_deps if self.wweight != None else None

    # Allow --input to be defined globally in init, or per method
    # Methods will use object global if left undefined by user
    # For example, generate words from one file and candidates from another
    def evalFileInput(self, source):
        return self.source if source == None else source
