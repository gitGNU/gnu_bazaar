# $Id: assoc.py,v 1.23 2004/01/21 23:06:28 wrobell Exp $

import app
import btest

import bazaar.exc

class OneToOneAssociationTestCase(btest.DBBazaarTestCase):
    """
    Test one-to-one associations.
    """

    def testLoading(self):
        """Test one-to-one association loading"""
        for boss in self.bazaar.getObjects(app.Boss):
            self.assertEqual(boss.dep_fkey, boss.department.__key__, 'one-to-one association data mismatch')
            self.assertEqual(boss.department, \
                self.getCache(app.Department)[boss.dep_fkey], \
                'one-to-one association data mismatch')

        for dep in self.bazaar.getObjects(app.Department):
            self.assertEqual(dep.boss_fkey, dep.boss.__key__, 'one-to-one association data mismatch')
            self.assertEqual(dep.boss, \
                self.getCache(app.Boss)[dep.boss_fkey], \
                'one-to-one association data mismatch')


    def testUpdating(self):
        """Test one-to-one association updating"""
        self.bazaar.getObjects(app.Boss)
        self.bazaar.getObjects(app.Department)
        b1 = self.getCache(app.Boss)[1001]
        b2 = self.getCache(app.Boss)[1002]
        d1 = self.getCache(app.Department)[1001]
        d2 = self.getCache(app.Department)[1002]
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



class ManyToManyAssociationTestCase(btest.DBBazaarTestCase):
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
        for emp in self.bazaar.getObjects(app.Employee):
            if len(emp.orders) > 0:
                break

        assert len(emp.orders) > 0

        for o in emp.orders:
            del emp.orders[o]

        assert len(emp.orders) == 0

        # reload data and check if they are reloaded
        app.Employee.orders.reloadData()
        self.checkEmpAsc()


    def testAppending(self):
        """Test appending objects to many-to-many association
        """
        emp = self.bazaar.getObjects(app.Employee)[0]

        ord1 = app.Order()
        ord1.no = 1002
        ord1.finished = False

        ord2 = app.Order()
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
        ord1 = app.Order()
        ord1.no = 1002
        ord1.finished = False
        emp.orders.append(ord1)
        self.assertRaises(app.dbmod.ProgrammingError, emp.orders.update)
        self.bazaar.rollback()

        self.assertRaises(bazaar.exc.AssociationError, emp.orders.append, None)
        self.assertRaises(bazaar.exc.AssociationError, emp.orders.append, object())
        self.assertRaises(bazaar.exc.AssociationError, emp.orders.append, ord1)


    def testRemoving(self):
        """Test removing objects from many-to-many association
        """
        for emp in self.bazaar.getObjects(app.Employee):
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
        ord1 = app.Order()
        ord1.no = 1002
        ord1.finished = False

        ord2 = app.Order()
        ord2.no = 1003
        ord2.finished = False

        # first, get order object to remove, this way we are sure that we
        # will not remove object appended as ord1
        for emp in self.bazaar.getObjects(app.Employee):
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



class OneToManyAssociationTestCase(btest.DBBazaarTestCase):
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
        for ord in self.bazaar.getObjects(app.Order):
            if len(ord.items) > 0:
                break

        # remove all of referenced objects
        assert len(ord.items) > 0
        for oi in ord.items:
            del ord.items[oi]
        assert len(ord.items) == 0

        # reload data and check if they are reloaded
        app.Order.items.reloadData()
        self.checkOrdAsc()


    def testAppending(self):
        """Test appending objects to one-to-many association
        """
        ord = self.bazaar.getObjects(app.Order)[0]
        art = self.bazaar.getObjects(app.Article)[0]

        oi1 = app.OrderItem()
        oi1.pos = 1000
        oi1.quantity = 10.3
        oi1.article = art

        oi2 = app.OrderItem()
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

        oi3 = app.OrderItem()
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
        for ord in self.bazaar.getObjects(app.Order):
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

        ord = app.Order()
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
        for ord in self.bazaar.getObjects(app.Order):
            if len(ord.items) > 0:
                break

        art = self.bazaar.getObjects(app.Article)[0]

        oi1 = app.OrderItem()
        oi1.pos = 1000
        oi1.quantity = 10.3
        oi1.article = art

        oi2 = app.OrderItem()
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
        ord = self.bazaar.find(app.Order, {'__key__': 1000}).next()

        art = self.bazaar.getObjects(app.Article)[0]

        oi1 = app.OrderItem()
        oi1.pos = 1000
        oi1.quantity = 10.3
        oi1.article = art

        oi2 = app.OrderItem()
        oi2.pos = 1001
        oi2.quantity = 10.4
        oi2.article = art

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
