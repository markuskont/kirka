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

#from bokeh.plotting import figure, output_file, show
from bokeh.charts import Bar, Line, output_file, show

def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--infile')
    args = parser.parse_args()

    return args

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

    #keys = sketch.keys()
    #values = sketch.values()
    #values = [10, 20, 40, 30]

    #q = Bar(keys, values, title="simple line example", xlabel='x', ylabel='y')
    #bar = Bar(sorted(values),xlabel="x",ylabel="Y", width=len(values))
    #bar.toolbar.logo = None
    #bar.toolbar_location = None
    #q.line(keys, values, legend="Temp.", line_width=2)
    values = sorted(values)
    #print(values[-1])
    percentile = np.percentile(values,99)
    print(percentile)

    line = Line(values, title='Words', legend=False, ylabel='Count', width=1500)

    output_file("out.html")
    show(line)

if __name__ == "__main__":
    main()
