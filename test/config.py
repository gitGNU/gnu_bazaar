# $Id: config.py,v 1.1 2003/11/23 20:33:00 wrobell Exp $

from ConfigParser import ConfigParser

import unittest

import bazaar.core
import bazaar.config

import app
import btest

"""
Test mapping application classes to database relations.
"""

class ConfigTestCase(btest.BazaarTestCase):
    """
    Test Bazaar reconfiguration.
    """

    def testConfig(self):
        """Test Bazaar reconfiguration"""
        config = ConfigParser()
        config.read('bazaar.ini')
#        config.add_section('bazaar')
#        config.set('bazaar', 'dsn', app.dsn)
#        config.set('bazaar', 'module', app.db_module)

        b = bazaar.core.Bazaar(self.cls_list)
        
        b.setConfig(bazaar.config.CPConfig(config))

        self.assertEqual(b.dsn, 'dbname = ord port = 5433')
        self.assertEqual(b.db_module.__name__, 'psycopg')
        self.assertEqual(b.seqpattern, "select nextval('%s')")

#fixme        self.assertEqual(app.Article.cache, bazaar.cache.LoadObject)
        self.assertEqual(app.Article.relation, 'tarticle')
        self.assertEqual(app.Article.sequencer, 'tarticle_seq')
