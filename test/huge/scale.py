#!/usr/bin/python

import sys
import time

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
ord = Order({'no': 1, 'finished': False})
bzr.add(ord)

ts = time.time()
items = ord.items
for i in range(amount):
    oi = OrderItem()
    oi.article = art
    oi.quantity = 10
    oi.pos = i
    items.append(oi)
    bzr.add(oi)
items.update()
bzr.reloadObjects(OrderItem)
Order.items.reloadData(True)
te = time.time()
print '%5d %0.2f' % (amount, te - ts)
