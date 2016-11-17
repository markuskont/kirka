#!/usr/bin/env python3
# coding: utf-8
# see - http://ristov.github.io/logcluster/

import json
import argparse
from common.print import *
import hashlib

import matplotlib.pyplot as plt
import operator

import numpy as np
import math

#from bokeh.plotting import figure, output_file, show
from bokeh.charts import Bar, Line, output_file, show

def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--infile')
    args = parser.parse_args()

    return args

def calcExponentialGrowthRate(
    FinalAmount,
    BeginningAmount,
    Time):
    # FinalAmount = BeginningAmount*e**constant*Time
    return np.log( FinalAmount / BeginningAmount ) / Time

def assessValues(data, count=0):
    data = sorted(data)
    print('MAX: ', data[-1])
    percentile = np.percentile(data, 99.99)
    print(percentile)
    growth = calcExponentialGrowthRate(data[-1], data[0], count)
    print(growth)

    stop, start = 20, 2
    print(calcExponentialGrowthRate(stop, start, data.index(stop) - data.index(start)))
    stop, start = 586202, 20
    print(calcExponentialGrowthRate(stop, start, data.index(stop) - data.index(start)))

    steps = 50
    step = math.floor(len(data) / steps)

    stop = 0
    for start in range(steps):
        stop += step
        growth = calcExponentialGrowthRate(data[stop], data[start], step)
        print(growth)

def drawLineGraph(data=[]):
    line = Line(sorted(data), title='Words', legend=False, ylabel='Count', width=1500)

    output_file("out.html")
    show(line)

def main():
    args = parse_arguments()
    infile=args.infile

    with open(infile) as data_file:
        data = json.load(data_file)

    sketch = {}
    count = 0
    filtered_count = 0
    collisions = 0
    values = []
    for k, v in data.items():
        image = hashlib.md5(k.encode('utf-8')).digest()
        #image = int(hashlib.sha256(k.encode('utf-8')).hexdigest(), 16) % (10 ** 8)
        if image in sketch:
            collisions += 1

        sketch[image] = v
        if v > 1:
            values.append(v)
            filtered_count += 1
        count += 1

    print('Elements: ', count)
    print('Elements after preliminary filtering: ', filtered_count)
    print('Collisions: ', collisions)

    assessValues(values, filtered_count)
    drawLineGraph(values)


if __name__ == "__main__":
    main()
