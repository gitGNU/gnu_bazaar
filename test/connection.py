# $Id: connection.py,v 1.1 2003/07/10 23:06:07 wrobell Exp $

import unittest
import logging

import bazaar.core

import app
import btest

"""
<s>Test layer database connection management.</s>
"""

log = logging.getLogger('bazaar.test.connection')

class ConnTestCase(btest.BazaarTestCase):
    """
    <s>Test layer database connection managment.</s>
    """
    def testConnection(self):
        """
        <s>Test database connection initialization.</s>
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
        <s>Test database connection closing.</s>
        """
        log.info('begin test of database connection closing')

        self.bazaar.connectDB(app.dsn)
        self.bazaar.closeDBConn()

        self.assert_(not (self.bazaar.motor.db_conn and self.bazaar.motor.dbc), \
            'db connection should not be set')
        
        log.info('finished test of database connection closing')
