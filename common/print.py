#!/usr/bin/env python3
# coding: utf-8

import json

def dumpAsJSON(dictionary):
    return json.dumps(dictionary, sort_keys=False, indent=2)
