# $Id: btest.py,v 1.3 2003/07/19 10:04:13 wrobell Exp $

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
