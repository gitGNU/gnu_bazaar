# $Id: conf.py,v 1.16 2003/09/20 17:11:24 wrobell Exp $
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

It is possible to create application class by class instantiation::
    Order = bazaar.conf.Persistence('order')
    Order.addColumn('no')
    Order.addColumn('finished')

Of course, both ideas can be mixed::
    class Order(bazaar.core.PersitentObject):
        __metaclass__ = bazaar.conf.Persistence
        relation      = 'order'

    Order.addColumn('no')
    Order.addColumn('finished')

@todo: write tutorial about class configuration
"""

import logging

import bazaar.core
import bazaar.assoc

log = logging.getLogger('bazaar.conf')


class Column:
    """
    Describes application class attribute.

    Application class atribute can be simple attribute or can define
    association (relationship) between application classes.

    When class attribute describes association the @C{vcls} is always
    defined. Depedning on relationship type (1-1, 1-n, m-n,
    uni-directional, bi-directional) some of the attributes @C{vlink},
    @C{vcol}, @C{vattr} are defined, too.

    @ivar attr: Application class attribute name.
    @ivar col: Relation column name (equal to @C{attr} by default).

    @ivar vcls: Class of referenced object(s).
    @ivar link:  Many-to-many link relation name.
    @ivar vcol: Relation column name of referenced object(s).
    @ivar vattr: Attribute name of referenced object(s). 

    @ivar association: Association descriptor of given column.

    @ivar is_one_to_one: Class attribute is one-to-one association.
    @ivar is_one_to_many: Class attribute is one-to-many association.
    @ivar is_many_to_many: Class attribute is many-to-many association.
    @ivar is_bidir: Class attribute describes bi-directional association.
    @ivar is_many: Class attribute is one-to-many or many-to-many association.

    @see: bazaar.conf.Persistence.addColumn bazaar.assoc
    """

    def __init__(self, attr, col = None):
        """
        Create application class attribute description.

        @param attr: Application class attribute name.
        @param col: Relation column.
        """
        self.attr = attr

        if col is None:
            self.col = self.attr
        else:
            self.col = col

        self.vcls = None
        self.link = None
        self.vcol = None
        self.vattr = None
        self.association = None


    is_one_to_one = property(lambda self: \
            self.vcls is not None \
            and self.link is None \
            and self.vcol is None \
    )
    is_one_to_many =  property(lambda self: \
            self.vcls is not None \
            and self.link is None \
            and self.vcol is not None \
            and self.vattr is not None \
    )
    is_many_to_many =  property(lambda self: \
            self.vcls is not None \
            and self.col is not None \
            and self.link is not None \
            and self.vcol is not None \
    )
    is_bidir =  property(lambda self: self.vcls is not None and self.vattr is not None)
    is_many = property(lambda self: self.is_one_to_many or self.is_many_to_many)



class Persistence(type):
    """
    Application class metaclass.

    Programmer defines application classes with the metaclass. The
    class is assigned to the database relation. Class name is used as
    relation name, by default.

    @ivar relation: Database relation name.
    @ivar columns: List of application class attribute descriptions.
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

        c = type.__new__(self, name, bases, data)

        if __debug__:
            log.debug('new class "%s" for relation "%s"' % (c.__name__, data['relation']))

        assert c.relation, 'class relation should not be empty' # fixme: MappingError

        return c


    def addColumn(self, attr, col = None, vcls = None, link = None, vcol = None, vattr = None):
        """
        Add attribute description to persistent application class.

        This way the application class attributes and relationships between
        application classes are defined.

        @ivar attr: Application class attribute name.
        @ivar col: Relation column name (equal to @C{attr} by default).
        @ivar vcls: Class of referenced object(s).
        @ivar link:  Many-to-many link relation name.
        @ivar vcol: Relation column name of referenced object(s).
        @ivar vattr: Attribute name of referenced object(s). 

        @see: bazaar.conf.Column
        """
        if attr in self.columns:
            raise ValueError('column "%s" is already defined in class "%s"' % (attr, self.__name__))
            # fixme: MappingError

        col = Column(attr, col)
        col.vcls = vcls
        col.link = link
        col.vcol = vcol
        col.vattr = vattr

        self.delete_values = False

        self.columns[col.attr] = col

        if __debug__: log.debug('column "%s" is added to class "%s"' % (attr, self.__name__))
