# $Id: assoc.py,v 1.19 2003/09/25 12:50:55 wrobell Exp $
"""
Association classes.
"""

import sets
import itertools

import logging

log = logging.getLogger('bazaar.assoc')



def juggle(obj, value, app, rem):
    """
    Dictionaries C{app} and C{rem} contain sets of referenced objects
    indexed by application objects C{obj}.

    Function appends referenced object C{value} to set C{app[obj]} and
    removes it from C{rem[obj]}. If set C{rem[obj]} contains no values, then
    it is deleted.
    """
    if obj in rem:
        objects = rem[obj]
        if value in objects:
            del objects[value]
        if len(objects) == 0:
            del rem[obj]

    if obj not in app:
        app[obj] = sets.Set()
    app[obj].add(value)

    assert value in app[obj]
    assert obj not in rem or value not in rem[obj]



class ReferenceBuffer(dict):
    """
    Simple reference buffer class.

    The class is used to save referenced objects, which has no primary key
    value.

    It is dictionary with application objects as keys and referenced
    objects as values.
    @see: l{bazaar.assoc.ListReferenceBuffer}
    """
    def __contains__(self, (obj, value)):
        """
        Check if application object is stored in reference buffer.

        @param obj: Application object.
        @param value: Referenced object.

        @return: Returns true if C{obj} is in reference buffer.
        """
        return super(ReferenceBuffer, self).__contains__(obj)


    def __delitem__(self, (obj, value)):
        """
        Remove application object from reference buffer. 
        """
        super(ReferenceBuffer, self).__delitem__(obj)



class ListReferenceBuffer(ReferenceBuffer):
    """
    Reference buffer for set of objects.

    It is dictionary with application objects as keys and set of referenced
    objects as value.

    @see: L{bazaar.assoc.ReferenceBuffer}
    """
    def __contains__(self, (obj, value)):
        """
        Check if application object referenced objects are in reference
        buffer.

        @param obj: Application object.
        @param value: Referenced object.
        """
        return super(ListReferenceBuffer, self).__contains__((obj, value)) and value in self[obj]


    def __setitem__(self, obj, value):
        """
        Add referenced object to the aplication object's set of referenced
        objects.

        The set is created if it does not exist.

        @param obj: Application object.
        @param value: Referenced object.
        """
        assert obj is not None and value is not None

        ref_buf = super(ListReferenceBuffer, self)
        if ref_buf.__contains__((obj, value)):
            obj_set = ref_buf.__getitem__(obj)
        else:
            obj_set = sets.Set()
            ref_buf.__setitem__(obj, obj_set)

        assert isinstance(obj_set, sets.Set)

        obj_set.add(value)


    def __delitem__(self, (obj, value)):
        """
        Remove referenced object from application object's set of
        referenced objects.

        If the set contains no more referenced objects, it is removed from
        dictionary.

        @param obj: Application object.
        @param value: Referenced object.
        """
        assert obj is not None and value is not None

        ref_buf = ListReferenceBuffer(self)
        if obj in ref_buf:
            ref_buf[obj].discard(value)
            if len(ref_buf[obj]) == 0:
                del ref_buf[obj]

        assert obj not in ref_buf or obj in ref_buf and len(ref_buf[obj]) > 0 and value not in ref_buf[obj]



class ObjectIterator(object):
    """
    Iterator of referenced objects.
    """

    def __init__(self, obj, association):
        """
        Create iterator of reference objects.

        The iterator is used to append, remove and update referenced
        objects, which are associated with application object.

        For example, to print article of order items::

            for oi in order.items:
                print oi.article


        @param obj: Application object.
        @param association: One-to-many or many-to-many association object.
        """
        object.__init__(self)
        self.obj = obj
        self.association = association
        assert isinstance(association, List)


    def __iter__(self):
        """
        Iterate all referenced objects.

        @return: Iterator of all referenced objects.
        """
        return self.association.iterAllObjects(obj)


    def append(self, value):
        """
        Associate referenced object with application object.

        Referenced object cannot be C{None}.

        @param value: Referenced object.
        """
        assert value is not None  # fixme: AssociationError
        self.association.append(self.obj, value)


    def remove(self, value):
        """
        Remove referenced object from association.

        Referenced object cannot be C{None}.

        @param value: Referenced object.
        """
        assert value is not None  # fixme: AssociationError
        self.association.remove(self.obj, value)


    def update(self):
        """
        Update association data for application object.
        """
        self.association.update(self.obj)


    def __len__(self):
        """
        Return amount of referenced objects.
        """
        return self.association.len(self.obj)



