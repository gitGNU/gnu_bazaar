#!/usr/bin/python
#
# $Id: fill.py,v 1.14 2005/05/10 16:57:13 wrobell Exp $
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

import sys
import random
import sets

AMOUNT_EMPLOYEE = 10
AMOUNT_ORDER    = 10
AMOUNT_MAX_ORDER_ITEMS = 20
AMOUNT_ARTICLE = 10

if len(sys.argv) != 3:
    print 'usage: %s <dbmodule> <dsn>' % sys.argv[0]
    print '  i.e. %s psycopg "dbname = bazaar"' % sys.argv[0]
    sys.exit(1)

dbmodule = __import__(sys.argv[1])
db = dbmodule.connect(sys.argv[2])

class Row(dict):
    """
    Database row, there is relation and data to insert into the relation.
    """
    def __init__(self, relation, data):
        self.relation = relation
        self.update(data)


class ObjectRow(Row):
    def __init__(self, relation, data):
        super(ObjectRow, self).__init__(relation, data)
        if '__key__' not in self:
            self['__key__'] = getKey(self.relation)


    def __hash__(self):
        return  self['__key__']


def getKey(relation):
    """
    Get primary key value for given relation.
    """
    dbc = db.cursor()
    dbc.execute('select nextval(%s)', ('%s_seq' % relation, ))
    return dbc.fetchone()[0]


def insert(db, row):
    """
    Insert a row into database.
    """
    dbc = db.cursor()
    query = 'insert into "%s" (%s) values (%s)' % (row.relation, \
            ', '.join(['"%s"' % item for item in row.keys()]),
            ', '.join(['%%(%s)s' % item for item in row.keys()]))

    if __debug__: print 'query: %s' % query

    dbc.execute(query, row)


employees = [ \
    ObjectRow('employee', {'name': 'p%02d' % i, 'surname': 's%02d' % i, 'phone': '%10d' % i}) \
        for i in xrange(AMOUNT_EMPLOYEE) \
]


articles = [ \
    ObjectRow('article', {'name': 'art %02d' % i, 'price': random.uniform(0, 10)}) \
        for i in xrange(AMOUNT_ARTICLE) \
]


def get_random_row(rows):
    return rows[random.randint(0, len(rows) - 1)]


def gen_order_items(order, amount):
    for i in xrange(1, random.randint(5, amount)):
        yield ObjectRow('order_item', {
                'order_fkey': order,
                'article_fkey': get_random_row(articles)['__key__'],
                'pos': i,
                'quantity': random.uniform(1, 10)
        })


def gen_orders(amount):
    for i in xrange(1, amount + 1):
        row = ObjectRow('order', {
            'no': i,
            'finished': 'false'
        })
        yield row

        for item in gen_order_items(row['__key__'], AMOUNT_MAX_ORDER_ITEMS):
            yield item

        emps_amount = random.randint(1, len(employees) - 1)
        if emps_amount < 2: emps_amount = 3
        emps = sets.Set([ get_random_row(employees) for j in xrange(1, emps_amount) ])
        assert len(emps) >= 1
        for emp in emps:
            yield Row('employee_orders', {
                'employee': emp['__key__'],
                'order': row['__key__'],
            })


for row in employees:
    insert(db, row)

for row in articles:
    insert(db, row)

for row in gen_orders(AMOUNT_ORDER):
    insert(db, row)

# insert article, order and employee rows, so we can delete them by test
# cases
insert(db, ObjectRow('article', {'__key__': 1000, 'name': 'article', 'price': random.uniform(0, 10)}))
insert(db, ObjectRow('order', {'__key__': 1000, 'no': 1001, 'finished': 'false' }))
insert(db, ObjectRow('employee', {'__key__': 1000, 'name': 'n1001', 'surname': 's1001', 'phone': '1001'}))

insert(db, ObjectRow('boss', {'__key__': 1001, 'dep_fkey': 1001, 'name': 'name0', 'surname': 'surname0', 'phone': 'phone0'}))
insert(db, ObjectRow('boss', {'__key__': 1002, 'dep_fkey': 1002, 'name': 'name1', 'surname': 'surname1', 'phone': 'phone1'}))
insert(db, ObjectRow('department', {'__key__': 1001, 'boss_fkey': 1001}))
insert(db, ObjectRow('department', {'__key__': 1002, 'boss_fkey': 1002}))

for rel in ['order', 'employee', 'article', 'order_item', 'department']:
    db.cursor().execute('select setval(\'%s_seq\', max(__key__)) from "%s"' % (rel, rel))

db.commit()
