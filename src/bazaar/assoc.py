# $Id: assoc.py,v 1.11 2003/09/22 22:59:45 wrobell Exp $
"""
Association classes.
"""

import logging

log = logging.getLogger('bazaar.assoc')

class AssociationReferenceProxy(dict):
    """
    Association reference proxy abstract class for application objects. 

    Reference proxy allows to get (upon foreign key value of object's column)
    and set (upon primary key value of referenced object) reference to
    other object.

    There should be one reference proxy object per association between
    application classes.
    
    It is allowed to set reference to:
        - application object with primary key
        - application object without primary key (object is not completed nor
          stored in database)
        - None (NULL) value

    When referenced object has no primary key, then reference proxy buffers
    the object as value. Objects are buffered with buffer key, which is
    defined by descendants of this class (see L{getForeignKey} and
    L{setForeignKey} methods). The buffer key value should be unique in
    space of all referenced objects of given class, i.e. for one-to-one
    association buffer key can be referenced object itself and for one-to-many
    buffer key can be tuple of object and referenced object's position in
    the list of objects.

    The class derives from C{dict} type, so setting and getting referenced object is
    performed with::

        ref_buffer[obj] = value
        value = ref_buffer[obj]

    Application class attribute C{col} defines parameters of association.

    @ivar col: Application object's class attribute.
    @ivar broker: Broker of application class.
    @ivar vbroker: Broker of referenced application objects' class.
    @ivar association: Referenced object's association object of
        bi-directional association.

    @see: L{bazaar.conf.Persistence} L{bazaar.conf.Column}
    """
    def __init__(self, col):
        """
        Create association reference proxy.

        Brokers are not initialized with the constructor. Instead, they are
        set when Bazaar layer is started up.

        @param col: Application object's class attribute.

        @see: L{bazaar.core.Bazaar.__init__} L{bazaar.conf.Persistence}
            L{bazaar.conf.Column}
        """
        super(AssociationReferenceProxy, self).__init__()
        self.col = col
        self.broker = None
        self.vbroker = None
        self.association = None


    def __getitem__(self, buffer_key):
        """
        Return referenced object.

        Foreign key value of referenced object's column is extracted with 
        L{getForeignKey} method.

        @param buffer_key: Buffer key value.

        @see: L{getForeignKey}
        """
        assert self.vbroker is not None

        # if the referenced object have had no primary key, then return
        # object from reference buffer, otherwise get referenced object
        # with broker
        if dict.has_key(self, buffer_key):
            return dict.__getitem__(self, buffer_key)
        else:
            value_key = self.getForeignKey(buffer_key)
            if value_key is None:
                return None
            else:
                return self.vbroker.get(value_key)
            # fixme: above five lines -> self.vbroker.get(self.getForeignKey(buffer_key))


    def __setitem__(self, buffer_key, value):
        """
        Assign referenced object.

        Foreign key value of referenced object's column is set with 
        L{setForeignKey} method.

        @param buffer_key: Buffer key value.
        @param value: Referenced object.

        @see: L{setForeignKey}
        """
        # remove entry from reference buffer if it exists
        if dict.has_key(self, buffer_key):
            del self[buffer_key]

        # if value is NULL/None or value's primary key is NULL/None
        # then set referenced object's column foreign key value to None
        fk_value = None

        if value is not None:
            if value.__key__ is None:
                # refernced object's primary key is not defined,
                # store object in reference buffer
                dict.__setitem__(self, buffer_key, value)
            else:
                # set referenced object's column foreign key value
                # to referenced object's primary key
                fk_value = value.__key__

        # set foreign key value
        self.setForeignKey(buffer_key, fk_value)


    def getForeignKey(self, buffer_key):
        """
        Abstract method to get foreign key value of referenced
        object's column.

        @param buffer_key: Buffer key value.
        """
        raise NotImplementedError


    def setForeignKey(self, buffer_key, value_key):
        """
        Abstract method to set foreign key value of referenced
        object's column to referenced object's primary key.

        @param buffer_key: Buffer key value.
        @param value_key: Associated object's primary key value.
        """
        raise NotImplementedError



