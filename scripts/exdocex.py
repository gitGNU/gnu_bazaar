#!/usr/bin/python

# $Id: exdocex.py,v 1.3 2003/10/09 16:51:10 wrobell Exp $

# usage:
#   exdocex.py < module.py | python -
#

import sys
import re

ilen = 4       # amount of indent spaces (yes, no tabs)
code = False   # processing example code
indent = None  # indentation of example code 

for l in sys.stdin:
    if code:
        if re.match('(^%s+[\'\"{}()\[\]#_a-zA-Z])|(^$)' % indent, l) is not None:
            pl = re.match('(^%s(.*))|^()$' % indent, l).group(2)
            if pl is None:
                print
            else:
                print pl
        else: # end of example code
            code = False
            indent = None

    # find the begining of example code
    if l[-3:] == '::\n':    # we should process docstrings, now
        assert not code and indent is None
        match = re.match('^ *', l)
        if match is not None:
            code = True
            indent = match.group(0) + ilen * ' '
