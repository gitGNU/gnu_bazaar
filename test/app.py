# $Id: app.py,v 1.6 2003/09/03 22:30:38 wrobell Exp $

"""
Sample test application for Bazaar layer testing purposes.

File sql/init.sql contains relations definitions.
"""

import bazaar.conf

db_module = None
dsn = ''

# define test application classes
Order = bazaar.conf.Persistence('Order', relation = 'order')
Order.addColumn('no')
Order.addColumn('finished')
#Order.addColumn('items')
#Order.addColumn('employees')
Order.setKey(('no', ))

Employee = bazaar.conf.Persistence('Employee', relation = 'employee')
Employee.addColumn('name')
Employee.addColumn('surname')
Employee.addColumn('phone')
#Employee.addColumn('orders')
Employee.setKey(('name', 'surname'))

Article = bazaar.conf.Persistence('Article', relation = 'article')
Article.addColumn('name')
Article.addColumn('price')
Article.setKey(('name',))

OrderItem = bazaar.conf.Persistence('OrderItem', relation = 'order_item')
OrderItem.addColumn('order')
OrderItem.addColumn('pos')
OrderItem.addColumn('quantity')
OrderItem.addColumn('article_fkey', 'article', Article, ('article_fkey',))
OrderItem.setKey(('order', 'pos'))
