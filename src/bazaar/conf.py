# $Id: conf.py,v 1.15 2003/09/19 14:58:32 wrobell Exp $
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
    Order = bazaar.conf.Persistence('order')
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
import bazaar.assoc

log = logging.getLogger('bazaar.conf')


def getConvertKeyMethod(key_columns):
    """
    Create conversion method of key value into a tuple of values.

    Key can be either single column or multi column. Returned callable
    class is an efficient method for returning key value as a tuple of
    values for both types of keys.

    Examples::

        # convert single column key value
        key = 'John'
        convert_key = getConvertKeyMethod(('name',))()
        convert_key(key)
        ('John', )

        # get multi column key value
        key = ('John', 'Smith')
        convert_key = getConvertKeyMethod(('name', 'surname'))()
        convert_key(key)
        ('John', 'Smith')


    @param key_columns: Names of key columns.
    """
    assert key_columns >= 1

    def toSTuple(self, key): return (key, )
    def toMTuple(self, key): return key

    class ConvertKeyTool(object):
        if len(key_columns) == 1:
            __call__ = toSTuple
            if __debug__: log.debug('single column key conversion method')
        else:
            __call__ = toMTuple
            if __debug__: log.debug('multi column key conversion method')
    return ConvertKeyTool



def getGetKeyMethod(key_columns):
    """
    Create extraction method of key value from dictionary.

    Key can be either single column or multi column. Returned callable
    class is an efficient method for returning key value for both types of
    keys.

    Examples::

        data = {'name': 'John', 'surname': 'Smith', 'birthdate': '01-09-1900'}
        
        # get single column key value
        get_key = getGetKeyMethod(('name',))()
        get_key(data)
        'John'

        # get multi column key value
        get_key = getGetKeyMethod(('name', 'surname'))()
        get_key(data)
        ('John', 'Smith')

    @param key_columns: Names of key columns.
    """

    assert key_columns >= 1

    def getSKey(self, data): return data[self.cols[0]]
    def getMKey(self, data): return tuple([data[col] for col in self.cols])

    class GetKeyTool(object):
        if len(key_columns) == 1:
            __call__ = getSKey
            if __debug__: log.debug('single column key setting method')
        else:
            __call__ = getMKey
            if __debug__: log.debug('multi column key setting method')
        cols = key_columns
    return GetKeyTool



class Column:
    """
    Describes application class attribute.

    The column name is attribute name by default.

    Take a look L{bazaar.conf.Persistence.addColumn}'s method description
    to understand how the class describes associations between
    application classes.

    @ivar name: Application class column name.
    @ivar attr: Application class attribute name.
    @ivar cls:  Application class of associated objects.

    @ivar afkey: Foreign key's column list.
    @ivar link:  Many-to-many link relation name.
    @ivar bfkey: Foreign key's column list.

    @ivar one_to_one:  Association is one-to-one association.
    @ivar association: Association descriptor of given column.

    @see bazaar.conf.Persistence.addColumn
    """

    def __init__(self, name, attr = None):
        """
        Create application class column.

        @param name: Column name.
        @param attr: Attribute name.
        """
        self.name = name

        if attr is None:
            self.attr = self.name
        else:
            self.attr = attr

        self.cls = None
        self.association = None
        self.afkey = None
        self.link = None
        self.bfkey = None

        self.one_to_one = False



class Persistence(type):
    """
    Application class metaclass.

    Programmer defines application classes with the metaclass. The
    class is assigned to the database relation.  If programmer does not
    provide a database relation, then class name will be used as
    relation name.

    @ivar relation: Database relation name.
    @ivar columns: Database relation list of columns.
    @ivar key_columns: Database relation key column names.
    """

    def __new__(self, name, bases = (bazaar.core.PersistentObject, ), data = None, relation = ''):
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

        if 'convertKey' not in data:
            data['convertKey'] = None

        if 'getKey' not in data:
            data['getKey'] = None

        c = type.__new__(self, name, bases, data)

        if __debug__:
            log.debug('new class "%s" for relation "%s"' % (c.__name__, data['relation']))

        assert c.relation, 'class relation should not be empty'

        return c


    def addColumn(self, name, attr = None, cls = None,
            afkey = None, link = None, bfkey = None, bidir = None):
        """
        Add column to persistent application class.

        This way the application class attribute and associations between
        application classes are defined.

        @param name: Application class column name.
        @param attr: Application class attribute name, defaults to name.
        @param cls:  Application class of associated objects.

        @param afkey: Foreign key's column list.
        @param link:  Many-to-many link relation name.
        @param bfkey: Foreign key's column list.

        @param bidir:

        @see: bazaar.conf.Column
        """

        if name in self.columns:
            raise ValueError('column "%s" is already defined in class "%s"' % (name, self.__name__))

        col = Column(name, attr)

        def setAssociation(cls, col, assoc_cls, fkey):
            col.association = assoc_cls(col)
            setattr(cls, col.attr, col.association)
            # set association foreign key extraction and conversion methods
            col.association.getKey = getGetKeyMethod(fkey)()
            col.association.convertKey = getConvertKeyMethod(fkey)()


        if cls is not None:
            col.cls = cls
            if bfkey is not None and afkey is None:
                pass
            elif bfkey is not None and afkey is not None and link is not None:
                pass
            elif afkey is not None:
                # fixme: throw MappingError exc when len(afkey) < 1
                col.afkey = afkey
                assoc_cls = bazaar.assoc.UniDirOneToOneAssociation
            else:
                pass # throw MappingError exc

            assert issubclass(assoc_cls, bazaar.assoc.AssociationReferenceProxy)

            if bidir is None:
                setAssociation(self, col, assoc_cls, col.afkey)
                if __debug__:
                    log.debug('uni-directional association %s.%s -> %s: ' % (self, attr, cls))

            else: # if association is going to be bi-directional
                if __debug__:
                    log_info = 'bi-directional association %s.%s <-> %s.%s: %%s' \
                        % (self, attr, cls, bidir)
                    log.info(log_info % 'detected')

                # If second direction column is defined, then create
                # association objects, otherwise delay it.
                # The association objects will be created while defining second
                # direction column.
                if bidir in cls.columns:
                    if __debug__:
                        log.info(log_info % 'creating association objects')

                    if issubclass(assoc_cls, bazaar.assoc.OneToOneAssociation):
                        assoc_cls = bazaar.assoc.BiDirOneToOneAssociation
                    else:
                        pass # throw MappingError exception
                        
                    setAssociation(self, col, assoc_cls, afkey)
                    setAssociation(cls, cls.columns[bidir], assoc_cls, cls.columns[bidir].afkey)
                else:
                    if __debug__:
                        log.info(log_info % 'delaying creation of association objects')

        self.columns[name] = col

        if __debug__: log.debug('column "%s" is added to class "%s"' % (name, self.__name__))


    def setKey(self, columns):
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
            if c not in self.columns:
                raise ValueError('key\'s column "%s" not found on list of relation columns' % c)

        self.key_columns = tuple(columns)

        # set key value extraction and conversion methods
        self.getKey = getGetKeyMethod(self.key_columns)()
        self.convertKey = getConvertKeyMethod(self.key_columns)()

        if __debug__: log.debug('class "%s" key: %s' % (self.__name__, self.key_columns))
