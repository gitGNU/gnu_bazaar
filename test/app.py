# $Id: app.py,v 1.13 2004/01/21 23:06:28 wrobell Exp $

"""
Sample test application for Bazaar layer testing purposes.

File sql/init.sql contains relations definitions.
"""

import bazaar.conf

dbmod = None
dsn = ''

####
#   # simple
#   .addColumn('price')
#   .addColumn('price', 'price_col')
#
#   # 1-1 uni-dir
#   .addColumn('boss', 'boss_fkey', Boss)
#
#   # 1-1 bi-dir
#   .addColumn('boss', 'boss_fkey', Boss, vattr = 'department')
#   .addColumn('department', 'dep_fkey', Department, vattr = 'boss')
#
#   # 1-n, bi-dir
#   addColumn('items', vcls = OrderItem, vcol = 'order_fkey', vattr = 'order')
#   addColumn('order', 'order_fkey', Order, vattr = 'items')
#
#   # 1-n, many side, uni-dir <- it is like 1-1 uni-dir
#   addColumn('article', 'article_fkey', Article)
#
#   # 1-n, one side, uni-dir <- does not exist
#
#   # m-n uni-dir
#   addColumn('orders', 'employee', Order, 'employee_orders', 'order')
#
#   # m-n bi-dir; de facto vattr = 'employees'
#   addColumn('orders', 'employee' Order, 'employee_orders', 'order', 'empleyees')
#   addColumn('empleyees', 'order', Employee, 'employee_orders', 'employee', 'orders')
#
# define test application classes
Article = bazaar.conf.Persistence('Article', relation = 'article', modname = 'app')
Article.addColumn('name')
Article.addColumn('price')

Order = bazaar.conf.Persistence('Order', relation = 'order', modname = 'app')
OrderItem = bazaar.conf.Persistence('OrderItem', relation = 'order_item', modname = 'app')
Employee = bazaar.conf.Persistence('Employee', relation = 'employee', modname = 'app')

OrderItem.addColumn('pos')
OrderItem.addColumn('quantity')
OrderItem.addColumn('article', 'article_fkey', Article)
OrderItem.addColumn('order', 'order_fkey', Order, vattr = 'items')

Order.addColumn('no')
Order.addColumn('finished')
Order.addColumn('items', vcls = OrderItem, vcol = 'order_fkey', vattr = 'order', update = False)
Order.addColumn('employees', 'order', Employee, 'employee_orders', 'employee')

Employee.addColumn('name')
Employee.addColumn('surname')
Employee.addColumn('phone')
Employee.addColumn('orders', 'employee', Order, 'employee_orders', 'order')

Department = bazaar.conf.Persistence('Department', relation = 'department', modname = 'app')
Boss = bazaar.conf.Persistence('Boss', relation = 'boss', modname = 'app')

Boss.addColumn('department', 'dep_fkey', Department, vattr = 'boss')
Department.addColumn('boss', 'boss_fkey', Boss, vattr = 'department')
