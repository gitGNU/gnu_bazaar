# $Id: assoc.py,v 1.10 2003/09/29 11:36:42 wrobell Exp $

import app
import btest

import bazaar.exc

class OneToOneAssociationTestCase(btest.DBBazaarTestCase):
    """
    Test one-to-one associations.
    """

    def testLoading(self):
        """Test one-to-one association loading"""

        self.bazaar.getObjects(app.OrderItem)
        dbc = self.bazaar.motor.db_conn.cursor()
        dbc.execute('select __key__, "order_fkey", pos, article_fkey from order_item')
        row = dbc.fetchone()
        while row:
            order_item = self.bazaar.brokers[app.OrderItem].cache[row[0]]

            # check the value of foreign key
            self.assertEqual(order_item.article_fkey, row[3], \
                'article foreign key mismatch "%s" != "%s"' % (order_item.article_fkey, row[3]))

            # check the value of associated object's primary key
            self.assertEqual(order_item.article.__key__, row[3], \
                'article primary key mismatch "%s" != "%s"' % (order_item.article.__key__, row[3]))

            row = dbc.fetchone()


    def testUpdating(self):
        """Test one-to-one association updating"""
        pass



class ManyToManyAssociationTestCase(btest.DBBazaarTestCase):
    """
    Test many-to-many associations.
    """
    def checkAsc(self):
        mem_data = []
        for obj in self.bazaar.getObjects(app.Employee):
            for val in obj.orders:
                self.assert_(val is not None, \
                    'referenced object cannot be None (application object key: %d)' % obj.__key__)
                mem_data.append((obj.__key__, val.__key__))
        mem_data.sort()

        dbc = self.bazaar.motor.db_conn.cursor()
        dbc.execute('select employee, "order" from employee_orders order by employee, "order"')
        db_data = dbc.fetchall()
        db_data.sort()

        self.assertEqual(db_data, mem_data, 'database data are different than memory data')


    def testLoading(self):
        """Test many-to-many association loading
        """
        self.checkAsc()


    def testReloading(self):
        """Test many-to-many association loading
        """
        emp = self.bazaar.getObjects(app.Employee)[0]
        orders = emp.orders

        # remove some referenced objects
        assert len(orders) > 0
        for o in orders:
            del orders[o]
        assert len(orders) == 0

        # reload data and check if they are reloaded
        app.Employee.orders.reloadData()
        self.checkAsc()


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
        self.checkAsc()

        # append object with undefined primary key value
        ord1 = app.Order()
        ord1.no = 1002
        ord1.finished = False
        emp.orders.append(ord1)
        self.assertRaises(app.db_module.ProgrammingError, emp.orders.update)
        self.bazaar.rollback()

        self.assertRaises(bazaar.exc.AssociationError, emp.orders.append, None)
        self.assertRaises(bazaar.exc.AssociationError, emp.orders.append, object())
        self.assertRaises(bazaar.exc.AssociationError, emp.orders.append, ord1)


    def testRemoving(self):
        """Test removing objects from many-to-many association
        """
        emp = self.bazaar.getObjects(app.Employee)[0]
        assert len(emp.orders) > 0
        orders = list(emp.orders)
        ord = orders[0]
        del emp.orders[ord]
        self.assert_(ord not in emp.orders, \
            'removed referenced object found in association')
        emp.orders.update()
        self.checkAsc()
        self.assertRaises(bazaar.exc.AssociationError, emp.orders.remove, None)
        self.assertRaises(bazaar.exc.AssociationError, emp.orders.remove, object())
        self.assertRaises(bazaar.exc.AssociationError, emp.orders.remove, ord)


    def testMixedUpdate(self):
        """Test appending and removing objects to/from many-to-many association
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

        assert len(emp.orders) > 0
        orders = list(emp.orders)
        ord = orders[0]
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

        self.checkAsc()

        emp.orders.append(ord)
        emp.orders.remove(ord1)
        emp.orders.remove(ord2)

        self.assert_(ord in emp.orders, \
            'appended referenced object not found in association')
        self.assert_(ord1 not in emp.orders, \
            'removed referenced object found in association')
        self.assert_(ord2 not  in emp.orders, \
            'removed referenced object found in association')

        emp.orders.update()

        self.assert_(ord in emp.orders, \
            'appended referenced object not found in association')
        self.assert_(ord1 not in emp.orders, \
            'removed referenced object found in association')
        self.assert_(ord2 not  in emp.orders, \
            'removed referenced object found in association')

        self.checkAsc()



class OneToManyAssociationTestCase(btest.DBBazaarTestCase):
    """
    Test one-to-many associations.
    """
