# $Id: connection.py,v 1.3 2003/08/27 15:22:38 wrobell Exp $

import unittest

import bazaar.core

import app
import btest

"""
Test layer database connection management.
"""

class ConnTestCase(btest.BazaarTestCase):
    """
    Test layer database connection managment.
    """
    def testConnection(self):
        """Test database connection initialization"""


        self.bazaar.connectDB(app.dsn)

        self.assert_(self.bazaar.motor.db_conn and self.bazaar.motor.dbc, \
            'db connection is missing')
        
        # simple query
        self.bazaar.motor.dbc.execute('begin; rollback')


    def testConnectionClosing(self):
        """Test database connection closing"""


        self.bazaar.connectDB(app.dsn)
        self.bazaar.closeDBConn()

        self.assert_(not (self.bazaar.motor.db_conn and self.bazaar.motor.dbc), \
            'db connection should not be set')
