# $Id: config.py,v 1.3 2003/11/24 18:42:22 wrobell Exp $

from ConfigParser import ConfigParser

import unittest

import bazaar.core
import bazaar.config
import bazaar.cache

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
#        config.set('bazaar', 'module', app.dbmod)

        b = bazaar.core.Bazaar(self.cls_list)
        
        b.setConfig(bazaar.config.CPConfig(config))

        self.assertEqual(b.dsn, 'dbname = ord port = 5433')
        self.assertEqual(b.dbmod.__name__, 'psycopg')
        self.assertEqual(b.seqpattern, "select nextval('%s')")

        self.assertEqual(app.Article.relation, 'tarticle')
        self.assertEqual(app.Article.sequencer, 'tarticle_seq')

        self.assertEqual(app.Article.cache, bazaar.cache.LazyObject)
        self.assertEqual(b.brokers[app.Article].cache.__class__, bazaar.cache.LazyObject)

        self.assertEqual(app.Order.items.col.cache, bazaar.cache.LazyAssociation)
