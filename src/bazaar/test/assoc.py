# $Id: assoc.py,v 1.1 2004/05/21 18:12:38 wrobell Exp $
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

import bazaar.test.app
import bazaar.test.bzr

import bazaar.exc

class OneToOneAssociationTestCase(bazaar.test.bzr.TestCase):
    """
    Test one-to-one associations.
    """

    def testLoading(self):
        """Test one-to-one association loading"""
        for boss in self.bazaar.getObjects(bazaar.test.app.Boss):
            self.assertEqual(boss.dep_fkey, boss.department.__key__, 'one-to-one association data mismatch')
            self.assertEqual(boss.department, \
                self.getCache(bazaar.test.app.Department)[boss.dep_fkey], \
                'one-to-one association data mismatch')

        for dep in self.bazaar.getObjects(bazaar.test.app.Department):
            self.assertEqual(dep.boss_fkey, dep.boss.__key__, 'one-to-one association data mismatch')
            self.assertEqual(dep.boss, \
                self.getCache(bazaar.test.app.Boss)[dep.boss_fkey], \
                'one-to-one association data mismatch')


    def testUpdating(self):
        """Test one-to-one association updating"""
        self.bazaar.getObjects(bazaar.test.app.Boss)
        self.bazaar.getObjects(bazaar.test.app.Department)
        b1 = self.getCache(bazaar.test.app.Boss)[1001]
        b2 = self.getCache(bazaar.test.app.Boss)[1002]
        d1 = self.getCache(bazaar.test.app.Department)[1001]
        d2 = self.getCache(bazaar.test.app.Department)[1002]
        self.assertEqual(b1.department, d1, 'one-to-one associations data mismatch')
        self.assertEqual(d1.boss, b1, 'one-to-one associations data mismatch')
        self.assertEqual(b2.department, d2, 'one-to-one associations data mismatch')
        self.assertEqual(d2.boss, b2, 'one-to-one associations data mismatch')

        b1.department = d2
        self.assertEqual(b1.department, d2, 'one-to-one associations data mismatch')
        self.assertEqual(d2.boss, b1, 'one-to-one associations data mismatch')
        self.assertEqual(d2.boss_fkey, b1.__key__, 'one-to-one association data mismatch')
        self.assertEqual(b1.dep_fkey, d2.__key__, 'one-to-one association data mismatch')

        d1.boss = b2
        self.assertEqual(b2.department, d1, 'one-to-one associations data mismatch')
        self.assertEqual(d1.boss, b2, 'one-to-one associations data mismatch')
        self.assertEqual(d1.boss_fkey, b2.__key__, 'one-to-one association data mismatch')
        self.assertEqual(b2.dep_fkey, d1.__key__, 'one-to-one association data mismatch')

        d1.boss = None
        self.assertEqual(d1.boss, None, 'one-to-one associations data mismatch')
        self.assertEqual(d1.boss_fkey, None, 'one-to-one associations data mismatch')
        self.assertEqual(b2.department, None, 'one-to-one associations data mismatch')
        self.assertEqual(b2.dep_fkey, None, 'one-to-one associations data mismatch')



