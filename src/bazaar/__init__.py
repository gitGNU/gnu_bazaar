# $Id: __init__.py,v 1.6 2003/10/03 16:13:54 wrobell Exp $
"""
Bazaar is an easy to use and powerful abstraction layer between
relational database and object oriented application.

Features:
    - easy to use: define classes and programmer is ready to get and modify
      application data in object-oriented way
    - application class relationships:
        - one-to-one
        - one-to-many
        - many-to-many
        - uni-directional
        - bi-directional
    - application objects cache

Requirements:
    - Python 2.3
    - Python DB-API 2.0 module with ``format'' and ``pyformat'' parameter
      style support (tested with U{psycopg 1.1.9<http://initd.org/software/psycopg>})
    - RDBMS (tested with U{PostgreSQL 7.3.4<http://www.postgresql.org>})

This is free software and is distributed under U{GNU Lesser General Public
License<http://www.fsf.org/licenses/lgpl.html>}.

Bazaar is easy to use, but is designed for people who know both
object-oriented and relational technologies, their advantages,
disadvantages and differences between them (U{``The Object-Relational
Impedance Mismatch''<http://www.agiledata.org/essays/impedancemismatch.html>} reading
is recommended).

Using the layer
===============
Diagram::

    Order | 1 ---- * > OrderItem | * ---- 1 > Article

First, define classes (more about class and relationships defining in
L{bazaar.conf} module documentation)::

    Article = bazaar.conf.Persistence('Article', relation = 'article')
    Article.addColumn('name')
    Article.addColumn('price')

    Order = bazaar.conf.Persistence('Order', relation = 'order')
    Order.addColumn('no')
    Order.addColumn('items')

    OrderItem = bazaar.conf.Persistence('OrderItem', relation = 'order_item')
    OrderItem.addColumn('pos')
    OrderItem.addColumn('article')


@todo:
Bazaar supports GUI development with set of powerful widgets designed
to simplify development of presentation, manipulation and
data searching.

More features:
    - differenct cache strategies: lazy, etc.
    - object search
    - security: sql injection, passwords
"""
