# $Id: config.py,v 1.5 2004/01/22 23:21:41 wrobell Exp $
#
# Bazaar - an easy to use and powerful abstraction layer between relational
# database and object oriented application.
#
# Copyright (C) 2000-2004 by Artur Wroblewski <wrobell@pld-linux.org>
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

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
