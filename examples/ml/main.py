#!/usr/bin/env python

import kNN

group,labels = kNN.createDataSet()
print kNN.classify0([0,0.1], group, labels, 3)