class AssociationReferenceProxy(object):
    """
    Association reference proxy abstract class for application objects. 

    Reference proxy allows to get (upon foreign key value of object's column)
    and set (upon primary key value of referenced object) reference to
    other application object.

    There should be one reference proxy object per association between
    application classes.
    
    It is allowed to set reference to:
        - application object with primary key
        - application object without primary key (object is not completed nor
          stored in database)
        - None (NULL) value

    When referenced object has no primary key, then reference proxy buffers
    the object as value with reference buffer.

    Application class attribute C{col} defines parameters of association.

    @ivar col: Application object's class attribute.
    @ivar broker: Broker of application class.
    @ivar vbroker: Broker of referenced application objects' class.
    @ivar association: Referenced class' association object of bi-directional association.

    @see: L{bazaar.assoc.ReferenceBuffer} L{bazaar.assoc.ListReferenceBuffer}
        L{bazaar.conf.Persistence} L{bazaar.conf.Column}
    """
    def __init__(self, col, ref_buf = None):
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
        if ref_buf is None:
            self.ref_buf = ReferenceBuffer()
        else:
            self.ref_buf = ref_buf


    def save(self, obj, value):
        """
        Assign referenced object.

        If primary key value of referenced object is not defined, then it
        is stored in reference buffer, otherwise it's set with L{saveForeignKey}
        method.

        @param obj: Application object.
        @param value: Referenced object.

        @see: L{saveForeignKey} L{bazaar.assoc.ReferenceBuffer}
            L{bazaar.assoc.ListReferenceBuffer}
        """
        # remove entry from reference buffer if it exists
        if (obj, value) in self.ref_buf:
            del self.ref_buf[obj, value]

        # if value is NULL/None or value's primary key is NULL/None
        # then set referenced object's column foreign key value to None
        vkey = None

        if value is not None:
            if value.__key__ is None:
                # refernced object's primary key is not defined,
                # store object in reference buffer
                self.ref_buf[obj] = value
            else:
                # set referenced object's column foreign key value
                # to referenced object's primary key
                vkey = value.__key__

        # store foreign key value
        self.saveForeignKey(obj, vkey)


    def saveForeignKey(self, obj, vkey):
        """
        Abstract method to save referenced object's primary key value.

        @param obj: Application object.
        @param vkey: Referenced object primary key value.
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

        @return: Referenced object when C{obj} is not null, otherwise descriptor object.
        """
        if obj:
            if (obj, None) in self.ref_buf:
                return self.ref_buf[obj]
            else:
                return self.vbroker.get(getattr(obj, self.col.col))
        else:
            return self


    def saveForeignKey(self, obj, vkey):
        """
        Save referenced object's primary key value.

        Application object's foreign key value is set to referenced
        object's primary key value.

        @param obj: Application object.
        @param vkey: Referenced object primary key value.
        """
        setattr(obj, self.col.col, vkey)


    def __set__(self, obj, value):
        """
        Descriptor method to set application object's attribute and foreign
        key values.

        This method is optimized for uni-directional one-to-one association.

        @param obj: Application object.
        @param value: Referenced object.
        """
        assert value is None or isinstance(value, self.col.vcls), '%s != %s' % (value.__class__, self.col.vcls) # fixme: AssociationError
        assert obj is not None
        self.save(obj, value)



