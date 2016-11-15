#!/usr/bin/env python3
# coding: utf-8

import json, os, sys

def dumpAsJSON(dictionary):
    return json.dumps(dictionary, sort_keys=False, indent=2)

def dumpDataToFile(data, dumpfile):
    if not os.path.exists(dumpfile):
        with open(dumpfile, 'w') as dump:
            json.dump(data, dump)
    else:
        message = "%s already exists, not dumping." % (dumpfile)
        logMsg(message, 'info')

def logMsg(message, level):
    if(level=='error'):
        print(message)
        print("Please refer to --help")
        sys.exit(1)
    else:
        print(message)

def debugPrint(data):
    for key, value in data.items():
        ID_HASH = hashlib.md5(key.encode()).hexdigest()
        print('-------KEY--------')
        print(ID_HASH)
        print('-------VALUE------')
        print(value)
