# $Id: bzr.py,v 1.7 2005/05/29 18:41:11 wrobell Exp $
#
# Bazaar ORM - an easy to use and powerful abstraction layer between
# relational database and object oriented application.
#
# Copyright (C) 2000-2005 by Artur Wroblewski <wrobell@pld-linux.org>
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

"""
Run all Bazaar ORM tests.
"""

import bazaar.core

import bazaar.test
import bazaar.test.app

bazaar.test.TestCase.cls_list = bazaar.test.app.cls_list

class TestCase(bazaar.test.DBTestCase):
    """
    Basic test case for Bazaar ORM library tests.
    """
    def setUp(self):
        """
        Set up test.
        """
        super(TestCase, self).setUp()

        # bazaar.test.cache tests for lazy cache!
        assert not self.config.has_section('bazaar.cls')
        assert not self.config.has_section('bazaar.asc')
        assert bazaar.test.app.Article.cache == bazaar.cache.FullObject
        assert bazaar.test.app.Order.getColumns()['items'].cache \
            == bazaar.cache.FullAssociation
        assert bazaar.test.app.Employee.getColumns()['orders'].cache \
            == bazaar.cache.FullAssociation


    def checkObjects(self, cls, amount = None, key = None):
        """
        Check all application objects data integrity.

        @param amount: Amount of objects.
        """
        params = {
            bazaar.test.app.Order: {
                'relation': 'order',
                'cols'    : ('no', 'finished'),
                'test'    : self.checkOrder
            },
            bazaar.test.app.Article: {
                'relation': 'article',
                'cols'    : ('name', 'price'),
                'test'    : self.checkArticle
            },
            bazaar.test.app.OrderItem: {
                'relation': 'order_item',
                'cols'    : ('order_fkey', 'pos', 'quantity'),
                'test'    : self.checkOrderItem
            },
            bazaar.test.app.Employee: {
                'relation': 'employee',
                'cols'    : ('name', 'surname', 'phone'),
                'test'    : self.checkEmployee
            },
            bazaar.test.app.EmployeeAlt: {
                'relation': 'employee_alt',
                'cols'    : ('name', 'surname', 'phone', 'status'),
                'test'    : self.checkEmployeeAlt
            },
            bazaar.test.app.Boss: {
                'relation': 'boss',
                'cols'    : ('dep_fkey',),
                'test'    : self.checkBoss
            },
            bazaar.test.app.Department: {
                'relation': 'department',
                'cols'    : ('boss_fkey',),
                'test'    : self.checkDepartment
            }
        }

        dbc = self.bazaar.motor.conn.cursor()

        query = 'select "__key__", %s from "%s"' \
                % (', '.join(['"%s"' % col for col in params[cls]['cols']]),
                params[cls]['relation'])

        if key is not None:
            query += 'where __key__ = %d' % key

        dbc.execute(query)

        if amount is not None:
            self.assertEqual(amount, dbc.rowcount, \
                'class %s: objects: %d, rows: %d' % (cls, amount, dbc.rowcount))

        row = dbc.fetchone()
        while row:
            self.assert_(params[cls]['test'](row[0], row[1:]),
                'data integrity test failed: %s' % str(row))

            row = dbc.fetchone()


    def checkOrder(self, key, row):
        """
        Order class data integrity test function.
        """
        order = self.bazaar.brokers[bazaar.test.app.Order].cache[key]
        return order.no == row[0] and order.finished == row[1]


    def checkEmployee(self, key, row):
        """
        Employee class data integrity test function.
        """
        emp = self.bazaar.brokers[bazaar.test.app.Employee].cache[key]
        return emp.name == row[0] and emp.surname == row[1] \
            and emp.phone == row[2]


    def checkEmployeeAlt(self, key, row):
        """
        Employee class data integrity test function.
        """
        emp = self.bazaar.brokers[bazaar.test.app.EmployeeAlt].cache[key]

        # status should be equal 2 as it is read only column
        #
        # phone can be None (not fetched from db) or set to value before
        # writing it
        return emp.name == row[0] and emp.surname == row[1] \
            and (emp.phone == None or emp.phone == row[2]) and row[3] == 2


    def checkArticle(self, key, row):
        """
        Article class data integrity test function.
        """
        art = self.bazaar.brokers[bazaar.test.app.Article].cache[key]
        return art.name == row[0] and art.price == row[1]


    def checkOrderItem(self, key, row):
        """
        OrderItem class data integrity test function.
        """
        order_item = self.bazaar.brokers[bazaar.test.app.OrderItem].cache[key]
        return order_item.order_fkey == row[0] and order_item.pos == row[1] \
            and order_item.quantity == row[2]


    def checkBoss(self, key, row):
        """
        Boss class data integrity test function.
        """
        boss = self.bazaar.brokers[bazaar.test.app.Boss].cache[key]
        return boss.dep_fkey == row[0]


    def checkDepartment(self, key, row):
        """
        Department class data integrity test function.
        """
        dep = self.bazaar.brokers[bazaar.test.app.Department].cache[key]
        return dep.boss_fkey == row[0]


    def getCache(self, cls):
        """
        Utility function to get cache of application class.

        @param cls: Application class.

        @return: Application class cache.
        """
        return self.bazaar.brokers[cls].cache


    def checkListAsc(self, cls, attr, query):
        """
        Check association data with data stored in database.
        """
        mem_data = []
        for obj in self.bazaar.getObjects(cls):
            for val in getattr(obj, attr):
                self.assert_(val is not None,
                    'referenced object cannot be None' \
                    ' (application object key: %d)' % obj.__key__)

                mem_data.append((obj.__key__, val.__key__))
        mem_data.sort()

        dbc = self.bazaar.motor.conn.cursor()
        dbc.execute(query)
        db_data = dbc.fetchall()
        db_data.sort()
        self.assertEqual(db_data, mem_data,
            """database data are different than memory data
            database data : %s
            memory data   : %s
            difference    : %s
            """ % (db_data, mem_data, set(db_data) ^ set(mem_data)))


    def checkOrdAsc(self):
        """
        Check association data between Order and OrderItem classes
        with data stored in database.
        """
        self.checkListAsc(bazaar.test.app.Order, 'items', \
            'select order_fkey, __key__  from order_item' \
            ' where order_fkey is not null order by order_fkey, __key__')


    def checkEmpAsc(self):
        """
        Check association data between Order and Employee classes
        with data stored in database.
        """
        self.checkListAsc(bazaar.test.app.Employee, 'orders', \
            'select employee, "order" from employee_orders' \
            ' order by employee, "order"')



if __name__ == '__main__':
    bazaar.test.main(('bazaar.test.assoc', 'bazaar.test.cache',
        'bazaar.test.conf', 'bazaar.test.config', 'bazaar.test.connection',
        'bazaar.test.core', 'bazaar.test.find', 'bazaar.test.init'))