class OneToOne(AssociationReferenceProxy):
    """
    Class for uni-directional one-to-one association descriptors.

    @see: L{bazaar.assoc.AssociationReferenceProxy}
    @see: L{bazaar.assoc.BiDirOneToOne}
    """

    def __get__(self, obj, cls):
        """
        Descriptor method to retrieve reference of referenced object for
        application object.

        @param obj: Application object.
        @param cls: Application class.

        @return: Returns referenced object when C{obj} is not null,
            otherwise descriptor object is returned.
        """
        if obj:
            return self[obj]
        else:
            return self


    def getForeignKey(self, buffer_key):
        """
        Return foreign key value of referenced object's column.

        @param buffer_key: Buffer key value, which is application object.
        """
        return getattr(buffer_key, self.col.col)


    def setForeignKey(self, buffer_key, value_key):
        """
        Set foreign key value of application object's column to
        referenced object's primary key.

        @param buffer_key: Buffer key value, which is application object.
        @param value_key: Referenced object's primary key value.
        """
        setattr(buffer_key, self.col.col, value_key)


    def __set__(self, obj, value):
        """
        Descriptor method to set application object's column value.

        This method is optimized for uni-directional one-to-one
        association.

        @param obj: Application object.
        @param value: Referenced object.
        """
        assert value is None or value.__class__ == self.col.vcls, '%s != %s' % (value.__class__, self.col.vcls)
        assert obj is not None
        self[obj] = value



class BiDirOneToOne(OneToOne):
    """
    Bi-directional one-to-one association descriptor.
    """
    def __set__(self, obj, value):
        """
        Descriptor method to set application object's column value.

        The method keeps data integrity of bi-directional one-to-one
        association.

        @param obj: Application object.
        @param value: Referenced object.
        """
        super(BiDirOneToOne, self).__set__(obj, value)
        self.association.integrate(value, obj)


    def integrate(self, obj, value):
        """
        Keep bi-directional association data integrity method.

        Method is called by second association object from bi-directional
        relationship.
        
        Application object is referenced object in second association
        object.

        @param obj: Application object.
        @param value: Referenced object.
        """
        if obj is not None:
            super(BiDirOneToOne, self).__set__(obj, value)



class ListAssociation(AssociationReferenceProxy):
    """
    Basic descriptor for one-to-many and many-to-many associations.

    @ivar obj_lists: Lists of referenced objects per application object.
    @ivar reload: If true, then association data will be loaded from
        database.
    """
    def __init__(self, col):
        """
        Create descriptor for one-to-many and one-to-one associations.

        @param col: Referenced application object's class column.

        @see: L{bazaar.assoc.AssociationReferenceProxy.__init__}
            L{bazaar.core.Bazaar.__init__} L{bazaar.conf.Persistence}
            L{bazaar.conf.Column}
        """
        super(ListAssociation, self).__init__(col)
        self.obj_lists = {}
        self.appended = {}
        self.removed = {}
        self.reload = True



    def getForeignKey(self, buffer_key):
        """
        Return foreign key value of referenced object's column.

        @param buffer_key: Buffer key value, which is pair of application
            object and index of referenced object in referenced object list.
        @return: Referenced object's primary key value.
        """
        assert len(buffer_key) == 2 and type(buffer_key[0]) == self.broker.cls
        # obj = buffer_key[0]
        # index = buffer_key[1]
        return list.__getitem__(self.obj_lists[buffer_key[0]], buffer_key[1])


    def setForeignKey(self, buffer_key, value_key):
        """
        Set foreign key value of application object's column to primary key
        of referenced object.

        @param buffer_key: Buffer key value, which is pair of application
            object and index of referenced object in object list.
        @param value_key: Referenced object's primary key value.
        """
        assert len(buffer_key) == 2 and type(buffer_key[0]) == self.broker.cls
        # obj = buffer_key[0]
        # index = buffer_key[1]
        list.__setitem__(self.obj_lists[buffer_key[0]], buffer_key[1], value_key)


    def __get__(self, obj, cls):
        """
        Descriptor method to get list of referenced objects.

        For example, (items is the descriptor)::

            order_item_list = order.items

        @param obj: Application object.
        @param cls: Application class.

        @return: Returns list of referenced objects, when C{obj} is not null,
            otherwise descriptor object is returned.
        """
        if obj:

            if self.reload:
                self.loadAll()

            if obj not in self.obj_lists:
                self.obj_lists[obj] = ObjectList(obj, self)

            return self.obj_lists[obj]
        else:
            return self


    def __set__(self, obj, value):
        """
        Assigning list of referenced objects is not implemented yet.
        """
        raise NotImplementedError


    def add(self, obj, index, value):
        """
        Add referenced object to application object's list of referenced
        objects.

        @param obj: Application object.
        @param index: Index of the referenced object in the list of
            referenced objects.
        @param value: Referenced object.
        """
        self[(obj, index)] = value


    def getList(self, obj):
        """
        Append referenced object to application object's list of referenced
        objects.

        @param obj: Application object.
        @param value: Referenced object.
        """
        assert obj is not None
        if obj not in self.obj_lists:    # if list of referenced objects does not exist, then create it
            self.obj_lists[obj] = ObjectList(obj, self)
        return self.obj_lists[obj]


    def reload(self, now):
        """
        Request reloading association relational data.

        Association data are removed from memory. If C{now} is set to true, then
        relationship data are loaded from database immediately.

        @param now: Reload relationship data immediately.
        """
        self.reload = True
        self.obj_lists.clear()
        self.appended.clear()
        self.removed.clear()
        if now:
            self.loadAll()


    def loadAll(self):
        """
        Load association data from database.
        """
        log.info('load association %s.%s' % (self.broker.cls, self.col.attr))
        for okey, vkey in self.broker.convertor.getPair(self.col):
            obj = self.broker.get(okey)
            if obj is not None:
                value = self.vbroker.get(vkey)
                list.append(self.getList(obj), vkey)

        log.info('len(%s.%s) = %d' % (self.broker.cls, self.col.attr, len(self.obj_lists)))

        self.reload = False


    def update(self, obj_list):
        """
        Update association data of given list of referenced objects in
        database.

        fixme: nfy
        """
        obj = obj_list.obj
        okey = obj.__key__

        def equalize(set, method):
            if obj in set:
                for value in set[obj]:
                    method(self.col, okey, value.__key__)
                set.clear()
