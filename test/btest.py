# $Id: btest.py,v 1.2 2003/07/17 23:46:38 wrobell Exp $

import unittest

import bazaar.core

import app

class BazaarTestCase(unittest.TestCase):
    """
    <s>Test layer database connection managment.</s>

    <attr name = 'bazaar'>Bazaar layer object.</attr>
    """

    def setUp(self):
        """
        <s>Create Bazaar layer object.</s>
        """
        cls_list = (app.Order, app.Employee, app.Article, app.OrderItem)
        self.bazaar = bazaar.core.Bazaar(cls_list, app.db_module)
