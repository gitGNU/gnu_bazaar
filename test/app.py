# $Id: app.py,v 1.3 2003/07/19 10:01:59 wrobell Exp $

"""
<s>Sample test application for Bazaar layer testing purposes.</s>
<p>
    File sql/init.sql contains relations definitions.
</p>
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
#OrderItem.addColumn('article')
OrderItem.setKey(('order', 'pos'))