#        equalize(sel.removed, self.broker.convertor.delAssociationPair)
        equalize(self.appended, self.broker.convertor.addPair)


    def juggle(self, obj, value, app, rem):
        if obj in rem:
            objects = rem[obj]
            if value in objects:
                del objects[value]
            if len(objects) == 0:
                del rem[obj]

        if obj not in app:
            app[obj] = sets.Set()
        app[obj].add(value)


    def append(self, obj, index, value):
        self.add(obj, index, value)
        self.juggle(obj, value, self.appended, self.removed)
        assert value in self.appended[obj]
        assert obj not in self.removed or value not in self.removed[obj]

    def remove(self, obj, index, value):
        if (obj, index) in self: del self[(obj, index)]
        self.juggle(obj, value, self.removed, self.appended)
        assert value in self.removed[obj]
        assert obj not in self.appended or value not in self.appended[obj]




class UniDirManyToMany(ListAssociation):
    """
    Uni-directional many-to-many association.
    """
    pass


import sets
class OneToMany(ListAssociation):
    """
    Bi-directional one-to-many association descriptor.

    One-to-many association is always bi-directional relationship.
    """
    def add(self, obj, index, value):
        super(OneToMany, self).add(obj, index, value)
        self.association.integrate(value, obj)


    def integrate(self, obj, value):
        if obj is None:
            self.remove(obj, value)
        else:
            self.getList(obj).append(value)


class ObjectList(list):
    def __init__(self, obj, association):
        list.__init__(self)
        self.obj = obj
        self.association = association


    def __getitem__(self, item):
        return self.get(item)


    def __setitem__(self, index, value):
        raise NotImplementedError
        #self.set(index, value)


    def __delitem__(self, index):
        self.association.remove(self.obj, index, value)


    def append(self, value):
        assert value is None or self.association.col.vcls == value.__class__
        index = len(self)
        list.append(self, None)
        self.association.append(self.obj, index, value)


    def __iter__(self):
        for i in range(len(self)):
            yield self.get(i)


    def __str__(self):
        return str([val for val in self])


    def set(self, index, value):
        self.association.add(self.obj, index, value)


    def get(self, index):
        return self.association[(self.obj, index)]


    def update(self):
        self.association.update(self)
