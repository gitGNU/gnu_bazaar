# $Id: btest.py,v 1.11 2003/09/29 18:36:53 wrobell Exp $

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
        self.cls_list = (app.Order, app.Employee, app.Article, app.OrderItem, app.Boss, app.Department)
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
            app.Boss: {
                'relation': 'boss',
                'cols'    : ('dep_key',),
                'test'    : self.checkBoss
            },
            app.Department: {
                'relation': 'department',
                'cols'    : ('boss_key',),
                'test'    : self.checkDepartment
            }
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


    def checkBoss(self, key, row):
        """
        Boss class data integrity test function.
        """
        boss = self.bazaar.brokers[app.Boss].cache[key]
        return boss.dep_key == row[0]


    def checkDepartment(self, key, row):
        """
        Department class data integrity test function.
        """
        dep = self.bazaar.brokers[app.Department].cache[key]
        return dep.boss_key == row[0]


    def getCache(self, cls):
        return self.bazaar.brokers[cls].cache


    def findObj(self, cls, data):
        attrs = tuple([attr for attr in data])
        for obj in self.bazaar.getObjects(cls):
            data_val = tuple([data[attr] for attr in attrs])
            obj_val = tuple([getattr(obj, attr) for attr in attrs])
            if obj_val == data_val:
                return obj
        return None



    def checkListAsc(self, cls, attr, query):
        mem_data = []
        for obj in self.bazaar.getObjects(cls):
            for val in getattr(obj, attr):
                self.assert_(val is not None, \
                    'referenced object cannot be None (application object key: %d)' % obj.__key__)
                mem_data.append((obj.__key__, val.__key__))
        mem_data.sort()

        dbc = self.bazaar.motor.db_conn.cursor()
        dbc.execute(query)
        db_data = dbc.fetchall()
        db_data.sort()
        self.assertEqual(db_data, mem_data, 'database data are different than memory data')
