# $Id: cache.py,v 1.1 2004/05/21 18:12:39 wrobell Exp $
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

import gc
from ConfigParser import ConfigParser

import bazaar.core
import bazaar.config

import bazaar.test.bzr
import bazaar.test.app

"""
Test object and association data cache.
"""

class LazyTestCase(bazaar.test.TestCase):
    """
    Test lazy cache.
    """
    def testObjectLoading(self):
        """Test object lazy cache"""
        self.config.add_section('bazaar.cls')
        self.config.set('bazaar.cls', 'bazaar.test.app.Article.cache', 'bazaar.cache.LazyObject')

        self.bazaar.setConfig(bazaar.config.CPConfig(self.config))
        self.bazaar.connectDB()
        self.config.remove_section('bazaar.cls')

        articles = []
        abroker = self.bazaar.brokers[bazaar.test.app.Article]
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


    def testAscLoading(self):
        """Test association data lazy cache"""
#        config.add_section('bazaar.cls')
#        config.set('bazaar.cls', 'bazaar.test.app.Order.cache', 'bazaar.cache.LazyObject')
        self.config.add_section('bazaar.asc')
        self.config.set('bazaar.asc', 'bazaar.test.app.Order.items.cache', \
            'bazaar.cache.LazyAssociation')
        self.config.set('bazaar.asc', 'bazaar.test.app.Employee.orders.cache', \
            'bazaar.cache.LazyAssociation')

        self.bazaar.setConfig(bazaar.config.CPConfig(self.config))
        self.bazaar.connectDB()
        self.config.remove_section('bazaar.asc')

        order = self.bazaar.getObjects(bazaar.test.app.Order)[0]
        oikeys = [oi.__key__ for oi in order.items]
        oikeys.sort()

        dbc = self.bazaar.motor.conn.cursor()
        dbc.execute('select __key__ from "order_item" where order_fkey = %s', [order.__key__])
        dbkeys = [row[0] for row in dbc.fetchall()]
        dbkeys.sort()

        self.assertEqual(oikeys, dbkeys)

        art = self.bazaar.getObjects(bazaar.test.app.Article)[0]
                                                                                                                               
        oi1 = bazaar.test.app.OrderItem()
        oi1.pos = 1000
        oi1.quantity = 10.3
        oi1.article = art
                                                                                                                               
        oi2 = bazaar.test.app.OrderItem()
        oi2.pos = 1001
        oi2.quantity = 10.4
        oi2.article = art

        order.items.append(oi1)
        order.items.append(oi2)

        self.bazaar.reloadObjects(bazaar.test.app.Order)
        del order
        gc.collect()
        self.assertEqual(len(bazaar.test.app.Order.items.ref_buf), 0)
        self.assertEqual(len(bazaar.test.app.Order.items.cache), 0)


        emp = self.bazaar.getObjects(bazaar.test.app.Employee)[0]
        ordkeys = [ord.__key__ for ord in emp.orders]
        ordkeys.sort()

        dbc = self.bazaar.motor.conn.cursor()
        dbc.execute('select "order" from "employee_orders" where employee = %s', [emp.__key__])
        dbkeys = [row[0] for row in dbc.fetchall()]
        dbkeys.sort()

        self.assertEqual(ordkeys, dbkeys)

        art = self.bazaar.getObjects(bazaar.test.app.Article)[0]
                                                                                                                               
        ord1 = bazaar.test.app.Order()
        ord1.no = 1000
        ord1.finished = False
                                                                                                                               
        ord2 = bazaar.test.app.Order()
        ord1.no = 1001
        ord1.finished = True

        emp.orders.append(ord1)
        emp.orders.append(ord2)

        self.bazaar.reloadObjects(bazaar.test.app.Employee)
        del emp
        gc.collect()
        self.assertEqual(len(bazaar.test.app.Employee.orders.ref_buf), 0)
        self.assertEqual(len(bazaar.test.app.Employee.orders.cache), 0)
            


class FullTestCase(bazaar.test.bzr.TestCase):
    """
    Test full cache.
    """
    def testObjectLoading(self):
        """Test object full cache"""
        # get one object...
        abroker = self.bazaar.brokers[bazaar.test.app.Article]
        abroker.get(1)

        # ... and check if all are loaded
        self.checkObjects(bazaar.test.app.Article, len(abroker.cache))


    def testAscLoading(self):
        """Test association full cache"""
        order = self.bazaar.getObjects(bazaar.test.app.Order)[0]
        self.checkOrdAsc()



if __name__ == '__main__':
    bazaar.test.main()