class ManyToManyAssociationTestCase(bazaar.test.bzr.TestCase):
    """
    Test many-to-many associations.
    """
    def testLoading(self):
        """Test many-to-many association loading
        """
        self.checkEmpAsc()


    def testReloading(self):
        """Test many-to-many association loading
        """
        for emp in self.bazaar.getObjects(bazaar.test.app.Employee):
            if len(emp.orders) > 0:
                break

        assert len(emp.orders) > 0

        for o in emp.orders:
            del emp.orders[o]

        assert len(emp.orders) == 0

        # reload data and check if they are reloaded
        bazaar.test.app.Employee.orders.reloadData()
        self.checkEmpAsc()


    def testAppending(self):
        """Test appending objects to many-to-many association
        """
        emp = self.bazaar.getObjects(bazaar.test.app.Employee)[0]

        ord1 = bazaar.test.app.Order()
        ord1.no = 1002
        ord1.finished = False

        ord2 = bazaar.test.app.Order()
        ord2.no = 1003
        ord2.finished = False

        # append object with _defined_ primary key value
        self.bazaar.add(ord1)
        emp.orders.append(ord1)

        # append object with _undefined_ primary key value
        emp.orders.append(ord2)
        self.bazaar.add(ord2)
        self.assert_(ord1 in emp.orders, \
            'appended referenced object not found in association %s -> %s' % \
            (emp, ord1))
        self.assert_(ord2 in emp.orders, \
            'appended referenced object not found in association %s -> %s' % \
            (emp, ord2))
        emp.orders.update()
        self.checkEmpAsc()

        # append object with undefined primary key value
        ord1 = bazaar.test.app.Order()
        ord1.no = 1002
        ord1.finished = False
        emp.orders.append(ord1)
        self.assertRaises(self.bazaar.dbmod.IntegrityError, emp.orders.update)
        self.bazaar.rollback()

        self.assertRaises(bazaar.exc.AssociationError, emp.orders.append, None)
        self.assertRaises(bazaar.exc.AssociationError, emp.orders.append, object())
        self.assertRaises(bazaar.exc.AssociationError, emp.orders.append, ord1)


    def testRemoving(self):
        """Test removing objects from many-to-many association
        """
        for emp in self.bazaar.getObjects(bazaar.test.app.Employee):
            if len(emp.orders) > 0:
                break

        assert len(emp.orders) > 0

        orders = list(emp.orders)
        ord = orders[0]
        del emp.orders[ord]
        self.assert_(ord not in emp.orders, \
            'removed referenced object found in association')
        emp.orders.update()
        self.checkEmpAsc()
        self.assertRaises(bazaar.exc.AssociationError, emp.orders.remove, None)
        self.assertRaises(bazaar.exc.AssociationError, emp.orders.remove, object())
        self.assertRaises(bazaar.exc.AssociationError, emp.orders.remove, ord)


    def testMixedUpdate(self):
        """Test appending and removing objects to/from many-to-many association
        """
        ord1 = bazaar.test.app.Order()
        ord1.no = 1002
        ord1.finished = False

        ord2 = bazaar.test.app.Order()
        ord2.no = 1003
        ord2.finished = False

        # first, get order object to remove, this way we are sure that we
        # will not remove object appended as ord1
        for emp in self.bazaar.getObjects(bazaar.test.app.Employee):
            if len(emp.orders) > 0:
                break
        orders = list(emp.orders)
        ord = orders[0]

        # append object with _defined_ primary key value
        self.bazaar.add(ord1)
        emp.orders.append(ord1)

        # fixme: improve test code, so assertion below is not required
        assert ord != ord2 != ord1

        del emp.orders[ord]

        # append object with _undefined_ primary key value
        emp.orders.append(ord2)
        self.bazaar.add(ord2)

        self.assert_(ord not in emp.orders, \
            'removed referenced object found in association')
        self.assert_(ord1 in emp.orders, \
            'appended referenced object not found in association')
        self.assert_(ord2 in emp.orders, \
            'appended referenced object not found in association')

        emp.orders.update()

        self.assert_(ord not in emp.orders, \
            'removed referenced object found in association')

        self.assert_(ord1 in emp.orders, \
            'appended referenced object not found in association')
        self.assert_(ord2 in emp.orders, \
            'appended referenced object not found in association')

        self.checkEmpAsc()

        emp.orders.append(ord)
        emp.orders.remove(ord1)
        emp.orders.remove(ord2)

        self.assert_(ord in emp.orders, \
            'appended referenced object not found in association')
        self.assert_(ord1 not in emp.orders, \
            'removed referenced object found in association')
        self.assert_(ord2 not in emp.orders, \
            'removed referenced object found in association')

        emp.orders.update()

        self.assert_(ord in emp.orders, \
            'appended referenced object not found in association')
        self.assert_(ord1 not in emp.orders, \
            'removed referenced object found in association')
        self.assert_(ord2 not in emp.orders, \
            'removed referenced object found in association')

        self.checkEmpAsc()