class BiDirOneToOne(OneToOne):
    """
    Bi-directional one-to-one association descriptor.
    """
    def __set__(self, obj, value):
        """
        Descriptor method to set application object's attribute and foreign
        key values.

        The method keeps data integrity of bi-directional one-to-one
        association.

        @param obj: Application object.
        @param value: Referenced object.
        """
        old_val = getattr(obj, self.col.attr)
        super(BiDirOneToOne, self).__set__(obj, value)

        if value is None:
            if old_val is not None:
                self.association.integrateRemove(old_val, obj)
        else:
            self.association.integrateSave(value, obj)


    def integrateSave(self, obj, value):
        """
        Keep bi-directional association data integrity when setting
        reference is performed.

        Application and referenced objects cannot be C{None}.

        Method is called by second association object from bi-directional
        relationship.
        
        Application object is referenced object in second association
        object.

        @param obj: Application object.
        @param value: Referenced object.
        """
        assert obj is not None and value is not None
        self.save(obj, value)


    def integrateRemove(self, obj, value):
        """
        Keep bi-directional association data integrity when removal
        of reference is performed.

        Application and referenced objects cannot be C{None}.

        Method is called by second association object from bi-directional
        relationship.
        
        Application object is referenced object in second association
        object.

        @param obj: Application object.
        @param value: Referenced object.
        """
        assert obj is not None and value is not None
        self.save(obj, None)



class List(AssociationReferenceProxy):
    """
    Basic descriptor for one-to-many and many-to-many associations.

    @ivar value_keys: Sets of referenced objects's primary key values per application object.
    @ivar reload: If true, then association data will be loaded from
        database.
    @ivar appended: Sets of referenced objects appended to association.
    @ivar removed: Sets of referenced objects removed from association.

    @todo: Referenced objects' primary key values and referenced objects with
    undefinded primary key values are stored with sets internally.
    Sets are good where list of referenced objects is long enough.
    Consider the script::

        #!/bin/sh
        echo amount: $1
        echo lists:
        python /usr/lib/python2.3/timeit.pyo -s "amount = $1; x = range(amount)" -n 10000 "amount in x"
        echo sets:
        python /usr/lib/python2.3/timeit.pyo -s "import sets; amount = $1; x = sets.Set(range(amount))" -n 10000 "amount in x"


    Test results::

        amount: 10
        lists: 10000 loops, best of 3: 5.4 usec per loop
        sets:  10000 loops, best of 3: 17.4 usec per loop

        amount: 25
        lists: 10000 loops, best of 3: 11.5 usec per loop
        sets:  10000 loops, best of 3: 17.9 usec per loop

        amount: 50
        lists: 10000 loops, best of 3: 21.8 usec per loop
        sets:  10000 loops, best of 3: 17.5 usec per loop

        amount: 100
        lists: 10000 loops, best of 3: 42.7 usec per loop
        sets:  10000 loops, best of 3: 17.3 usec per loop


    Creating set costs more comparing to creating list::

        $ timeit -s 'from sets import Set' -n 100000 'x = Set()'
        100000 loops, best of 3: 21.5 usec per loop

        $ timeit -s 'from sets import Set' -n 100000 'x = list()'
        100000 loops, best of 3: 4.5 usec per loop

    Conclusion. Store referenced objects with lists internally by
    default and make configuration option, so switching to sets is
    possible.
    """
    def __init__(self, col):
        """
        Create descriptor for one-to-many and one-to-one associations.

        @param col: Referenced application object's class column.

        @see: L{bazaar.assoc.AssociationReferenceProxy.__init__}
            L{bazaar.core.Bazaar.__init__} L{bazaar.conf.Persistence}
            L{bazaar.conf.Column}
        """
        super(List, self).__init__(col, ListReferenceBuffer())
        self.value_keys = {}
        self.appended = {}
        self.removed = {}
        self.reload = True
        assert isinstance(self.ref_buf, ListReferenceBuffer)


    def saveForeignKey(self, obj, vkey):
        """
        Save referenced object's primary key value.

        Primary key value is appended to the set of referenced objects'
        primary key values.

        @param obj: Application object.
        @param vkey: Referenced object's primary key value.
        """
        self.getValueKeys(obj).add(vkey)


    def __get__(self, obj, cls):
        """
        Descriptor method to get iterator of referenced objects.

        For example, to get list of all referenced objects
        by order C{ord} (items is the descriptor)::

            order_item_list = [ord.items]


        @param obj: Application object.
        @param cls: Application class.

        @return: Iterator of referenced objects, when C{obj} is not null,
            otherwise descriptor object.

        @see: L{bazaar.assoc.ObjectIterator}
        """
        if obj:
            if self.reload:
                self.loadData()
            return ObjectIterator(obj, self)   
        else:
            return self


    def __set__(self, obj, value):
        """
        Assigning list of referenced objects is not implemented yet.
        """
        raise NotImplementedError


    def getValueKeys(self, obj):
        """
        Get referenced objects' primary key values set.

        If the set does not exist, then it will be created.

        @param obj: Application object.
        """
        assert obj is not None

        # if set of referenced objects does not exist, then create it
        if obj not in self.value_keys:
            self.value_keys[obj] = sets.Set()
        return self.value_keys[obj]


    def reloadData(self, now = False):
        """
        Request reloading association relational data.

        Association data are removed from memory. If C{now} is set to true, then
        relationship data are loaded from database immediately.

        @param now: Reload relationship data immediately.
        """
        self.reload = True
        self.value_keys.clear()
        self.appended.clear()
        self.removed.clear()
        if now:
            self.loadData()



    def loadData(self):
        """
        Load association data from database.
        """
        log.info('load association %s.%s' % (self.broker.cls, self.col.attr))

        assert len(self.value_keys) == 0 and len(self.appended) ==0 and len(self.removed) == 0

        for okey, vkey in self.broker.convertor.getPair(self.col):
            obj = self.broker.get(okey)
            if obj is not None:
                self.getValueKeys(obj).add(vkey)

        log.info('len(%s.%s) = %d' % (self.broker.cls, self.col.attr, len(self.value_keys)))

        self.reload = False


    def iterObjects(self, obj):
        """
        Return iterator of all referenced objects by application object.

        @param obj: Application object.

        @return: Iterator of all referenced objects.
        """
        # return all objects with defined primary key values
        def getObjects():
            if obj in self.value_keys:
                for vkey in self.value_keys[obj]:
                    yield self.vbroker.get(vkey)

        if obj in self.ref_buf:
            # return all objects
            return itertools.chain(getObjects(), self.ref_buf[obj])
        else:
            # no objects with undefined primary key value
            return getObjects()


    def update(self, obj):
        """
        Update relational data of association of given application object
        in database.

        @param obj: Application object.
        fixme: nfy
        """
        okey = obj.__key__

        def equalize(set, method):
            if obj in set:
                for value in set[obj]:
                    method(self.col, okey, value.__key__)
                set.clear()
