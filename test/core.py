# $Id: core.py,v 1.20 2004/03/23 13:48:27 wrobell Exp $
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
        for cls in self.cls_list:
            self.checkObjects(cls, len(self.bazaar.getObjects(cls)))


    def testObjectReload(self):
        """Test application objects reloading"""

        # load objects
        for cls in self.cls_list:
            self.bazaar.getObjects(cls)

        dbc = self.bazaar.motor.conn.cursor()
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

        dbc = self.bazaar.motor.conn.cursor()
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



class CreateObjectTestCase(btest.DBBazaarTestCase):
    """
    Test application object creation.
    """
    def testObjectCreation(self):
        """Test object creation"""
        # check for attributes with no value assigned before attribute
        # access
        apple = app.Article()
        self.assertEqual(apple.name, None)
        self.assertEqual(apple.price, None)
        self.assertEqual(apple.__dict__['name'], None)
        self.assertEqual(apple.__dict__['price'], None)

        # check attribute value assigning
        apple = app.Article()
        apple.name = 'apple'
        apple.price = 2.33
        self.assertEqual(apple.name, 'apple')
        self.assertEqual(apple.price, 2.33)

        # check attribute value assigning via constructor
        apple = app.Article(name = 'apple', price = 3)
        self.assertEqual(apple.name, 'apple')
        self.assertEqual(apple.price, 3)

        # load all articles, so they will not be reloaded when checking
        # order item article below
        self.bazaar.getObjects(app.Article)

        self.bazaar.add(apple)

        # check attribute value assigning when attribute is an reference
        oi = app.OrderItem(pos = 1, quantity = 100, article = apple)
        self.assertEqual(oi.article, apple)
        self.assertEqual(oi.article_fkey, apple.__key__)



class ModifyObjectTestCase(btest.DBBazaarTestCase):
    """
    Test application objects modification.
    """
    def testObjectAdding(self):
        """Test adding objects into database"""

        dbc = self.bazaar.motor.conn.cursor()

        # load all objects before adding new objects into database;
        # this way added objects will not be reloaded when accessing object
        # cache
        for cls in self.cls_list:
            self.bazaar.getObjects(cls)

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
        """Test deleting objects from database"""

        def delete(cls, data):
            self.bazaar.getObjects(cls)
            obj = self.bazaar.find(cls, data).next()
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
        emp = self.bazaar.find(app.Employee, \
            {'name': 'n1001', 'surname': 's1001'}).next()
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
        emp = self.bazaar.find(app.Employee, \
            {'name': 'n1001', 'surname': 's1001'}).next()
        self.assert_(emp.__key__ in self.getCache(app.Employee), 'employee object not found in cache')


    def testRollback(self):
        """Test database transaction rollback"""

        self.bazaar.getObjects(app.Employee)
        emp = self.bazaar.find(app.Employee, {'name': 'n1001', 'surname': 's1001'}).next()
        key = emp.__key__
        self.bazaar.delete(emp)
        self.bazaar.rollback()

        # reload objects immediately, so we can find them in cache
        self.bazaar.reloadObjects(app.Employee, True)

        # objects is deleted, but it should exist in cache due to objects
        # reload
        self.assert_(key in self.getCache(app.Employee), \
            'employee object not found in cache')
