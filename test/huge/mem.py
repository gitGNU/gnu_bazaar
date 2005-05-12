#!/usr/bin/python
#
# $Id: mem.py,v 1.7 2005/05/12 18:29:58 wrobell Exp $
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

import sys
import os
import re

import bazaar.core

import bazaar.test.app

Order     = bazaar.test.app.Order
OrderItem = bazaar.test.app.OrderItem
Article   = bazaar.test.app.Article
Employee  = bazaar.test.app.Employee

mod = __import__(sys.argv[1])
dsn = sys.argv[2]
amount = int(sys.argv[3])

bzr = bazaar.core.Bazaar((Order, OrderItem, Article, Employee),
    dbmod = mod, dsn = dsn,
    seqpattern = 'select nextval(\'%s\')')

art = Article(name = 'apple', price = 2.22)
bzr.add(art)

for j in range(0, amount, 5000):
    ord = Order(no = j, finished = False)
    bzr.add(ord)
    items = ord.items
    oi_count = j + 5000
    for i in range(j, oi_count):
        oi = OrderItem()
        oi.article = art
        oi.quantity = 10
        oi.pos = i
        items.append(oi)
        bzr.add(oi)

    # get memory amount: linux specific
    f = open('/proc/%d/status' % os.getpid())
    for l in f.readlines():
        header, value = l.split(':')
        if header == 'VmSize':
            try:
                value = int(re.search('[0-9]+', value).group(0))
            except AttributeError, ex:
                print 'failed with value "%s"' % value
                sys.exit(ex)
            break
    print '%5d %d' % (oi_count, value)
