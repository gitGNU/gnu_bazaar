# $Id: connection.py,v 1.5 2003/11/23 23:39:18 wrobell Exp $

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
        self.assert_(self.bazaar.motor.conn, 'db connection is missing')
        # simple query
        self.bazaar.motor.conn.cursor().execute('begin; rollback')


    def testConnectionClosing(self):
        """Test database connection closing"""

        self.bazaar.connectDB(app.dsn)
        self.bazaar.closeDBConn()

        self.assert_(not self.bazaar.motor.conn, 'db connection should not be set')
