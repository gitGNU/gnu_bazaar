# $Id: core.py,v 1.14 2003/10/01 14:29:00 wrobell Exp $

import unittest

import bazaar.core

import app
import btest

"""
Test object loading and reloading from database.
"""

class ObjectLoadTestCase(btest.DBBazaarTestCase):
    """
    Test object loading and reloading from database.

    @ivar params: Object checking parameters (class, relation, relation columns, test
        function).
    """
    def testObjectLoading(self):
        """Test loaded application objects data integrity"""

        # check test application objects
        for cls in self.cls_list:
            self.checkObjects(cls, len(self.bazaar.getObjects(cls)))


    def testObjectReload(self):
        """Test application objects reloading"""

        # load objects
        for cls in self.cls_list:
            self.bazaar.getObjects(cls)

        dbc = self.bazaar.motor.db_conn.cursor()
        # change data in database
        dbc.execute('update article set price = price * 2')
        dbc.execute('update order_item set quantity = quantity * 2')
        dbc.execute('update "order" set finished = true')
        dbc.execute('update employee set phone = \'000\'')

        # reload objects (not immediately) and get them from database
        for cls in self.cls_list:
            self.bazaar.reloadObjects(cls)
            self.bazaar.getObjects(cls)

        # check data integrity
        for cls in self.cls_list:
            self.checkObjects(cls, len(self.bazaar.brokers[cls].cache))


    def testObjectReloadNow(self):
        """Test application objects immediate reloading"""

        # load objects
        for cls in self.cls_list:
            self.bazaar.getObjects(cls)

        dbc = self.bazaar.motor.db_conn.cursor()
        # change data in database
        dbc.execute('update article set price = price * 2')
        dbc.execute('update order_item set quantity = quantity * 2')
        dbc.execute('update "order" set finished = true')
        dbc.execute('update employee set phone = \'000\'')

        # reload objects immediately
        for cls in self.cls_list:
            self.bazaar.reloadObjects(cls, True)
            self.assertEqual(self.bazaar.brokers[cls].reload, False, \
                'class "%s" objects are not loaded from db' % cls)

        # check data integrity but do not load objects from database
        # (they should be loaded at this moment)
        for cls in self.cls_list:
            self.checkObjects(cls, len(self.bazaar.brokers[cls].cache))



class ModifyObjectTestCase(btest.DBBazaarTestCase):
    """
    Test application objects modification.
    """
    def testObjectAdding(self):
        """Test adding objects into database"""

        dbc = self.bazaar.motor.db_conn.cursor()

        # add and check order object
        order = app.Order()
        order.no = 1000
        order.finished = True
        self.bazaar.add(order)

        self.assert_(order.__key__ in self.bazaar.brokers[app.Order].cache, \
            'order object not found in cache')
        self.assertEqual(self.bazaar.brokers[app.Order].cache[order.__key__], order,
            'cache object mismatch')
        self.checkObjects(app.Order, key = order.__key__)

        # add and check article object
        article = app.Article()
        article.name = 'apple'
        article.price = 1.23

        self.bazaar.add(article)
        self.assert_(article.__key__ in self.bazaar.brokers[app.Article].cache, \
            'article object not found in cache')
        self.assertEqual(self.bazaar.brokers[app.Article].cache[article.__key__], article,
            'cache object mismatch')
        self.checkObjects(app.Article, key = article.__key__)

        # add and check order item object
        order_item = app.OrderItem()
        order_item.order = order
        order_item.pos = 0
        order_item.quantity = 2.123
        order_item.article = article

        self.bazaar.add(order_item)
        self.assert_(order_item.__key__ in self.bazaar.brokers[app.OrderItem].cache, \
            'order item object not found in cache')
        self.assertEqual(self.bazaar.brokers[app.OrderItem].cache[order_item.__key__], order_item,
            'cache object mismatch')
        self.checkObjects(app.OrderItem, key = order_item.__key__)

        # add and check employee object
        emp = app.Employee()
        emp.name = 'name'
        emp.surname = 'surname'
        emp.phone = '0123456789'

        self.bazaar.add(emp)
        self.assert_(emp.__key__ in self.bazaar.brokers[app.Employee].cache, \
            'employee object not found in cache')
        self.assertEqual(self.bazaar.brokers[app.Employee].cache[emp.__key__], emp,
            'cache object mismatch')
        self.checkObjects(app.Employee, key = emp.__key__)


    def testObjectUpdating(self):
        """Test updating objects in database"""

        order = self.bazaar.getObjects(app.Order)[0]
        order.finished = True
        self.bazaar.update(order)
        self.checkObjects(app.Order, key = order.__key__)

        article = self.bazaar.getObjects(app.Article)[0]
        article.price = 1.12
        self.bazaar.update(article)
        self.checkObjects(app.Article, key = article.__key__)

        order_item = self.bazaar.getObjects(app.OrderItem)[0]
        order_item.article = article
        self.bazaar.update(order_item)
        self.checkObjects(app.OrderItem, key = order_item.__key__)

        emp = self.bazaar.getObjects(app.Employee)[0]
        emp.phone = '00000'
        self.bazaar.update(emp)
        self.checkObjects(app.Employee, key = emp.__key__)
        

    def testObjectDeleting(self):
        """Test updating objects in database"""

        def delete(cls, data):
            self.bazaar.getObjects(cls)
            obj = self.findObj(cls, data)
            assert obj is not None
            key = obj.__key__
            self.bazaar.delete(obj)
            self.assert_(key not in self.getCache(cls), '%s object found in cache <- error, it is deleted' % cls)

        delete(app.Order, {'no': 1001})
        delete(app.Article, {'name': 'article'})
        delete(app.Employee, {'name': 'n1001', 'surname': 's1001'})



class TransactionsTestCase(btest.DBBazaarTestCase):
    """
    Test database transaction commiting and rollbacking.
    """
    def testCommit(self):
        """Test database transaction commit"""

        self.bazaar.getObjects(app.Employee)
        emp = self.findObj(app.Employee, {'name': 'n1001', 'surname': 's1001'})
        key = emp.__key__
        self.bazaar.delete(emp)
        self.bazaar.commit()
        self.bazaar.reloadObjects(app.Employee, now = True)

        # object is deleted, so it does not exist in cache due to objects
        # _immediate_ reload
        self.assert_(key not in self.getCache(app.Employee), \
            'employee object found in cache <- error, it is deleted')

        # readd object and commit, it should reappear in cache
        self.bazaar.add(emp)
        self.bazaar.commit()
        self.bazaar.reloadObjects(app.Employee, now = True)
        emp = self.findObj(app.Employee, {'name': 'n1001', 'surname': 's1001'})
        self.assert_(emp.__key__ in self.getCache(app.Employee), 'employee object not found in cache')


    def testRollback(self):
        """Test database transaction rollback"""

        self.bazaar.getObjects(app.Employee)
        emp = self.findObj(app.Employee, {'name': 'n1001', 'surname': 's1001'})
        self.bazaar.delete(emp)
        self.bazaar.rollback()

        # reload objects immediately, so we can find them in cache
        self.bazaar.reloadObjects(app.Employee, True)

        # objects is deleted, but it should exist in cache due to objects
        # reload
        self.assert_(emp.__key__ in self.getCache(app.Employee), \
            'employee object not found in cache')
