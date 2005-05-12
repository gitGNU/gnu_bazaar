#!/usr/bin/python
#
# $Id: exdocex.py,v 1.5 2005/05/12 18:29:58 wrobell Exp $
#
# Bazaar - an easy to use and powerful abstraction layer between relational
# database and object oriented application.
#
# Copyright (C) 2000-2005 by Artur Wroblewski <wrobell@pld-linux.org>
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
