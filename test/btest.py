# $Id: btest.py,v 1.8 2003/09/24 18:19:10 wrobell Exp $

import unittest

import bazaar.core

import app

class BazaarTestCase(unittest.TestCase):
    """
    Base class for Bazaar layer tests.

    @ivar bazaar: Bazaar layer object.
    @ivar cls_list: List of test application classes.
    """
    def setUp(self):
        """
        Create Bazaar layer object.
        """
        self.cls_list = (app.Order, app.Employee, app.Article, app.OrderItem)
        self.bazaar = bazaar.core.Bazaar(self.cls_list, app.db_module)


class DBBazaarTestCase(BazaarTestCase):
    """
    Base class for Bazaar layer tests with enabled database connection.
    """
    def setUp(self):
        """
        Create Bazaar layer instance and connect with database.
        """
        BazaarTestCase.setUp(self)
        self.bazaar.connectDB(app.dsn)


    def tearDown(self):
        """
        Close database connection.
        """
        self.bazaar.closeDBConn()


    def checkObjects(self, cls, amount = None, key = None):
        """
        Check all application objects data integrity.

        @param amount: Amount of objects.
        """
        params = {
            app.Order: {
                'relation': 'order',
                'cols'    : ('no', 'finished'),
                'test'    : self.checkOrder
            },
            app.Article: {
                'relation': 'article',
                'cols'    : ('name', 'price'),
                'test'    : self.checkArticle
            },
            app.OrderItem: {
                'relation': 'order_item',
                'cols'    : ('order_fkey', 'pos', 'quantity'),
                'test'    : self.checkOrderItem
            },
            app.Employee: {
                'relation': 'employee',
                'cols'    : ('name', 'surname', 'phone'),
                'test'    : self.checkEmployee
            },
        }

        dbc = self.bazaar.motor.db_conn.cursor()

        query = 'select "__key__", %s from "%s"' \
                % (', '.join(['"%s"' % col for col in params[cls]['cols']]), params[cls]['relation'])

        if key is not None:
            query += 'where __key__ = %d' % key

        dbc.execute(query)

        if amount is not None:
            self.assertEqual(amount, dbc.rowcount, \
                'objects count: %d, row count: %d' % (amount, dbc.rowcount))

        row = dbc.fetchone()
        while row:
            self.assert_(params[cls]['test'](row[0], row[1:]), 'data integrity test failed: %s' % str(row))
            row = dbc.fetchone()


    def checkOrder(self, key, row):
        """
        Order class data integrity test function.
        """
        order = self.bazaar.brokers[app.Order].cache[key]
        return order.no == row[0] and order.finished == row[1]


    def checkEmployee(self, key, row):
        """
        Employee class data integrity test function.
        """
        emp = self.bazaar.brokers[app.Employee].cache[key]
        return emp.name == row[0] and emp.surname == row[1] and emp.phone == row[2]


    def checkArticle(self, key, row):
        """
        Article class data integrity test function.
        """
        art = self.bazaar.brokers[app.Article].cache[key]
        return art.name == row[0] and art.price == row[1]


    def checkOrderItem(self, key, row):
        """
        OrderItem class data integrity test function.
        """
        oi = self.bazaar.brokers[app.OrderItem].cache[key]
        return oi.order_fkey == row[0] and oi.pos == row[1] and oi.quantity == row[2]


    def getCache(self, cls):
        return self.bazaar.brokers[cls].cache
