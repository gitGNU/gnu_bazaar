#!/usr/bin/python

import sys
import os
import re

import bazaar.core

import app

Order     = app.Order
OrderItem = app.OrderItem
Article   = app.Article
Employee  = app.Employee

mod = __import__(sys.argv[1])
dsn = sys.argv[2]
amount = int(sys.argv[3])

bzr = bazaar.core.Bazaar((Order, OrderItem, Article, Employee), \
    dbmod = mod, dsn = dsn)

art = Article({'name': 'apple', 'price': 2.22})
bzr.add(art)

for j in range(0, amount, 5000):
    ord = Order({'no': j, 'finished': False})
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
