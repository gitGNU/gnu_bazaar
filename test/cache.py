# $Id: cache.py,v 1.3 2003/11/26 02:34:31 wrobell Exp $

import unittest
import gc
from ConfigParser import ConfigParser

import bazaar.core
import bazaar.config

import app
import btest

"""
Test object and association data cache.
"""

class LazyTestCase(btest.DBBazaarTestCase):
    """
    Test lazy cache.
    """
    def testObjectLoading(self):
        """Test object lazy cache"""
        config = ConfigParser()
        config.add_section('bazaar.cls')
        config.set('bazaar.cls', 'app.Article.cache', 'bazaar.cache.LazyObject')

        self.bazaar.setConfig(bazaar.config.CPConfig(config))
        self.bazaar.connectDB()

        articles = []
        abroker = self.bazaar.brokers[app.Article]
        for i in range(1, 4):
            articles.append(abroker.get(i))

        keys = [art.__key__ for art in articles]
        self.assertEqual(len(keys), len(abroker.cache))

        for art in articles:
            self.assert_(art.__key__ in abroker.cache)
            self.assertEqual(art, abroker.get(art.__key__))

        # remove all strong references...
        del articles
        del art
        gc.collect()
        # ... now cache should be empty
        self.assertEqual(len(abroker.cache), 0)


    def testAscLoading(self):
        """Test association data lazy cache"""
        config = ConfigParser()
#        config.add_section('bazaar.cls')
#        config.set('bazaar.cls', 'app.Order.cache', 'bazaar.cache.LazyObject')
        config.add_section('bazaar.asc')
        config.set('bazaar.asc', 'app.Order.items.cache', \
            'bazaar.cache.LazyAssociation')
        config.set('bazaar.asc', 'app.Employee.orders.cache', \
            'bazaar.cache.LazyAssociation')

        self.bazaar.setConfig(bazaar.config.CPConfig(config))
        self.bazaar.connectDB()

        order = self.bazaar.getObjects(app.Order)[0]
        oikeys = [oi.__key__ for oi in order.items]
        oikeys.sort()

        dbc = self.bazaar.motor.conn.cursor()
        dbc.execute('select __key__ from "order_item" where order_fkey = %s', [order.__key__])
        dbkeys = [row[0] for row in dbc.fetchall()]
        dbkeys.sort()

        self.assertEqual(oikeys, dbkeys)

        art = self.bazaar.getObjects(app.Article)[0]
                                                                                                                               
        oi1 = app.OrderItem()
        oi1.pos = 1000
        oi1.quantity = 10.3
        oi1.article = art
                                                                                                                               
        oi2 = app.OrderItem()
        oi2.pos = 1001
        oi2.quantity = 10.4
        oi2.article = art

        order.items.append(oi1)
        order.items.append(oi2)

        self.bazaar.reloadObjects(app.Order)
        del order
        gc.collect()
        self.assertEqual(len(app.Order.items.ref_buf), 0)
        self.assertEqual(len(app.Order.items.cache), 0)


        emp = self.bazaar.getObjects(app.Employee)[0]
        ordkeys = [ord.__key__ for ord in emp.orders]
        ordkeys.sort()

        dbc = self.bazaar.motor.conn.cursor()
        dbc.execute('select "order" from "employee_orders" where employee = %s', [emp.__key__])
        dbkeys = [row[0] for row in dbc.fetchall()]
        dbkeys.sort()

        self.assertEqual(ordkeys, dbkeys)

        art = self.bazaar.getObjects(app.Article)[0]
                                                                                                                               
        ord1 = app.Order()
        ord1.no = 1000
        ord1.finished = False
                                                                                                                               
        ord2 = app.Order()
        ord1.no = 1001
        ord1.finished = True

        emp.orders.append(ord1)
        emp.orders.append(ord2)

        self.bazaar.reloadObjects(app.Employee)
        del emp
        gc.collect()
        self.assertEqual(len(app.Employee.orders.ref_buf), 0)
        self.assertEqual(len(app.Employee.orders.cache), 0)
            


class FullTestCase(btest.DBBazaarTestCase):
    """
    Test full cache.
    """
    def testObjectLoading(self):
        """Test object full cache"""
        # get one object...
        abroker = self.bazaar.brokers[app.Article]
        abroker.get(1)

        # ... and check if all are loaded
        self.checkObjects(app.Article, len(abroker.cache))


    def testAscLoading(self):
        """Test association full cache"""
        order = self.bazaar.getObjects(app.Order)[0]
        self.checkOrdAsc()
