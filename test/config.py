# $Id: config.py,v 1.4 2003/11/26 00:24:35 wrobell Exp $

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

        b = bazaar.core.Bazaar(self.cls_list)
        
        # save default conf
        oldconf = app.Article.relation, \
            app.Article.sequencer, \
            app.Article.cache, \
            app.Order.items.col.cache

        # set new configuration
        b.setConfig(bazaar.config.CPConfig(config))

        self.assertEqual(b.dsn, 'dbname = ord port = 5433')
        self.assertEqual(b.dbmod.__name__, 'psycopg')
        self.assertEqual(b.seqpattern, "select nextval('%s')")

        self.assertEqual(app.Article.relation, 'tarticle')
        self.assertEqual(app.Article.sequencer, 'tarticle_seq')

        self.assertEqual(app.Article.cache, bazaar.cache.LazyObject)
        self.assertEqual(b.brokers[app.Article].cache.__class__, bazaar.cache.LazyObject)

        self.assertEqual(app.Order.items.col.cache, bazaar.cache.LazyAssociation)

        # restore default conf to process in the rest of tests
        app.Article.relation, app.Article.sequencer, \
            app.Article.cache, app.Order.items.col.cache = oldconf
