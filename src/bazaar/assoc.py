# $Id: assoc.py,v 1.6 2003/09/19 14:59:48 wrobell Exp $
"""
Association classes.
"""

import logging

log = logging.getLogger('bazaar.assoc')

class AssociationReferenceProxy(dict):
    """
    Association reference proxy abstract class for application objects. 

    Reference proxy allows to get (upon foreign key value of associating
    object's column) and set (upon primary key value of associated object),
    reference of associated object.

    There should be one reference proxy object per association between
    application classes.
    
    It is allowed to set reference of:
        - associated object with primary key
        - associated object without primary key (object is not completed nor
          stored in database)
        - None (NULL) value

    When associated object has no primary key, then reference proxy buffers
    the object as value. Objects are buffered with buffer key, which is
    defined by descendants of this class (see L{getForeignKey} and
    L{setForeignKey} methods). The buffer key value should be unique in
    space of all objects of associating class, i.e. for one-to-one
    association buffer key can be associating object or for one-to-many
    buffer key can be tuple of associating object and object's position in
    the list of associated objects.

    Application class column defines the name of foreign key column and
    associated application class.

    @ivar column: Associating application class column.
    @ivar broker: Broker of associated application class.

    @see: L{bazaar.conf.Persistence} L{bazaar.conf.Column}
    """
    def __init__(self, column):
        """
        Initialize association reference proxy.

        Application broker is not initialized with the constructor, but is
        set when Bazaar layer is started up.

        @param column: Associating application class column.

        @see: L{bazaar.core.Bazaar.__init__} L{bazaar.conf.Persistence}
            L{bazaar.conf.Column}
        """
        super(AssociationReferenceProxy, self).__init__()
        self.column = column
        self.broker = None


    def __getitem__(self, buffer_key):
        """
        Return reference of associated object.

        Foreign key value of associating object's column is extracted with 
        L{getForeignKey} method.

        @param buffer_key: Buffer key value.

        @see: L{getForeignKey}
        """
        assert self.broker is not None

        # if the associated object have had no primary key, then return
        # object from reference buffer, otherwise get associated object
        # with broker
        if dict.has_key(self, buffer_key):
            return dict.__getitem__(self, buffer_key)
        else:
            value_key = self.getForeignKey(buffer_key)
            if value_key is None:
                return None
            else:
                return self.broker.get(value_key)


    def __setitem__(self, buffer_key, value):
        """
        Set reference of associated object.

        Foreign key value of associating object's column is set with 
        L{setForeignKey} method.

        @param buffer_key: Buffer key value.
        @param value: Associated object.

        @see: L{setForeignKey}
        """
        # remove entry from reference buffer if it exists
        if dict.has_key(self, buffer_key):
            del self[buffer_key]

        # if value is NULL/None or value's primary key is NULL/None
        # then set associating object's column foreign key value to None
        fk_value = None

        if value is not None:
            if value.key is None:
                # associated object's primary key is not defined,
                # store object in reference buffer
                dict.__setitem__(self, buffer_key, value)
            else:
                # set associating object's column foreign key value
                # to associated object primary key
                fk_value = value.key

        # set foreign key value
        self.setForeignKey(buffer_key, fk_value)


    def getForeignKey(self, buffer_key):
        """
        Abstract method to get foreign key value of associating
        object's column.

        @param buffer_key: Buffer key value.
        """
        raise NotImplementedError


    def setForeignKey(self, buffer_key, value_key):
        """
        Abstract method to set foreign key value of associating
        object's column with associated object's primary key.

        @param buffer_key: Buffer key value.
        @param value_key: Associated object's primary key value.
        """
        raise NotImplementedError



class OneToOneAssociation(AssociationReferenceProxy):
    """
    Base descriptor class for uni and bi-directional one to one association
    descriptors.

    @see: L{bazaar.assoc.AssociationReferenceProxy}
    @see: L{bazaar.assoc.UniDirOneToOneAssociation}
    @see: L{bazaar.assoc.BiDirOneToOneAssociation}
    """

    def __get__(self, obj, cls):
        """
        Descriptor method to get reference of associated object.

        @param obj: Associating object.
        @param cls: Associating class.

        @return: Returns associated object when C{obj} is not null,
            else descriptor object is returned.
        """
        if obj:
            return self[obj]
        else:
            return self


    def getForeignKey(self, buffer_key):
        """
        Return foreign key value of associating object's column.

        @param buffer_key: Buffer key value, which is associating object.
        """
        return getattr(buffer_key, self.column.name)


    def setForeignKey(self, buffer_key, value_key):
        """
        Set foreign key value of associating object's column to primary key
        of associated object.

        @param buffer_key: Buffer key value, which is associating object.
        @param value_key: Associated object's primary key value.
        """
        setattr(buffer_key, self.column.name, value_key)



class UniDirOneToOneAssociation(OneToOneAssociation):
    """
    Uni-directional one-to-one association descriptor.
    """
    def __set__(self, obj, value):
        """
        Descriptor method to set associating object's column value.

        This method is optimized for uni-directional one-to-one
        associations.

        @param obj: Associating object.
        @param value: Associated object.
        """
        self[obj] = value



class BiDirOneToOneAssociation(OneToOneAssociation):
    """
    Bi-directional one-to-one association descriptor.
    """
    def __set__(self, obj, value):
        """
        Descriptor method to set associating object's column value.

        The method keeps data integrity of bi-directional one-to-one
        associations.

        @param obj: Associating object.
        @param value: Associated object.
        """
        self[obj] = value
        self.column.association[value] = obj
