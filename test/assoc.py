# $Id: assoc.py,v 1.4 2003/09/24 16:48:17 wrobell Exp $

import app
import btest

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
        order_item = self.bazaar.getObjects(app.OrderItem)[0]

        art = app.Article()
        art.name = 'xxx1'
        art.price = 2.3
        self.bazaar.add(art)
        order_item.article = art
        self.bazaar.update(order_item)

        art = app.Article()
        art.name = 'xxx2'
        art.price = 2.3
        order_item.article = art
        self.bazaar.add(art)
        self.bazaar.update(order_item)

        order_item.article = None
        self.assertRaises(app.db_module.ProgrammingError, self.bazaar.update, order_item)
        self.bazaar.rollback() # exception line above, so rollback

        art = app.Article()
        art.name = 'xxx3'
        art.price = 2.3



class ManyToManyAssociationTestCase(btest.DBBazaarTestCase):
    """
    Test many-to-many associations.
    """
    def testLoading(self):
        """Test many-to-many association loading.
        """
        emps = self.bazaar.getObjects(app.Employee)
        for emp in emps:
            print emp.__key__, len(emp.orders)


    def testAppending(self):
        """Test appending to many-to-many association.
        """
        emps = self.bazaar.getObjects(app.Employee)
        ord1 = app.Order()
        ord1.no = 1002
        ord1.finished = False
        ord2 = app.Order()
        ord2.no = 1003
        ord2.finished = False

        emps[0].orders.append(ord1)
#        emps[0].orders[0] = ord2

        self.bazaar.add(ord1)
        print 'key', ord1.__key__
#        self.bazaar.add(ord2)

        emps[0].orders.update()
        app.Employee.orders.reloadData()
        print 'e', emps[0].__key__, emps[0].orders, len(emps[0].orders)



class OneToManyAssociationTestCase(btest.DBBazaarTestCase):
    """
    Test one-to-many associations.
    """
    def testLoading(self):
        """Test one-to-many association loading.
        """
        orders = self.bazaar.getObjects(app.Order)
        for order in orders:
            print 'l:', order.__key__, len(order.items)


    def testAppending(self):
        """Test appending to one-to-many association.
        """
        orders = self.bazaar.getObjects(app.Order)
        arts = self.bazaar.getObjects(app.Article)

        oi1 = app.OrderItem()
        oi1.pos = 1002
        oi1.article = arts[0]
        oi1.quantity = 5

        oi2 = app.OrderItem()
        oi2.pos = 1003
        oi2.article = arts[1]
        oi2.quantity = 6

        oi3 = app.OrderItem()
        oi3.pos = 1004
        oi3.article = arts[1]
        oi3.quantity = 7

        order = orders[1]

        print 'e1', order.__key__, order.items, len(order.items)

        order.items.append(oi1)
        oi2.order = order
##        order.items[0] = oi3

        self.bazaar.add(oi1)
        self.bazaar.add(oi2)
        self.bazaar.add(oi3)
        print 'oi1 key', oi1.__key__
        print 'oi2 key', oi2.__key__
##        print 'oi3 key', oi3.__key__

        order.items.update()
        app.Order.items.reloadData()
        print 'e2', order.__key__, order.items, len(order.items)
