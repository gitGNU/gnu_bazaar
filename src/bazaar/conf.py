# $Id: conf.py,v 1.10 2003/08/25 19:01:06 wrobell Exp $

"""
Provides classes for mapping application classes to database relations.

Application class can be defined by standard Python class definition::
    class Order(bazaar.core.PersitentObject):
        __metaclass__ = bazaar.conf.Persistence
        relation      = 'order'
        columns       = {
            'no'        : Column('no'),
            'finished'  : Column('finished'),
            'birthdate' : Column('birthdate'),
        }
        key_columns = ('no')

It is possible to create application class by class instantiation::
    Order = bazaar.conf.Persitence('order')
    Order.addColumn('no')
    Order.addColumn('finished')
    Order.setKey(('no', ))

Of course, both ideas can be mixed::
    class Order(bazaar.core.PersitentObject):
        __metaclass__ = bazaar.conf.Persistence
        relation      = 'order'

    Order.addColumn('no')
    Order.addColumn('finished')
    Order.setKey(('no', ))
"""

import logging

import bazaar.core

log = logging.getLogger('bazaar.conf')


class Column:
    """
    Describes database relation column.

    The column name is application class attribute.

    @ivar name: Column name.
    """

    def __init__(self, name):
        """
        Create database relation column.

        @param name: Column name.
        """
        self.name = name



class Persitence(type):
    """
    Application class metaclass.

    Programmer defines application classes with the metaclass. The
    class is assigned to the database relation.  If programmer does not
    provide a database relation, then class name will be used as
    relation name.

    @ivar relation: Database relation name.
    @ivar columns: Database relation column list.
    @ivar key_columns: Database relation column names.
    """

    def __new__(cls, name, bases = (bazaar.core.PersistentObject, ), data = None, relation = ''):
        """
        Create application class.

        @param relation: Database relation name.
        """
        if data is None:
            data = {}

        if not relation:
            relation = name

        if 'relation' not in data:
            data['relation'] = relation

        if 'columns' not in data:
            data['columns'] = {}

        if 'key_columns' not in data:
            data['key_columns'] = ()

        if 'getKey' not in data:
            data['getKey'] = None

        c = type.__new__(cls, name, bases, data)

        if __debug__:
            log.debug('new class "%s" for relation "%s"' % (c.__name__, data['relation']))

        assert c.relation, 'class relation should not be empty'

        return c


    def addColumn(cls, name):
        """
        Add relation column.

        This way the application class attribute is defined.

        @param name: Column name.
        """

        if name in cls.columns:
            raise ValueError('column "%s" is already defined in class "%s"' % (name, cls.__name__))

        cls.columns[name] = Column(name)

        if __debug__: log.debug('column "%s" is added to class "%s"' % (name, cls.__name__))


    def setKey(cls, columns):
        """
        Set relation key.

        @param columns: List of key columns. It cannot be empty and all specified
            columns should exist on relation column list.
        """
        if __debug__: log.debug('key columns "%s"' % (columns, ))

        if len(columns) < 1:
            raise ValueError , 'list of key\'s columns should not be empty'

        # check if given columns exist in list of relation columns
        for c in columns: 
            if c not in cls.columns:
                raise ValueError('key\'s column "%s" not found on list of relation columns' % c)

        cls.key_columns = tuple(columns)

        #
        # object key value extraction methods
        #

        # get multi column key value from object
        def getMKey(cls, obj):
#            if __debug__: log.debug('class "%s" object key value: "%s"' \
#                % (cls,  tuple([obj.__dict__[c] for c in cls.key_columns])))
            return tuple([obj.__dict__[c] for c in cls.key_columns])

        # get one column key value from object
        def getKey(cls, obj):
#            if __debug__: log.debug('class "%s" object key value: "%s"' \
#                % (cls,  obj.__dict__[cls.key_columns[0]]))
            return obj.__dict__[cls.key_columns[0]]

        # create class methods for object key extraction 
        if len(cls.key_columns) == 1:
            cls.getKey = classmethod(getKey)
            if __debug__: log.debug('class "%s" single column key extraction method' % cls)
        else:
            cls.getKey = classmethod(getMKey)
            if __debug__: log.debug('class "%s" multi column key extraction method' % cls)

        if __debug__: log.debug('class "%s" key: %s' % (cls.__name__, cls.key_columns))
