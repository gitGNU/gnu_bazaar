# $Id: bzr.py,v 1.1 2003/11/26 20:48:39 wrobell Exp $
import optparse
import sys
import time

import bazaar.core

import app

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


Order     = app.Order
OrderItem = app.OrderItem
Article   = app.Article
Employee  = app.Employee

bzr = bazaar.core.Bazaar((Order, OrderItem, Article, Employee), dbmod = mod, dsn = dsn)
if options.commit:
    finish = bzr.commit
else:
    finish = bzr.rollback

art = Article({'name': 'apple', 'price': 2.22})
bzr.add(art)
ord = Order({'no': 1, 'finished': False})
bzr.add(ord)

def go(opers):
    if 'add' in opers:
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
        obj_list = bzr.getObjects(OrderItem)
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
