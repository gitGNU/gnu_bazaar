# $Id: connection.py,v 1.2 2003/08/27 13:28:26 wrobell Exp $

import unittest
import logging

import bazaar.core

import app
import btest

"""
Test layer database connection management.
"""

log = logging.getLogger('bazaar.test.connection')

class ConnTestCase(btest.BazaarTestCase):
    """
    Test layer database connection managment.
    """
    def testConnection(self):
        """
        Test database connection initialization.
        """
        log.info('begin test of database connection initialization')

        self.bazaar.connectDB(app.dsn)

        self.assert_(self.bazaar.motor.db_conn and self.bazaar.motor.dbc, \
            'db connection is missing')
        
        # simple query
        self.bazaar.motor.dbc.execute('begin; rollback')

        log.info('finished test of database connection initialization')


    def testConnectionClosing(self):
        """
        Test database connection closing.
        """
        log.info('begin test of database connection closing')

        self.bazaar.connectDB(app.dsn)
        self.bazaar.closeDBConn()

        self.assert_(not (self.bazaar.motor.db_conn and self.bazaar.motor.dbc), \
            'db connection should not be set')
        
        log.info('finished test of database connection closing')
