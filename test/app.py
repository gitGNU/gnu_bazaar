# $Id: app.py,v 1.11 2003/11/23 23:39:18 wrobell Exp $

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
#   addColumn('article', article_fkey, Article)
#
#   # 1-n, one side, uni-dir <- does not exist
#
#   # m-n uni-dir
#   addColumn('orders', 'employee', Order, 'employee_orders', 'order')
#
#   # m-n bi-dir; de facto vattr = 'emploeyees'
#   addColumn('orders', 'employee' Order, 'employee_orders', 'order',, 'emploeyees')
#   addColumn('emploeyees', 'order', Employee, 'employee_orders', 'employee', 'orders')
#
# define test application classes
Article = bazaar.conf.Persistence('Article', relation = 'article')
Article.addColumn('name')
Article.addColumn('price')

Order = bazaar.conf.Persistence('Order', relation = 'order')
OrderItem = bazaar.conf.Persistence('OrderItem', relation = 'order_item')
OrderItem.addColumn('pos')
OrderItem.addColumn('quantity')
OrderItem.addColumn('article', 'article_fkey', Article)
OrderItem.addColumn('order', 'order_fkey', Order, vattr = 'items')

Order.addColumn('no')
Order.addColumn('finished')
Order.addColumn('items', vcls = OrderItem, vcol = 'order_fkey', vattr = 'order', update = False)
#Order.addColumn('employees')

Employee = bazaar.conf.Persistence('Employee', relation = 'employee')
Employee.addColumn('name')
Employee.addColumn('surname')
Employee.addColumn('phone')
Employee.addColumn('orders', 'employee', Order, 'employee_orders', 'order')

Department = bazaar.conf.Persistence('Department', relation = 'department')
Boss = bazaar.conf.Persistence('Boss', relation = 'boss')

Boss.addColumn('department', 'dep_fkey', Department, vattr = 'boss')
Department.addColumn('boss', 'boss_fkey', Boss, vattr = 'department')
