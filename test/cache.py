# $Id: cache.py,v 1.2 2003/11/26 00:16:48 wrobell Exp $

import unittest
import gc
from ConfigParser import ConfigParser

import bazaar.core
import bazaar.config

import app
import btest

"""
Test object and association data cache.
"""

class LazyTestCase(btest.DBBazaarTestCase):
    """
    Test lazy cache.
    """
    def testObjectLoading(self):
        """Test object lazy cache"""
        config = ConfigParser()
        config.add_section('bazaar.cls')
        config.set('bazaar.cls', 'app.Article.cache', 'bazaar.cache.LazyObject')

        self.bazaar.setConfig(bazaar.config.CPConfig(config))
        self.bazaar.connectDB()

        articles = []
        abroker = self.bazaar.brokers[app.Article]
        for i in range(1, 4):
            articles.append(abroker.get(i))

        keys = [art.__key__ for art in articles]
        self.assertEqual(len(keys), len(abroker.cache))

        for art in articles:
            self.assert_(art.__key__ in abroker.cache)
            self.assertEqual(art, abroker.get(art.__key__))

        # remove all strong references...
        del articles
        del art
        gc.collect()
        # ... now cache should be empty
        self.assertEqual(len(abroker.cache), 0)



class FullTestCase(btest.DBBazaarTestCase):
    """
    Test full cache.
    """
    def testObjectLoading(self):
        """Test object full cache"""
        # get one object...
        abroker = self.bazaar.brokers[app.Article]
        abroker.get(1)

        # ... and check if all are loaded
        self.checkObjects(app.Article, len(abroker.cache))


    def testAscLoading(self):
        """Test association full cache"""
        order = self.bazaar.getObjects(app.Order)[0]
        self.checkOrdAsc()
