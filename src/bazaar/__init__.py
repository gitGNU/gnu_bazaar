# $Id: __init__.py,v 1.9 2004/01/21 23:06:27 wrobell Exp $
"""
Bazaar is an easy to use and powerful abstraction layer between
relational database and object oriented application.

Features:
    - easy to use - define classes and programmer is ready to get and modify
      application data in object-oriented way (no additional steps such as
      code generation is required)

    - object-oriented programing and feel - using classes, objects and references
      instead of relations, its columns, primary and foreign keys

    - object-oriented database operations:
        - add, update, delete
        - get and reload
        - easy object finding with support for SQL queries
        - association data load and reload

    - application class relationships:
        - one-to-one, one-to-many and many-to-many
        - uni-directional and bi-directional

    - application objects and association data cache integrated with Python
      garbage collector:
        - full - load all rows at once from relation
        - lazy - load one row from relation

    - configurable - connection string, DB API module, class relations, object and
      association data cache types, etc.

Requirements:
    - Python 2.3
    - Python DB API 2.0 module with ``format'' and ``pyformat'' parameter
      style support (tested with U{psycopg 1.1.10<http://initd.org/software/psycopg>})
    - RDBMS (tested with U{PostgreSQL 7.4<http://www.postgresql.org>})

This is free software distributed under U{GNU Lesser General Public
License<http://www.fsf.org/licenses/lgpl.html>}. Download it from
U{project's page<http://savannah.nongnu.org/projects/bazaar/>}
on U{Savannah<http://savannah.nongnu.org>}.

Bazaar is easy to use, but is designed for people who know both
object-oriented and relational technologies, their advantages,
disadvantages and differences between them (U{``The Object-Relational
Impedance Mismatch''<http://www.agiledata.org/essays/impedancemismatch.html>} reading
is recommended).

Using the layer
===============

Creating application classes
----------------------------

Let's consider following diagram::

    Order < 1 ---- * > OrderItem
    OrderItem | * ---- 1 > Article

There are three classes and two associations. Both relationships are one to
many associations, but first one is bi-directional and second is
uni-directional.

Class definition (more about class and relationships defining can be
found in L{bazaar.conf} module documentation) should be like::

    # import bazaar module used to create classes
    import bazaar.conf

    # create class for articles
    # class name is specified, relation equals to class name
    Article = bazaar.conf.Persistence('Article')

    # add class attributes and relation columns
    # class attribute name is the same as relation column name
    Article.addColumn('name')
    Article.addColumn('price')

    # create order and order items classes
    # class names are different than database relation names
    Order = bazaar.conf.Persistence('Order', relation = 'order')
    OrderItem = bazaar.conf.Persistence('OrderItem', relation = 'order_item')

    Order.addColumn('no')           # order number
    OrderItem.addColumn('pos')      # order item position
    OrderItem.addColumn('quantity') # article quantity

    # define bi-directional association between Order and OrderItem classes
    #
    # from OrderItem perspective
    # attribute name: order
    # relation column name: order_fkey
    # referenced object's class: Order
    # referenced object's class attribute name: items
    OrderItem.addColumn('order', 'order_fkey', Order, vattr = 'items')

    # from Order perspective
    # attribute name: items
    # referenced object's class: OrderItem
    # referenced relation column name: order_fkey
    # referenced object's class attribute name: order
    Order.addColumn('items', vcls = OrderItem, vcol = 'order_fkey', vattr = 'order')

    # define uni-directional association between OrderItem and Article classes
    # 
    # attribute name: article
    # relation column name: article_fkey
    # referenced object's class: Article
    OrderItem.addColumn('article', 'article_fkey', Article)

Now, SQL schema can be created::

    # primary key values generator
    create sequence order_seq;
    create table "order" (
        # every application object is identified with __key__ attribute
        __key__      integer,
        no           integer not null unique,
        finished     boolean not null,
        primary key (__key__)
    );

    create sequence article_seq;
    create table article (
        __key__      integer,
        name         varchar(20) not null,
        price        numeric(10,2) not null,
        unique (name),
        primary key (__key__)
    );

    create sequence order_item_seq;
    create table order_item (
        __key__      integer,
        order_fkey   integer,
        pos          integer not null,
        article_fkey integer not null,
        quantity     numeric(10,3) not null,
        primary key (__key__),
        unique (order_fkey, pos),

        # association between Order and OrderItem
        foreign key (order_fkey) references "order"(__key__),

        # association between OrderItem and Article
        foreign key (article_fkey) references article(__key__)
    );

Application code
----------------

Application must import Bazaar core module::

    import bazaar.core
    import psycopg

DB API module is imported, too. However, it is not obligatory because it can
be specified in config file, see L{bazaar.config} module documentation for
details.

Create Bazaar layer instance. There are several parameters
(L{bazaar.core.Bazaar}), but now in this example only list of application
classes and DB API module are specified::

    bzr = bazaar.core.Bazaar((Article, Order, OrderItem), dbmod = psycopg)

Connect to database::

    bzr.connectDB('dbname = ord')

Connection string is standard database source name (dsn) described in DB
API 2.0 specification. Connection can be established with
L{bazaar.core.Bazaar} class constructor, too.

Create application object::

    apple = Article()
    apple.name = 'apple'
    apple.price = 2.33

    
Object constructor can initialize object attributes::

    oi1 = OrderItem(pos = 1, quantity = 10)
    oi1.article = apple

    peach = Article()
    peach.name = 'peach'
    peach.price = 2.34

    oi2 = OrderItem(article = peach)
    oi2.pos = 2
    oi2.quantity = 40

Create new order::

    ord = Order(no = 1)


Append order items to order. It can be made in two ways
(it is bi-directional relationship)::

    ord.items.append(oi1)
    oi2.order = ord

Finally, add created objects data into database::

    bazaar.add(apple)
    bazaar.add(peach)
    bazaar.add(oi1)
    bazaar.add(oi2)
    bazaar.add(ord)

Objects can be updated and deleted, too (L{bazaar.core.Bazaar}).


Now, let's play with some objects. Remove second order item from order no 1::

    del ord.items[oi2]

And update association::

    ord.items.update()

Add second order item again::

    ord.items.append(oi2)
    ord.items.update()

Change apple price::

    apple.price = 2.00

And update database data::

    bzr.update(apple)

Print all orders::

    for ord in bzr.getObjects(Order):
        print ord


Find order number 1::

    bzr.find(Order, {'no': 1})

Find order items for article "apple"::

    bzr.find(OrderItem,  {'article': apple})

Finally, commit transaction::

    bzr.commit()
"""
# @todo:
# Bazaar supports GUI development with set of powerful widgets designed
# to simplify development of presentation, manipulation and
# data searching.
