# $Id: config.py,v 1.1 2004/05/21 18:12:39 wrobell Exp $
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

import bazaar.core
import bazaar.config
import bazaar.cache

import bazaar.test
import bazaar.test.app
import bazaar.test.bzr

"""
Test mapping application classes to database relations.
"""

class ConfigTestCase(bazaar.test.TestCase):
    """
    Test Bazaar reconfiguration.
    """

    def testConfig(self):
        """Test Bazaar reconfiguration"""
        config = ConfigParser()
        config.add_section('bazaar')
        config.set('bazaar', 'module', 'psycopg')
        config.set('bazaar', 'dsn', 'dbname = ord port = 5433')
        config.set('bazaar', 'seqpattern', 'select nextval(\'%s\')')
        
        config.add_section('bazaar.cls')
        config.set('bazaar.cls', 'bazaar.test.app.Article.relation', 'tarticle')
        config.set('bazaar.cls', 'bazaar.test.app.Article.sequencer', 'tarticle_seq')
        config.set('bazaar.cls', 'bazaar.test.app.Article.cache', 'bazaar.cache.LazyObject')
        
        config.add_section('bazaar.asc')
        config.set('bazaar.asc', 'bazaar.test.app.Order.items.cache', 'bazaar.cache.LazyAssociation')
    
        b = bazaar.core.Bazaar(self.cls_list)
        
        # save default conf
        oldconf = bazaar.test.app.Article.relation, \
            bazaar.test.app.Article.sequencer, \
            bazaar.test.app.Article.cache, \
            bazaar.test.app.Order.items.col.cache

        # set new configuration
        b.setConfig(bazaar.config.CPConfig(config))

        self.assertEqual(b.dsn, 'dbname = ord port = 5433')
        self.assertEqual(b.dbmod.__name__, 'psycopg')
        self.assertEqual(b.seqpattern, "select nextval('%s')")

        self.assertEqual(bazaar.test.app.Article.relation, 'tarticle')
        self.assertEqual(bazaar.test.app.Article.sequencer, 'tarticle_seq')

        self.assertEqual(bazaar.test.app.Article.cache, bazaar.cache.LazyObject)
        self.assertEqual(b.brokers[bazaar.test.app.Article].cache.__class__, bazaar.cache.LazyObject)

        self.assertEqual(bazaar.test.app.Order.items.col.cache, bazaar.cache.LazyAssociation)

        # restore default conf to process in the rest of tests
        bazaar.test.app.Article.relation, bazaar.test.app.Article.sequencer, \
            bazaar.test.app.Article.cache, bazaar.test.app.Order.items.col.cache = oldconf



if __name__ == '__main__':
    bazaar.test.main()
