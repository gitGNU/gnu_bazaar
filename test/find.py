# $Id: find.py,v 1.1 2003/11/22 14:27:17 wrobell Exp $

import unittest

import app
import btest

"""
Test searching objects in database.
"""

class FindTestCase(btest.DBBazaarTestCase):
    """
    Test aplication objects searching in database.
    """
    def checkObjectList(self, objs, query):
        """
        Check if objects have the same primary key value as returned by the
        query.

        SQL query C{query} finds primary key values (first column), which
        are sorted ascending.

        @param objs: list of objects
        @param query: SQL query
        """
        objs.sort(lambda o1, o2: cmp(o1.__key__, o2.__key__))
#        print [o.__key__ for o in objs]
        dbc = self.bazaar.motor.db_conn.cursor()
        dbc.execute(query)
        row = dbc.fetchone()
        self.assertEqual(len(objs), dbc.rowcount)
        i = 0
        while row:
            self.assertEqual(objs[i].__key__, row[0])
            row = dbc.fetchone()
            i += 1


    def testOOFind(self):
        """Test object oriented searching"""
        articles = list(self.bazaar.find(app.Article, {
            'name': 'art 00',
        }))
        art = articles[0]
        self.checkObjectList(articles, \
            "select __key__ from article where name = 'art 00' order by 1")

        articles = list(self.bazaar.find(app.Article, {
            'name' : 'art 01',
            'price': '1.12',
        }))
        self.checkObjectList(articles, \
            "select __key__ from article where name = 'art 01'"
            " and price = 1.12 order by 1")

        orders = list(self.bazaar.find(app.Order, {
            'no'      : 1,
            'finished': False,
        }))
        self.checkObjectList(orders, \
            "select __key__ from \"order\" where no = 1"
            " and not finished order by 1")

        ord = orders[0]

        ois = list(self.bazaar.find(app.OrderItem, {
            'article': art,
            'order'  : ord,
        }))
        self.checkObjectList(ois, \
            "select __key__ from order_item where article_fkey = %d"
            " and order_fkey = %d order by 1" % (art.__key__, ord.__key__))


    def testSQLFind(self):
        """Test SQL searching"""
        orders = list(self.bazaar.find(app.Order,
            "select __key__ from \"order\""
            " where no = %(no)s and finished = %(finished)s", {
                'no'      : 1,
                'finished': False,
            }))
        self.checkObjectList(orders, \
            "select __key__ from \"order\""
            " where no = %(no)s and finished = %(finished)s order by 1" % {
                'no'      : 1,
                'finished': False,
            })

        ord = orders[0]

        ois = list(self.bazaar.find(app.OrderItem,
            "select quantity, __key__ from order_item"
            " where quantity > %(quantity)s ", {
                'quantity': 5,
            }, 1))

        self.checkObjectList(ois, \
            "select __key__ from order_item"
            " where quantity > %(quantity)s order by 1" % {
                'quantity': 5,
            })
