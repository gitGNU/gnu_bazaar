# $Id: assoc.py,v 1.1 2003/09/03 22:48:40 wrobell Exp $

import app
import btest

class OneToOneAssociationTestCase(btest.DBBazaarTestCase):
    """
    Test one-to-one associations.
    """

    def testLoading(self):
        """Test one-to-one association loading"""

        self.bazaar.getObjects(app.OrderItem)
        self.bazaar.getObjects(app.Article) # fixme: to be removed
        dbc = self.bazaar.motor.dbc
        dbc.execute('select "order", pos, article_fkey from order_item')
        row = dbc.fetchone()
        while row:
            order_item = self.bazaar.brokers[app.OrderItem].cache[(row[0], row[1])]
            self.assertEqual(order_item.article_fkey, row[2], \
                'article foreign key mismatch "%s" != "%s"' % (order_item.article_fkey, row[2]))
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
        self.bazaar.update(order_item)
