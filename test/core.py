# $Id: core.py,v 1.4 2003/08/07 18:00:04 wrobell Exp $

import unittest
import logging

import bazaar.core

import app
import btest

log = logging.getLogger('bazaar.test.core')

"""
<s>Test object loading and reloading from database.</s>
"""

class ObjectLoadTestCase(btest.DBBazaarTestCase):
    """
    <s>Test object loading and reloading from database.</s>

    <attr name = 'params'>
        Object checking parameters (class, relation, relation columns, test
        function).
    </attr>
    """
    def setUp(self):
        """
        <s>
            Create Bazaar layer instance and connect with database, then
            prepare object checking parameters.
        </s>
        """
        btest.DBBazaarTestCase.setUp(self)
        self.params = [
            { 
                'cls'     : app.Order,
                'relation': 'order',
                'cols'    : ('no', 'finished'),
                'test'    : self.checkOrder
            },
            { 
                'cls'     : app.Article,
                'relation': 'article',
                'cols'    : ('name', 'price'),
                'test'    : self.checkArticle
            },
            { 
                'cls'     : app.OrderItem,
                'relation': 'order_item',
                'cols'    : ('order', 'pos', 'quantity'),
                'test'    : self.checkOrderItem
            },
            { 
                'cls'     : app.Employee,
                'relation': 'employee',
                'cols'    : ('name', 'surname', 'phone'),
                'test'    : self.checkEmployee
            }
        ]


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



class ModifyObjectTestCase(btest.DBBazaarTestCase):
    """
    <s>Test application objects modification.</s>
    """
    def checkOrderObject(self, no, order):
        self.bazaar.motor.dbc.execute('select "no", "finished" from "order" where "no" = %(no)s'
            % { 'no': no})
        row = self.bazaar.motor.dbc.fetchone()
        self.assert_(self.checkOrder(row), 'data integrity test failed: %s' % str(row))


    def checkOrderItemObject(self, order_no, pos, order_item):
        self.bazaar.motor.dbc.execute(
            'select "order", "pos", "quantity" from "order_item" \
             where "order" = %(order)s and pos = %(pos)s', 
            {'order': order_no, 'pos': pos})
        row = self.bazaar.motor.dbc.fetchone()
        self.assert_(self.checkOrderItem(row), 'data integrity test failed: %s' % str(row))


    def checkArticleObject(self, name, article):
        self.bazaar.motor.dbc.execute(
            'select "name", "price" from "article" where "name" = %(name)s',
            { 'name': name })
        row = self.bazaar.motor.dbc.fetchone()
        self.assert_(self.checkArticle(row), 'data integrity test failed: %s' % str(row))


    def checkEmployeeObject(self, name, surname, emp):
        self.bazaar.motor.dbc.execute(
            'select "name", "surname", "phone" from "employee" \
             where "name" = %(name)s and "surname" = %(surname)s',
             { 'name': name, 'surname': surname })
        row = self.bazaar.motor.dbc.fetchone()
        self.assert_(self.checkEmployee(row), 'data integrity test failed: %s' % str(row))


    def testObjectAdding(self):
        """
        <s>Test adding objects into database.</s>
        """
        log.info('begin test of application objects adding')

        dbc = self.bazaar.motor.dbc

        # add and check order object
        order = app.Order({
            'no': 1000,
            'finished': True
        })
        self.bazaar.add(order)
        self.assert_(1000 in self.bazaar.brokers[app.Order].cache, \
            'order object not found in cache')
        self.assertEqual(self.bazaar.brokers[app.Order].cache[1000], order,
            'cache object mismatch')
        self.checkOrderObject(1000, order)

        # add and check article object
        article = app.Article({
            'name': 'apple',
            'price': 1.23
        })
        self.bazaar.add(article)
        self.assert_('apple' in self.bazaar.brokers[app.Article].cache, \
            'article object not found in cache')
        self.assertEqual(self.bazaar.brokers[app.Article].cache['apple'], article,
            'cache object mismatch')
        self.checkArticleObject('apple', article)

        # add and check order item object
        order_item = app.OrderItem({
            'order': 1000,
            'pos': 0,
            'quantity': 2.123,
            'article': 'apple'
        })
        self.bazaar.add(order_item)
        self.assert_((1000, 0) in self.bazaar.brokers[app.OrderItem].cache, \
            'order item object not found in cache')
        self.assertEqual(self.bazaar.brokers[app.OrderItem].cache[(1000, 0)], order_item,
            'cache object mismatch')
        self.checkOrderItemObject(1000, 0, order_item)

        # add and check employee object
        emp = app.Employee({
            'name': 'name',
            'surname': 'surname',
            'phone': '0123456789'
        })
        self.bazaar.add(emp)
        self.assert_(('name', 'surname') in self.bazaar.brokers[app.Employee].cache, \
            'employee object not found in cache')
        self.assertEqual(self.bazaar.brokers[app.Employee].cache[('name', 'surname')], emp,
            'cache object mismatch')
        self.checkEmployeeObject('name', 'surname', emp)

        log.info('finished test of application objects adding')


    def testObjectUpdating(self):
        """
        <s>Test updating objects in database.</s>
        """
        log.info('begin test of application objects updating')

        order = self.bazaar.getObjects(app.Order)[0]
        order.finished = True
        self.bazaar.update(order)
        self.checkOrderObject(order.key, order)

        article = self.bazaar.getObjects(app.Article)[0]
        article.price = 1.12
        self.bazaar.update(article)
        self.checkArticleObject(article.key, article)

        order_item = self.bazaar.getObjects(app.OrderItem)[0]
        order_item.article = 'art 09'
        self.bazaar.update(order_item)
        self.checkOrderItemObject(order_item.order, order_item.pos, order_item)

        emp = self.bazaar.getObjects(app.Employee)[0]
        emp.phone = '00000'
        self.bazaar.update(emp)
        self.checkEmployeeObject(emp.name, emp.surname, emp)

        log.info('finished test of application objects updating')


    def testObjectDeleting(self):
        """
        <s>Test updating objects in database.</s>
        """
        log.info('begin test of application objects deleting')

