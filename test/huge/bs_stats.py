#!/usr/bin/python
#
# $Id: bs_stats.py,v 1.3 2004/01/22 23:21:41 wrobell Exp $
#
# Bazaar - an easy to use and powerful abstraction layer between relational
# database and object oriented application.
#
# Copyright (C) 2000-2004 by Artur Wroblewski <wrobell@pld-linux.org>
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

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
    try:
        bzr_avg = average(bzr_data[key])
        std_avg = average(std_data[key])
    except: pass
    else:
        print '%7s: %12.2f %12.2f %12.2f' % (key, std_avg, bzr_avg, bzr_avg/std_avg)
