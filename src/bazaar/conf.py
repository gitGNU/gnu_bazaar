# $Id: conf.py,v 1.2 2003/06/19 16:39:59 wrobell Exp $

import logging

log = logging.getLogger('bazaar.conf')

"""
<s>Provides classes for mapping application classes to database relations.</s>
<p>
    Application class can be defined by standard Python class definition.
    <code>
        class Person(PersitentObject):
            __metaclass__ = Persistence
            relation      = 'person'
            attrs         = {
                'name'      : Column('name'),
                'surname'   : Column('surname'),
                'birthdate' : Column('birthdate'),
            }
            key_columns = ('name', 'surname')
    </code>

    It is possible to create application class by class instantiation.
    <code>
        Person = Persitence('person')
        Person.addColumn('name')
        Person.addColumn('surname')
        Person.addColumn('birthdate')
        Person.setKey('name', 'surname')
    </code>

    Of course, both ideas can be mixed.
    <code>
        class Person(PersitentObject):
            __metaclass__ = Persistence
            relation      = 'person'

        Person.addColumn('name')
        Person.addColumn('surname')
        Person.addColumn('birthdate')
        Person.setKey('name', 'surname')
    </code>
</p>
"""

class Column:
    """
    <s>Database relation column.</s>
    <attr name = 'name'>Column name.</attr>
    """

    def __init__(self, name):
        """
        <s>Create database relation column.</s>
        <attr name = 'name'>Column name.</attr>
        """
        self.name = name



class Persitence(type):
    """
    <s>Application class metaclass.</s>
    <attr name = 'relation'>Database relation name.</attr>
    <attr name = 'columns'>Database relation column list.</attr>
    """

    def __new__(cls, name, bases = (object, ), data = {}, relation = ''):
        """
        <s>Create application class.</s>
        <attr name = 'relation'>Database relation name.</attr>
        """
        cls_data = {}
        if not relation:
            relation = name

        if 'relation' in data:
            cls_data['relation'] = data['relation']
        else:
            cls_data['relation'] = relation

        if 'columns' in data:
            cls_data['columns'] = data['columns']
        else:
            cls_data['columns'] = {}

        if 'key_columns' in data:
            cls_data['key_columns'] = data['key_columns']
        else:
            cls_data['key_columns'] = None

        c = type.__new__(cls, name, bases, cls_data)

        if __debug__:
            log.debug('new class "%s" for relation "%s"' % (c.__name__, cls_data['relation']))

        assert c, 'class relation should not be empty'

        return c


    def addColumn(cls, name):
        """
        <s>Add relation column.</s>
        <p>This way the application class attribute is defined.</p>
        <attr name = 'name'>Column name.</attr>
        """

        if name in cls.columns:
            raise AttributeError('column "%s" is defined in class "%s"' % (name, cls.__name__))

        cls.columns[name] = Column(name)

        if __debug__: log.debug('column "%s" is added to class "%s"' % (name, cls.__name__))


    def setKey(cls, columns):
        """
        <s>Set relation key.</s>
        <attr name = 'columns'>Key columns.</attr>
        """
        if __debug__: log.debug('key columns "%s"' % (columns, ))

        if len(columns) < 1:
            raise AttributeError , 'key columns list should not be empty'

        # check if given columns exist in list of relation columns
        for c in columns: 
            if c not in cls.columns:
                raise AttributeError('key column "%s" not found on column list' % c)

        cls.key_columns = columns
        if __debug__: log.debug('class "%s" key: %s' % (cls.__name__, cls.key_columns))
