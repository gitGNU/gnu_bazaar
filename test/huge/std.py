# $Id: std.py,v 1.4 2004/05/26 17:28:05 wrobell Exp $
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

import optparse
import sys
import time

opt_parser = optparse.OptionParser('%prog [options] module dsn')
opt_parser.add_option('-a', dest = 'amount', type = 'int', default = 10**4, \
            help = 'amount of objects per class')
opt_parser.add_option('-o', dest = 'opers', default = 'add, load, update, delete', \
            help = 'operation to run')
(options, args) = opt_parser.parse_args()

if len(sys.argv) < 3:
    opt_parser.error("incorrect number of arguments")

mod = __import__(sys.argv[1])
dsn = sys.argv[2]

class OrderItem(object):
    def __init__(self, __key__ = None, order_fkey = None, pos = None,
            article_fkey = None, quantity = None):
        self.__key__ = __key__
        self.order_fkey = order_fkey
        self.pos = pos
        self.article_fkey = article_fkey
        self.quantity = quantity

query = {
    'add'   : "insert into \"order_item\"" \
              " (__key__, \"pos\", \"quantity\"," \
              "   \"article_fkey\", \"order_fkey\")" \
              " values (%(__key__)s, %(pos)s, %(quantity)s," \
              "   %(article_fkey)s, %(order_fkey)s)",
    'load'  : "select __key__, order_fkey, pos, article_fkey, quantity" \
              "   from order_item",
    'del'   : "delete from order_item where __key__ = %s",
    'update': "update order_item set pos = %s where __key__ = %s",
}


dbc = mod.connect(dsn)


opers = [op.strip() for op in options.opers.split(',')]

# add
if 'add' in opers:
    dbc.cursor().execute("insert into article (__key__, name, price) values (1, 'apple', 2.2)")
    dbc.cursor().execute("insert into \"order\" (__key__, no, finished) values (1, 1, false)")
    ts = time.time()
    obj_list = []
    pos = 0
    for i in range(options.amount):
        obj = OrderItem()
        obj.order_fkey = 1
        pos += 1
        obj.pos = pos
        obj.article_fkey = 1
        obj.quantity = 10

        # set primary key value
        c = dbc.cursor()
        c.execute('select nextval(\'order_item_seq\')')
        obj.__key__ = c.fetchone()[0]

        # add data into database
        c.execute(query['add'], obj.__dict__)
        obj_list.append(obj)

    te = time.time()
    print 'add: %0.2f' % (te - ts)


# load
if 'load' in opers:
    ts = time.time()

    obj_list = []
    c = dbc.cursor()
    c.execute(query['load'])
    row = c.fetchone() 
    while row:
        obj = OrderItem(*row)
        obj_list.append(obj)
        row = c.fetchone() 
    te = time.time()
    print 'load: %0.2f' % (te - ts)

# update
if 'update' in opers:
    ts = time.time()
    for obj in obj_list:
        dbc.cursor().execute(query['update'], (obj.pos, obj.__key__))
    te = time.time()
    print 'update: %0.2f' % (te - ts)

# del
if 'delete' in opers:
    ts = time.time()
    for obj in obj_list:
        dbc.cursor().execute(query['del'], (obj.__key__, ))
    del obj_list
    te = time.time()
    print 'del: %0.2f' % (te - ts)
