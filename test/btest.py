# $Id: btest.py,v 1.4 2003/08/07 17:54:20 wrobell Exp $

import unittest

import bazaar.core

import app

class BazaarTestCase(unittest.TestCase):
    """
    <s>Base class for Bazaar layer tests.</s>

    <attr name = 'bazaar'>Bazaar layer object.</attr>
    <attr name = 'cls_list'>List of test application classes.</attr>
    """

    def setUp(self):
        """
        <s>Create Bazaar layer object.</s>
        """
        self.cls_list = (app.Order, app.Employee, app.Article, app.OrderItem)
        self.bazaar = bazaar.core.Bazaar(self.cls_list, app.db_module)


class DBBazaarTestCase(BazaarTestCase):
    """
    <s>Base class for Bazaar layer tests with enabled database connection.</s>
    """

    def setUp(self):
        """
        <s>Create Bazaar layer instance and connect with database.</s>
        """
        BazaarTestCase.setUp(self)
        self.bazaar.connectDB(app.dsn)


    def tearDown(self):
        """
        <s>Close database connection.</s>
        """
        self.bazaar.closeDBConn()


    def checkOrder(self, row):
        """
        <s>Order class data integrity test function.</s>
        """
        order = self.bazaar.brokers[app.Order].cache[row[0]]
        return order.no == row[0] and order.finished == row[1]


    def checkEmployee(self, row):
        """
        <s>Employee class data integrity test function.</s>
        """
        emp = self.bazaar.brokers[app.Employee].cache[(row[0], row[1])]
        return emp.name == row[0] and emp.surname == row[1] and emp.phone == row[2]


    def checkArticle(self, row):
        """
        <s>Article class data integrity test function.</s>
        """
        art = self.bazaar.brokers[app.Article].cache[row[0]]
        return art.name == row[0] and art.price == row[1]


    def checkOrderItem(self, row):
        """
        <s>OrderItem class data integrity test function.</s>
        """
        oi = self.bazaar.brokers[app.OrderItem].cache[(row[0], row[1])]
        return oi.order == row[0] and oi.pos == row[1] and oi.quantity == row[2]
