# $Id: core.py,v 1.1 2003/07/10 23:11:12 wrobell Exp $

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
        self.bazaar.getObjects(app.Person)
