# $Id: btest.py,v 1.5 2003/08/27 15:02:47 wrobell Exp $

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


    def checkOrder(self, row):
        """
        Order class data integrity test function.
        """
        order = self.bazaar.brokers[app.Order].cache[row[0]]
        return order.no == row[0] and order.finished == row[1]


    def checkEmployee(self, row):
        """
        Employee class data integrity test function.
        """
        emp = self.bazaar.brokers[app.Employee].cache[(row[0], row[1])]
        return emp.name == row[0] and emp.surname == row[1] and emp.phone == row[2]


    def checkArticle(self, row):
        """
        Article class data integrity test function.
        """
        art = self.bazaar.brokers[app.Article].cache[row[0]]
        return art.name == row[0] and art.price == row[1]


    def checkOrderItem(self, row):
        """
        OrderItem class data integrity test function.
        """
        oi = self.bazaar.brokers[app.OrderItem].cache[(row[0], row[1])]
        return oi.order == row[0] and oi.pos == row[1] and oi.quantity == row[2]
