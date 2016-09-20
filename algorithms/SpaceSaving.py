#!/usr/bin/env python
# coding: utf-8

class SpaceSaving():
    def __init__(self):
        self.counters   = {}
        self.candidates = {}
        
    def add(self, item, k, k2, t):
        if item in self.counters:
            self.counters[item] = self.counters[item] + 1
        elif len(self.counters) < k:
            self.counters[item] = 1
        else:
            if item in self.candidates:
                self.candidates[item] = self.candidates[item] + 1
                if self.candidates[item] == t:
                    dropout = min(self.counters, key=self.counters.get)
                    del self.counters[dropout]
                    self.counters[item] = t
                    del self.candidates[item]
                    return dropout
            elif len(self.candidates) < k2:
                self.candidates[item] = 1
            else:
                del self.candidates[min(self.candidates, key=self.candidates.get)]
                self.candidates[item] = 1

    def returnItems(self):
        return self.counters

    def returnCandidates(self):
        return self.candidates
