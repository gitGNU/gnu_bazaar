# $Id: assoc.py,v 1.2 2003/09/07 11:49:30 wrobell Exp $

import app
import btest

class OneToOneAssociationTestCase(btest.DBBazaarTestCase):
    """
    Test one-to-one associations.
    """

    def testLoading(self):
        """Test one-to-one association loading"""

        self.bazaar.getObjects(app.OrderItem)
        dbc = self.bazaar.motor.dbc
        dbc.execute('select "order", pos, article_fkey from order_item')
        row = dbc.fetchone()
        while row:
            order_item = self.bazaar.brokers[app.OrderItem].cache[(row[0], row[1])]

            # check the value of foreign key
            self.assertEqual(order_item.article_fkey, row[2], \
                'article foreign key mismatch "%s" != "%s"' % (order_item.article_fkey, row[2]))

            # check the value of associated object's primary key
            self.assertEqual(order_item.article.key, row[2], \
                'article primary key mismatch "%s" != "%s"' % (order_item.article.key, row[2]))

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

        oi = app.OrderItem()
        oi.order = 0
        oi.pos = 1000
        oi.article = art
        oi.quantity = 5
        self.bazaar.add(art)
        self.bazaar.add(oi)