#        order_item = self.bazaar.getObjects(app.OrderItem)[0]
#        self.bazaar.delete(order_item)
#        self.assert_(order_item.key not in self.bazaar.brokers[app.OrderItem].cache, \
#            'order item object found in cache <- error, it is deleted')

#        order = self.bazaar.getObjects(app.Order)[0]
#        self.bazaar.delete(order)
#        self.assert_(order.key not in self.bazaar.brokers[app.Order].cache, \
#            'order object found in cache <- error, it is deleted')

#        article = self.bazaar.getObjects(app.Article)[0]
#        self.bazaar.delete(article)
#        self.assert_(article.key not in self.bazaar.brokers[app.Article].cache, \
#            'article object found in cache <- error, it is deleted')

        self.bazaar.getObjects(app.Employee)
        emp = self.bazaar.brokers[app.Employee].cache[('n1001', 's1001')]
        self.bazaar.delete(emp)
        self.assert_(emp.key not in self.bazaar.brokers[app.Employee].cache, \
            'employee object found in cache <- error, it is deleted')

        log.info('finished test of application objects deleting')


class TransactionsTestCase(btest.DBBazaarTestCase):
    """
    <s>Test database transaction commiting and rollbacking.</s>
    """
    def testCommit(self):
        """
        <s>Test database transaction commit.</s>
        """
        self.bazaar.getObjects(app.Employee)
        emp = self.bazaar.brokers[app.Employee].cache[('n1001', 's1001')]
        self.bazaar.delete(emp)
        self.bazaar.commit()
        self.bazaar.reloadObjects(app.Employee)
        # objects is deleted, so it does not exist in cache due to objects
        # reload
        self.assert_(emp.key not in self.bazaar.brokers[app.Employee].cache, \
            'employee object found in cache <- error, it is deleted')
        self.bazaar.add(emp)
        self.bazaar.commit()
        self.bazaar.reloadObjects(app.Employee)
        self.assert_(emp.key in self.bazaar.brokers[app.Employee].cache, \
            'employee object not found in cache')


    def testRollback(self):
        """
        <s>Test database transaction rollback.</s>
        """
        self.bazaar.getObjects(app.Employee)
        emp = self.bazaar.brokers[app.Employee].cache[('n1001', 's1001')]
        self.bazaar.delete(emp)
        self.bazaar.rollback()

        # reload objects immediately, so we can find them in cache
        self.bazaar.reloadObjects(app.Employee, True)

        # objects is deleted, but it should exist in cache due to objects
        # reload
        self.assert_(emp.key in self.bazaar.brokers[app.Employee].cache, \
            'employee object not found in cache')
