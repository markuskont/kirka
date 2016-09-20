#!/usr/bin/env python
# coding: utf-8

class Frequent():
    def __init__(self):
        self.counters   = {}

    def add(self, item, k, k2, t):
        if item in self.counters:
            counters[item] = counters[item] + 1
        elif len(self.counters) <= k:
            self.counters[item] = 1
        else:
            for key, value in self.counters.copy().items():
                if value > 1:
                    self.counters[key] = value - 1
                else:
                    del self.counters[key]
                    return key

    def returnItems(self):
        return self.counters
