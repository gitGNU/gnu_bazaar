#!/usr/bin/python

import re
import sys

if len(sys.argv) != 3:
    print >> sys.stderr, 'usage: cmp_std.py std.out bzr.out'
    sys.exit(1)

std_file = open(sys.argv[1])
bzr_file = open(sys.argv[2])

std_data = {}
bzr_data = {}
keys = ('add', 'load', 'update', 'del')
for key in keys:
    std_data[key] = []
    bzr_data[key] = []

def analyze(f, data):
    for l in f.readlines():
        op, time = l.split(':')
        data[op].append(float(time))

def average(list):
    return sum(list)/len(list)

analyze(std_file, std_data)
analyze(bzr_file, bzr_data)

print '%8s %12s %12s %12s' % ('', 'std', 'bzr', ('%'))
for key in keys:
    bzr_avg = average(bzr_data[key])
    std_avg = average(std_data[key])
    print '%7s: %12.2f %12.2f %12.2f' % (key, std_avg, bzr_avg, bzr_avg/std_avg)
