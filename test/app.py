# $Id: app.py,v 1.5 2003/08/27 15:02:47 wrobell Exp $

"""
Sample test application for Bazaar layer testing purposes.

File sql/init.sql contains relations definitions.
"""

import bazaar.conf

db_module = None
dsn = ''

# define test application classes
Order = bazaar.conf.Persitence('Order', relation = 'order')
Order.addColumn('no')
Order.addColumn('finished')
#Order.addColumn('items')
#Order.addColumn('employees')
Order.setKey(('no', ))

Employee = bazaar.conf.Persitence('Employee', relation = 'employee')
Employee.addColumn('name')
Employee.addColumn('surname')
Employee.addColumn('phone')
#Employee.addColumn('orders')
Employee.setKey(('name', 'surname'))

Article = bazaar.conf.Persitence('Article', relation = 'article')
Article.addColumn('name')
Article.addColumn('price')
Article.setKey(('name',))

OrderItem = bazaar.conf.Persitence('OrderItem', relation = 'order_item')
OrderItem.addColumn('order')
OrderItem.addColumn('pos')
OrderItem.addColumn('quantity')
OrderItem.addColumn('article')
OrderItem.setKey(('order', 'pos'))
