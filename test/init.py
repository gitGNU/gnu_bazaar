# $Id: init.py,v 1.4 2003/08/27 15:22:38 wrobell Exp $

import unittest

import bazaar.core
import bazaar.motor

import btest
import app

"""
Test layer initialization.
"""

class InitTestCase(unittest.TestCase):
    """
    Test layer initialization.
    """

    def testBazaarInit(self):
        """Test layer initialization"""


        cls_list = (app.Order, app.Employee, app.Article, app.OrderItem)

        b = bazaar.core.Bazaar(cls_list, app.db_module)

        self.assertNotEqual(b.motor, None, 'Motor object does not exist')
        self.assert_(isinstance(b.motor, bazaar.motor.Motor), 'Motor object class mismatch')

        for cls in cls_list:
            self.assert_(cls in b.brokers, 'class "%s" not found in broker list' % cls)
            self.assertEqual(cls, b.brokers[cls].cls, 'broker class mismatch')

        # there should be no connection, now
        self.assert_(not b.motor.db_conn, 'there should be no db connection')


    def testConnection(self):
        """Test layer initialization and database connection"""


        cls_list = (app.Order, app.Employee, app.Article, app.OrderItem)

        # init bazaar layer with connection
        b = bazaar.core.Bazaar(cls_list, app.db_module, app.dsn)
        self.assert_(b.motor.db_conn and b.motor.dbc, 'db connection is missing')
        
        # simple query
        b.motor.dbc.execute('begin; rollback')