#        equalize(sel.removed, self.broker.convertor.delAssociationPair)
        equalize(self.appended, self.broker.convertor.addPair)


    def append(self, obj, value):
        """
        Append referenced object to association.

        @param obj: Application object.
        @param value: Referenced object.
        """
        self.save(obj, value)
        juggle(obj, value, self.appended, self.removed)


    def remove(self, obj, value):
        """
        Remove referenced object from association.

        @param obj: Application object.
        @param value: Referenced object.
        """
        assert obj in self.value_keys

        juggle(obj, value, self.removed, self.appended)

        if (obj, value) in self.ref_buf:
            del self.ref_buf[(obj, value)]
        elif obj in self.value_keys:
            self.value_keys.discard(value.__key__)


    def len(self, obj):
        """
        Return amount of all referenced objects by application object.
        """
        size = 0
        if obj in self.value_keys:            # amount of objects with defined primary key value
            size += len(self.value_keys[obj])
        if (obj, None) in self.ref_buf:       # amount of objects with undefined primary key value
            size += len(self.ref_buf[obj])
        return size



class BiDirList(List):
    """
    Bi-directional one-to-many association descriptor.

    One-to-many association is always bi-directional relationship.
    """
    def append(self, obj, value):
        """
        Append referenced object to association and integrate association
        data.

        @param obj: Application object.
        @param value: Referenced object.
        """
        assert value is not None
        super(BiDirList, self).append(obj, value)
        self.association.integrateSave(value, obj)


    def remove(self, obj, value):
        """
        Remove referenced object from association and integrate association
        data.

        @param obj: Application object.
        @param value: Referenced object.
        """
        super(BiDirList, self).remove(obj, value)
        self.association.integrateRemove(value, obj)


    def integrateSave(self, obj, value):
        """
        Integrate association data when referenced object is appended to
        association.
        """
        assert obj is not None and value is not None
        super(BiDirList, self).append(obj, value)


    def integrateRemove(self, obj, value):
        """
        Integrate association data when referenced object is removed from
        association.

        @param obj: Application object.
        @param value: Referenced object.
        """
        assert obj is not None and value is not None
        super(BiDirList, self).remove(obj, value)
