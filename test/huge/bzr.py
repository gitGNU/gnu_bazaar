# $Id: bzr.py,v 1.5 2005/05/12 18:29:58 wrobell Exp $
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

import optparse
import sys
import time

import bazaar.core

import bazaar.test.app

opt_parser = optparse.OptionParser('%prog [options] module dsn')
opt_parser.add_option('-p', dest = 'prof', action = 'store_true', \
            help = 'use profiler')
opt_parser.add_option('-a', dest = 'amount', type = 'int', default = 10**4, \
            help = 'amount of objects per class')
opt_parser.add_option('-c', dest = 'commit', action = 'store_true', \
            help = 'commit instead of rollback')
opt_parser.add_option('-o', dest = 'opers', default = 'add, load, update, delete', \
            help = 'operation to run')
(options, args) = opt_parser.parse_args()

if len(sys.argv) < 3:
    opt_parser.error("incorrect number of arguments")

mod = __import__(sys.argv[1])
dsn = sys.argv[2]


Order     = bazaar.test.app.Order
OrderItem = bazaar.test.app.OrderItem
Article   = bazaar.test.app.Article
Employee  = bazaar.test.app.Employee

bzr = bazaar.core.Bazaar(
    (Order, OrderItem, Article, Employee),
    dbmod = mod, dsn = dsn,
    seqpattern = 'select nextval(\'%s\')')
if options.commit:
    finish = bzr.commit
else:
    finish = bzr.rollback

def go(opers):
    if 'add' in opers:
        art = Article(name = 'apple', price = 2.22)
        bzr.add(art)
        ord = Order(no = 1, finished = False)
        bzr.add(ord)
        # add
        ts = time.time()
        pos = 0
        for i in range(options.amount):
            obj = OrderItem()
            obj.order = ord
            obj.article = art
            obj.quantity = 10
            pos += 1
            obj.pos = pos
            bzr.add(obj)
        te = time.time()
        print 'add: %0.2f' % (te - ts)

    if 'load' in opers:
        # load
        ts = time.time()
        obj_list = list(bzr.getObjects(OrderItem))
        te = time.time()
        print 'load: %0.2f' % (te - ts)

    if 'update' in opers:
        # update
        ts = time.time()
        for obj in obj_list:
            bzr.update(obj)
        te = time.time()
        print 'update: %0.2f' % (te - ts)

    if 'delete' in opers:
        # del
        ts = time.time()
        for obj in obj_list:
            bzr.delete(obj)
        te = time.time()
        print 'del: %0.2f' % (te - ts)


opers = [op.strip() for op in options.opers.split(',')]
if options.prof:
    import hotshot, hotshot.stats
    prof = hotshot.Profile("bzr.prof")
    prof.runcall(go, opers)
    prof.close()
    stats = hotshot.stats.load("bzr.prof")
    stats.strip_dirs()
    stats.sort_stats('time', 'calls')
    stats.print_stats(20)

#    # old profiler:
#    import profile, pstats
#    profile.run('go(opers)', 'bzr.prof')
#    stats = pstats.Stats("bzr.prof")
#    stats.strip_dirs()
#    stats.sort_stats('time', 'calls')
#    stats.print_stats(20)
else:
    go(opers)

finish()
