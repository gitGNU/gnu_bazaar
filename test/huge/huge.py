import optparse
import sys
import random

import bazaar.core

import test.app

opt_parser = optparse.OptionParser('%prog [options] module dsn')
opt_parser.add_option('-n', dest = 'nonobj', action = 'store_true', \
            help = 'do not use bazaar layer')
opt_parser.add_option('-p', dest = 'prof', action = 'store_true', \
            help = 'use profiler')
opt_parser.add_option('-a', dest = 'amount', type = 'int', default = 10**3, \
            help = 'amount of objects per class')
opt_parser.add_option('-c', dest = 'commit', action = 'store_true', \
            help = 'commit instead of rollback')
opt_parser.add_option('-f', dest = 'func', default = 'load', \
            help = 'run test function: load (default), add, update, delete')
(options, args) = opt_parser.parse_args()

if len(sys.argv) < 3:
    opt_parser.error("incorrect number of arguments")

mod = __import__(sys.argv[1])
dsn = sys.argv[2]

if options.nonobj:
    test_type = 'non bazaar'
    class Order(object): pass
    class OrderItem(object): pass
    class Article(object): pass
    class Employee(object):
        def __init__(self, phone = None, surname = None, name = None):
            self.phone = phone
            self.surname = surname
            self.name = name

    i = 0
    qadd = {
        Order     : '',
        OrderItem : 'insert into "order_item" \
                (__key__, "pos", "quantity", "article_fkey", "order_fkey") \
                values (%(__key__)s, %(pos)s, %(quantity)s, %(article_fkey)s, %(order_fkey)s)',
        Article   : '',
        Employee  : 'insert into "employee" \
                (__key__, "phone", "surname", "name") \
                values (%(__key__)s, %(phone)s, %(surname)s, %(name)s)'
    }
    qload = {
        Order     : '',
        OrderItem : 'insert into "order_item" \
                (__key__, "pos", "quantity", "article_fkey", "order_fkey") \
                values (%(__key__)s, %(pos)s, %(quantity)s, %(article_fkey)s, %(order_fkey)s)',
        Article   : '',
        Employee  : 'select __key__, "phone", "surname", "name" from "employee"'
    }
    dbc = mod.connect(dsn)
    if options.commit:
        finish = dbc.commit
    else:
        finish = dbc.rollback
    obj_list = []

    def add(obj):
        global dbc, i
        obj.__key__ = i
        i += 1
        dbc.cursor().execute(qadd[obj.__class__], obj.__dict__)
        obj_list.append(obj)

    def load(cls):
        global dbc
        c = dbc.cursor()
        c.execute(qload[cls])
        row = c.fetchone() 
        while row:
            obj = cls(row)
            obj_list.append(obj)
            row = c.fetchone() 
        
else:
    test_type = 'bazaar'
    Order     = test.app.Order
    OrderItem = test.app.OrderItem
    Article   = test.app.Article
    Employee  = test.app.Employee
    bzr = bazaar.core.Bazaar((Order, OrderItem, Article, Employee), mod, dsn)
    if options.commit:
        finish = bzr.commit
    else:
        finish = bzr.rollback
    add = bzr.add
    load = bzr.getObjects

def fadd():
    for i in range(options.amount):
        emp = Employee()
        emp.name = '%d' % i
        emp.surname = '%d' % i
        emp.phone = '%d' % i
        add(emp)

def fload():
    load(Employee)

func = fload

if options.func == 'add':
    func = fadd

if options.prof:
    import hotshot, hotshot.stats
    prof = hotshot.Profile("bzr.prof")
    prof.runcall(func)
    prof.close()
    stats = hotshot.stats.load("bzr.prof")
    stats.strip_dirs()
    stats.sort_stats('time', 'calls')
    stats.print_stats(20)
else:
    import time
    t = time.time()
    func()
    print '%10s: %.2f' % (test_type, time.time() - t)

finish()
