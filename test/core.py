# $Id: core.py,v 1.3 2003/07/19 10:09:14 wrobell Exp $

import unittest
import logging

import bazaar.core

import app
import btest

log = logging.getLogger('bazaar.test.core')

"""
<s>Test object loading and reloading from database.</s>
"""

class ObjectLoadTestCase(btest.BazaarTestCase):
    """
    <s>Test object loading and reloading from database.</s>

    <attr name = 'params'>
        Object checking parameters (class, relation, relation columns, test
        function).
    </attr>
    """
    def setUp(self):
        """
        <s>Create Bazaar layer instance and connect with database.</s>
        """
        btest.BazaarTestCase.setUp(self)
        self.bazaar.connectDB(app.dsn)
        self.params = [
            { 
                'cls'     : app.Order,
                'relation': 'order',
                'cols'    : ('no', 'finished'),
                'test'    : self.checkOrders
            },
            { 
                'cls'     : app.Article,
                'relation': 'article',
                'cols'    : ('name', 'price'),
                'test'    : self.checkArticles
            },
            { 
                'cls'     : app.OrderItem,
                'relation': 'order_item',
                'cols'    : ('order', 'pos', 'quantity'),
                'test'    : self.checkOrderItems
            },
            { 
                'cls'     : app.Employee,
                'relation': 'employee',
                'cols'    : ('name', 'surname', 'phone'),
                'test'    : self.checkEmployees
            }
        ]


    def tearDown(self):
        """
        <s>Close database connection.</s>
        """
        self.bazaar.closeDBConn()


    def checkObjects(self, amount, columns, relation, test):
        """
        <s>Check all application objects data integrity.</s>

        <attr name = 'amount'>Amount of objects.</attr>
        <attr name = 'columns'>List of relation columns.</attr>
        <attr name = 'relation'>Relation name.</attr>
        <attr name = 'test'>
            Test function. Tests if for given row the object exists and the
            object data are integral with row data (returns true
            on success).
        </attr>
        """
        dbc = self.bazaar.motor.dbc
        query = 'select %s from "%s"' % (', '.join(['"%s"' % col for col in columns]), relation)
        dbc.execute(query)

        self.assertEqual(amount, dbc.rowcount, \
            'objects count: %d, row count: %d' % (amount, dbc.rowcount))

        row = dbc.fetchone()
        while row:
            self.assert_(test(row), 'data integrity test failed: %s' % str(row))
            row = dbc.fetchone()


    def checkOrders(self, row):
        """
        <s>Order class data integrity test function.</s>
        """
        order = self.bazaar.brokers[app.Order].cache[row[0]]
        return order.no == row[0] and order.finished == row[1]


    def checkEmployees(self, row):
        """
        <s>Employee class data integrity test function.</s>
        """
        emp = self.bazaar.brokers[app.Employee].cache[(row[0], row[1])]
        return emp.name == row[0] and emp.surname == row[1] and emp.phone == row[2]


    def checkArticles(self, row):
        """
        <s>Article class data integrity test function.</s>
        """
        art = self.bazaar.brokers[app.Article].cache[row[0]]
        return art.name == row[0] and art.price == row[1]


    def checkOrderItems(self, row):
        """
        <s>OrderItem class data integrity test function.</s>
        """
        oi = self.bazaar.brokers[app.OrderItem].cache[(row[0], row[1])]
        return oi.order == row[0] and oi.pos == row[1] and oi.quantity == row[2]


    def testObjectLoading(self):
        """
        <s>Test loaded application objects data integrity.</s>
        """

        log.info('begin test of loading application objects data integrity')

        # check test application objects
        for p in self.params:
            self.checkObjects(len(self.bazaar.getObjects(p['cls'])), \
                p['cols'], p['relation'], p['test'])

        log.info('finished test of loading application objects data integrity')


    def testObjectReload(self):
        """
        <s>Test application objects reloading.</s>
        """
        log.info('begin test of application objects reloading')

        # load objects
        for cls in self.cls_list:
            self.bazaar.getObjects(cls)

        # change data in database
        self.bazaar.motor.dbc.execute('update article set price = price * 2')
        self.bazaar.motor.dbc.execute('update order_item set quantity = quantity * 2')
        self.bazaar.motor.dbc.execute('update "order" set finished = true')
        self.bazaar.motor.dbc.execute('update employee set phone = \'000\'')

        # reload objects (not immediately) and get them from database
        for cls in self.cls_list:
            self.bazaar.reloadObjects(cls)
            self.bazaar.getObjects(cls)

        # check data integrity
        for p in self.params:
            self.checkObjects(len(self.bazaar.brokers[p['cls']].cache), \
                p['cols'], p['relation'], p['test'])

        log.info('finished test of application objects reloading')


    def testObjectReloadNow(self):
        """
        <s>Test application objects reloading.</s>
        """
        log.info('begin test of application objects immediate reloading')

        # load objects
        for cls in self.cls_list:
            self.bazaar.getObjects(cls)

        # change data in database
        self.bazaar.motor.dbc.execute('update article set price = price * 2')
        self.bazaar.motor.dbc.execute('update order_item set quantity = quantity * 2')
        self.bazaar.motor.dbc.execute('update "order" set finished = true')
        self.bazaar.motor.dbc.execute('update employee set phone = \'000\'')

        # reload objects immediately
        for cls in self.cls_list:
            self.bazaar.reloadObjects(cls, True)
            self.assertEqual(self.bazaar.brokers[cls].reload, False, \
                'class "%s" objects are not loaded from db' % cls)

        # check data integrity but do not load objects from database
        # (they should be loaded at this moment)
        for p in self.params:
            self.checkObjects(len(self.bazaar.brokers[p['cls']].cache), \
                p['cols'], p['relation'], p['test'])

        log.info('finished test of application objects immediate reloading')
