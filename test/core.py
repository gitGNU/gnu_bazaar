# $Id: core.py,v 1.2 2003/07/17 23:46:38 wrobell Exp $

import unittest
import logging

import bazaar.core

import app
import btest

"""
<s>Test object loading and reloading from database.</s>
"""

class ObjectLoadTestCase(btest.BazaarTestCase):
    """
    """
    def setUp(self):
        btest.BazaarTestCase.setUp(self)
        self.bazaar.connectDB(app.dsn)


    def testObjectLoading(self):
        self.bazaar.getObjects(app.Order)
