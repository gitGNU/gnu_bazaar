# $Id: init.py,v 1.1 2003/07/10 23:10:30 wrobell Exp $

import unittest
import logging

import bazaar.core
import bazaar.motor

import app

"""
<s>Test layer initialization.</s>
"""

log = logging.getLogger('bazaar.test.connection')

class InitTestCase(unittest.TestCase):
    """
    <s>Test layer initialization.</s>
    """

    def testBazaarInit(self):
        """
        <s>Test layer initialization.</s>
        """
        log.info('begin test of Bazaar layer initialization')

        cls_list = (app.Person, app.Address)

        b = bazaar.core.Bazaar(cls_list, app.db_module)

        self.assertNotEqual(b.motor, None, 'Motor object does not exist')
        self.assert_(isinstance(b.motor, bazaar.motor.Motor), 'Motor object class mismatch')

        for cls in cls_list:
            self.assert_(cls in b.brokers, 'class "%s" not found in broker list' % cls)
            self.assertEqual(cls, b.brokers[cls].cls, 'broker class mismatch')

        # there should be no connection, now
        self.assert_(not b.motor.db_conn, 'there should be no db connection')

        log.info('finished test of Bazaar layer initialization')


    def testConnection(self):
        """
        <s>Test layer initialization and database connection.</s>
        """
        log.info('begin test of Bazaar layer initialization with connection')

        cls_list = (app.Person, app.Address)

        # init bazaar layer with connection
        b = bazaar.core.Bazaar(cls_list, app.db_module, app.dsn)
        self.assert_(b.motor.db_conn and b.motor.dbc, 'db connection is missing')
        
        # simple query
        b.motor.dbc.execute('begin; rollback')

        log.info('finished test of Bazaar layer initialization with connection')