class OneToManyAssociationTestCase(bazaar.test.bzr.TestCase):
    """
    Test one-to-many associations.
    """
    def testLoading(self):
        """Test one-to-many association loading
        """
        self.checkOrdAsc()


    def testReloading(self):
        """Test one-to-many association loading
        """
        # find order with amount of items greater than zero, so it is
        # possible to remove a item
        for ord in self.bazaar.getObjects(bazaar.test.app.Order):
            if len(ord.items) > 0:
                break

        # remove all of referenced objects
        assert len(ord.items) > 0
        for oi in ord.items:
            del ord.items[oi]
        assert len(ord.items) == 0

        # reload data and check if they are reloaded
        bazaar.test.app.Order.items.reloadData()
        self.checkOrdAsc()


    def testAppending(self):
        """Test appending objects to one-to-many association
        """
        ord = self.bazaar.getObjects(bazaar.test.app.Order)[0]
        art = self.bazaar.getObjects(bazaar.test.app.Article)[0]

        oi1 = bazaar.test.app.OrderItem()
        oi1.pos = 1000
        oi1.quantity = 10.3
        oi1.article = art

        oi2 = bazaar.test.app.OrderItem()
        oi2.pos = 1001
        oi2.quantity = 10.4
        oi2.article = art

        # append object with _defined_ primary key value
        self.bazaar.add(oi1)
        ord.items.append(oi1)

        # append object with _undefined_ primary key value
        ord.items.append(oi2)
        self.bazaar.add(oi2)
        self.assert_(oi1 in ord.items, \
            'appended referenced object not found in association %s -> %s' % \
            (ord, oi1))
        self.assert_(oi2 in ord.items, \
            'appended referenced object not found in association %s -> %s' % \
            (ord, oi2))
        ord.items.update()
        self.checkOrdAsc()

        oi3 = bazaar.test.app.OrderItem()
        oi3.pos = 1005
        oi3.quantity = 10.4
        oi3.article = art
        oi3.order = ord
        self.assert_(oi3 in ord.items, \
            'appended referenced object not found in association %s -> %s' % \
            (ord, oi3))
        self.bazaar.add(oi3)
        ord.items.update()
        self.checkOrdAsc()

        self.assertRaises(bazaar.exc.AssociationError, ord.items.append, None)
        self.assertRaises(bazaar.exc.AssociationError, ord.items.append, object())
        self.assertRaises(bazaar.exc.AssociationError, ord.items.append, oi1)


    def testRemoving(self):
        """Test removing objects from one-to-many association
        """
        # find order with amount of items greater than zero, so it is
        # possible to remove a item
        for ord in self.bazaar.getObjects(bazaar.test.app.Order):
            if len(ord.items) > 0:
                break
        assert len(ord.items) > 0
        items = list(ord.items)
        oi = items[0]
        del ord.items[oi]
        self.assert_(oi not in ord.items, \
            'removed referenced object found in association')
        ord.items.update()
        self.checkOrdAsc()

        oi = items[1]
        oi.order = None
        self.assert_(oi not in ord.items, \
            'removed referenced object found in association')
        ord.items.update()
        self.checkOrdAsc()

        ord = bazaar.test.app.Order()
        ord.items.append(oi)
        del ord.items[oi]

        self.assertRaises(bazaar.exc.AssociationError, ord.items.remove, None)
        self.assertRaises(bazaar.exc.AssociationError, ord.items.remove, object())
        self.assertRaises(bazaar.exc.AssociationError, ord.items.remove, oi)


    def testMixedUpdate(self):
        """Test appending and removing objects to/from one-to-many association
        """
        # find order with amount of items greater than zero, so it is
        # possible to remove a item
        for ord in self.bazaar.getObjects(bazaar.test.app.Order):
            if len(ord.items) > 0:
                break

        art = self.bazaar.getObjects(bazaar.test.app.Article)[0]

        oi1 = bazaar.test.app.OrderItem()
        oi1.pos = 1000
        oi1.quantity = 10.3
        oi1.article = art

        oi2 = bazaar.test.app.OrderItem()
        oi2.pos = 1001
        oi2.quantity = 10.4
        oi2.article = art

        # first, get order item object to remove, this way we are sure that we
        # will not remove object appended as oi1
        assert len(ord.items) > 0, 'order key %d' % ord.__key__
        items = list(ord.items)
        oi = items[0]

        # append object with _defined_ primary key value
        self.bazaar.add(oi1)
        ord.items.append(oi1)

        # fixme: improve test code, so assertion below is not required
        assert oi != oi2 != oi1

        del ord.items[oi]

        # append object with _undefined_ primary key value
        ord.items.append(oi2)
        self.bazaar.add(oi2)

        self.assert_(oi not in ord.items, \
            'removed referenced object found in association')
        self.assert_(oi1 in ord.items, \
            'appended referenced object not found in association')
        self.assert_(oi2 in ord.items, \
            'appended referenced object not found in association')

        ord.items.update()

        self.assert_(oi not in ord.items, \
            'removed referenced object found in association')

        self.assert_(oi1 in ord.items, \
            'appended referenced object not found in association')
        self.assert_(oi2 in ord.items, \
            'appended referenced object not found in association')

        self.checkOrdAsc()

        ord.items.append(oi)
        ord.items.remove(oi1)
        ord.items.remove(oi2)

        self.assert_(oi in ord.items, \
            'appended referenced object not found in association')
        self.assert_(oi1 not in ord.items, \
            'removed referenced object found in association')
        self.assert_(oi2 not in ord.items, \
            'removed referenced object found in association')

        ord.items.update()

        self.assert_(oi in ord.items, \
            'appended referenced object not found in association')
        self.assert_(oi1 not in ord.items, \
            'removed referenced object found in association')
        self.assert_(oi2 not in ord.items, \
            'removed referenced object found in association')

        self.checkOrdAsc()


    def testEmptyList(self):
        """Test empty list of referenced objects (1-n)
        """
        # find order with amount of items equal to zero
        ord = self.bazaar.find(bazaar.test.app.Order, {'__key__': 1000}).next()

        self.assertEqual(len(ord.items), 0)

        art = self.bazaar.getObjects(bazaar.test.app.Article)[0]

        oi1 = bazaar.test.app.OrderItem()
        oi1.pos = 1000
        oi1.quantity = 10.3
        oi1.article = art

        oi2 = bazaar.test.app.OrderItem()
        oi2.pos = 1001
        oi2.quantity = 10.4
        oi2.article = art

        # fixme: create a test similar to this but without two lines below
        # fixme: the test will fail but ord.items.update (?) should throw
        # fixme: an exception about objects not added into database...
        self.bazaar.add(oi1)
        self.bazaar.add(oi2)

        ord.items.append(oi1)
        ord.items.append(oi2)
        ord.items.remove(oi1)
        ord.items.remove(oi2)

        ord.items.update()
        self.checkOrdAsc()

        ord.items.append(oi1)
        ord.items.append(oi2)

        ord.items.update()
        self.checkOrdAsc()

        # remove added data into the database - clean up the test 
        ord.items.remove(oi1)
        ord.items.remove(oi2)
        ord.items.update()
        self.checkOrdAsc()


if __name__ == '__main__':
    bazaar.test.main()
