# $Id: app.py,v 1.2 2004/12/20 07:39:52 wrobell Exp $
#
# Bazaar ORM - an easy to use and powerful abstraction layer between
# relational database and object oriented application.
#
# Copyright (C) 2000-2004 by Artur Wroblewski <wrobell@pld-linux.org>
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
Sample test application for Bazaar ORM layer testing purposes.

File sql/init.sql contains relations definitions.
"""

import bazaar.conf

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
#   addColumn('orders', 'employee' Order, 'employee_orders', 'order', 'employees')
#   addColumn('employees', 'order', Employee, 'employee_orders', 'employee', 'orders')
#
# define test application classes
Article = bazaar.conf.Persistence('Article', relation = 'article', modname = 'bazaar.test.app')
Article.addColumn('name')
Article.addColumn('price')

Order = bazaar.conf.Persistence('Order', relation = 'order', modname = 'bazaar.test.app')
OrderItem = bazaar.conf.Persistence('OrderItem', relation = 'order_item', modname = 'bazaar.test.app')
Employee = bazaar.conf.Persistence('Employee', relation = 'employee', modname = 'bazaar.test.app')

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

Department = bazaar.conf.Persistence('Department', relation = 'department', modname = 'bazaar.test.app')
Boss = bazaar.conf.Persistence('Boss', relation = 'boss', modname = 'bazaar.test.app')

Boss.addColumn('department', 'dep_fkey', Department, vattr = 'boss')
Department.addColumn('boss', 'boss_fkey', Boss, vattr = 'department')



cls_list = (Order, Employee, Article, OrderItem, Boss, Department)
