#!/usr/bin/env python3
# coding: utf-8

import hashlib
import argparse
import json
from algorithms.LogCluster import *
from common.print import *

# mapreduce
import re

class mapReduce(object):
    def __init__(self, separator=' '):
        self.separator = separator

        if self.separator != ' ':
            self.sepRegex = re.compile(self.separator)

    def splitLine(self, line):
        if self.separator != ' ':
            return self.sepRegex.split(line)
        else:
            return line.split()

def main():
    print('Hello world')

if __name__ == "__main__":
    main()
