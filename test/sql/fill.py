#!/usr/bin/python

# $Id: fill.py,v 1.1 2003/07/18 09:10:14 wrobell Exp $

from __future__ import generators

import sys
import random
import psycopg
import logging

log = logging.getLogger('fill')

AMOUNT_EMPLOYEE = 10
AMOUNT_ORDER    = 10
AMOUNT_MAX_ORDER_ITEMS = 20
AMOUNT_ARTICLE = 10

class Row(dict):
    """
    Database row, there is relation and data to insert into the relation.
    """
    def __init__(self, relation, data):
        self.relation = relation
        self.update(data)


def insert(dbc, row):
    """
    Insert a row into database.
    """
    query = 'insert into "%s" (%s) values (%s)' % (row.relation, \
            ', '.join(['"%s"' % item for item in row.keys()]),
            ', '.join(['%%(%s)s' % item for item in row.keys()]))

    if __debug__: print 'query: %s' % query

    dbc.execute(query, row)


def gen_employees(amount):
    for i in xrange(amount):
        yield Row('employee', \
            {'name': 'p%02d' % i, 'surname': 's%02d' % i, 'phone': '%10d' % i})


def gen_articles(amount):
    for i in xrange(amount):
        yield Row('article', {'name': 'art %02d' % i, 'price': random.uniform(0, 10)})


def gen_order_items(order, amount):
    for i in xrange(1, random.randint(2, amount)):
        yield Row('order_item', {
                'order': order,
                'article': 'art %02d' % random.randint(1, AMOUNT_ARTICLE-1),
                'pos': i,
                'quantity': random.uniform(1, 10)
        })


def gen_orders(amount):
    for i in xrange(amount):
        yield Row('order', {
            'no': i,
            'finished': 'false'
        })

        for item in gen_order_items(i, AMOUNT_MAX_ORDER_ITEMS):
            yield item

        for j in xrange(1, random.randint(1, AMOUNT_EMPLOYEE - 1)):
            yield Row('employee_orders', {
                'employee_name': 'p%02d' % j,
                'employee_surname': 's%02d' % j,
                'order': i,
            })

if len(sys.argv) != 2:
    print """bazaar test data generator

usage:
    fill.py dsn
"""
    sys.exit(1)

db = psycopg.connect(sys.argv[1])
dbc = db.cursor()

for row in gen_employees(AMOUNT_EMPLOYEE):
    insert(dbc, row)

for row in gen_articles(AMOUNT_ARTICLE):
    insert(dbc, row)

for row in gen_orders(AMOUNT_ORDER):
    insert(dbc, row)

db.commit()
