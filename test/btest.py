# $Id: btest.py,v 1.1 2003/07/10 23:04:23 wrobell Exp $

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
        cls_list = (app.Person, app.Address)
        self.bazaar = bazaar.core.Bazaar(cls_list, app.db_module)
