# $Id: assoc.py,v 1.43 2003/11/26 02:34:31 wrobell Exp $
"""
Association classes.
"""

import sets
import itertools
import weakref

import logging

import bazaar.exc

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
        objects.discard(value)
        if len(objects) == 0:
            del rem[obj]

    if obj not in app:
        app[obj] = sets.Set()
    app[obj].add(value)

    assert value in app[obj]
    assert obj not in rem or value not in rem[obj]



class ObjectIterator(object):
    """
    Iterator of referenced objects.

    The iterator is used to append, remove and update referenced
    objects, which are associated with application object.

    For example, to print article of order items::

        items = order.items
        for oi in items:
            print oi.article

    Several operators are supported
        - len: C{len(items)}
        - in: C{oi in items}
        - del: C{del items[oi]}

    @ivar association: Association object.
    @ivar obj: Application object.

    @see: L{AssociationReferenceProxy}
    """

    def __init__(self, obj, association):
        """
        Create iterator of reference objects.


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
        return self.association.iterObjects(self.obj)


    def append(self, value):
        """
        Associate referenced object with application object.

        Referenced object cannot be C{None}.

        @param value: Referenced object.
        """
        if value is None:
            raise bazaar.exc.AssociationError('referenced object cannot be null', \
                self.association, self.obj, value)

        if not isinstance(value, self.association.col.vcls):
            raise bazaar.exc.AssociationError('referenced object\'s class mismatch', self.association, self.obj, value)

        if self.association.contains(self.obj, value):
            raise bazaar.exc.AssociationError('object is referenced', self.association, self.obj, value)

        self.association.append(self.obj, value)


    def update(self):
        """
        Update association data for application object.
        """
        self.association.update(self.obj)


    def remove(self, value):
        """
        Remove referenced object from association.

        Referenced object cannot be C{None}.

        @param value: Referenced object.
        """
        if value is None:
            raise bazaar.exc.AssociationError('referenced object cannot be null', \
                self.association, self.obj, value)

        if not isinstance(value, self.association.col.vcls):
            raise bazaar.exc.AssociationError('referenced object\'s class mismatch', self.association, self.obj, value)

        if not self.association.contains(self.obj, value):
            raise bazaar.exc.AssociationError('object is not referenced', self.association, self.obj, value)

        self.association.remove(self.obj, value)


    __delitem__ = remove


    def __len__(self):
        """
        Return amount of referenced objects.
        """
        return self.association.len(self.obj)


    def __contains__(self, value):
        """
        Check if object is referenced in the relationship.

        @param value: Object to check.

        @return: True if object is referenced.
        """
        if value is None:
            return False
        else:
            return self.association.contains(self.obj, value)



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

    @see: L{bazaar.cache.ReferenceBuffer} L{bazaar.cache.ListReferenceBuffer}
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
            self.ref_buf = bazaar.cache.ReferenceBuffer()
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

        @see: L{saveForeignKey} L{bazaar.cache.ReferenceBuffer}
            L{bazaar.cache.ListReferenceBuffer}
        """
        assert obj is not None and value is not None

        if value.__key__ is None:
            # refernced object's primary key is not defined,
            # store object in reference buffer
            self.ref_buf[obj] = value
        else:
            # remove entry from reference buffer if it exists
            if (obj, value) in self.ref_buf:
                del self.ref_buf[obj, value]
        self.saveForeignKey(obj, value.__key__)


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
            if obj in self.ref_buf:
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
        assert obj is not None

        if not (value is None or isinstance(value, self.col.vcls)):
            raise bazaar.exc.AssociationError('referenced object\'s class mismatch', obj, value)

        if value is None:
            self.saveForeignKey(obj, None)
        else:
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

        if (obj, value) in self.ref_buf:
            del self.ref_buf[(obj, value)]
            # obj is in ref_buf so getattr(obj, self.col.col) is None
        else:
            self.saveForeignKey(obj, None)

        assert getattr(obj, self.col.col) is None



class List(AssociationReferenceProxy):
    """
    Basic descriptor for one-to-many and many-to-many associations.

    @ivar cache: Association data cache - sets of referenced objects's
                 primary key values per application object.
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
    possible or always use sets so system is scalable.
    """
    def __init__(self, col):
        """
        Create descriptor for one-to-many and one-to-one associations.

        @param col: Referenced application object's class column.

        @see: L{bazaar.assoc.AssociationReferenceProxy.__init__}
            L{bazaar.core.Bazaar.__init__} L{bazaar.conf.Persistence}
            L{bazaar.conf.Column}
        """
        super(List, self).__init__(col, bazaar.cache.ListReferenceBuffer())
        self.cache = self.col.cache(self)
        self.appended = weakref.WeakKeyDictionary()
        self.removed = weakref.WeakKeyDictionary()
        self.reload = True
        assert isinstance(self.ref_buf, bazaar.cache.ListReferenceBuffer)


    def saveForeignKey(self, obj, vkey):
        """
        Save referenced object's primary key value.

        Primary key value is appended to the set of referenced objects'
        primary key values.

        @param obj: Application object.
        @param vkey: Referenced object's primary key value.
        """
        if vkey is not None:
            self.cache[obj].add(vkey)


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
            return ObjectIterator(obj, self)   
        else:
            return self


    def __set__(self, obj, value):
        """
        Assigning list of referenced objects is not implemented yet.
        """
        raise NotImplementedError


    def reloadData(self, now = False):
        """
        Request reloading association relational data.

        Association data are removed from memory. If C{now} is set to true, then
        relationship data are loaded from database immediately.

        @param now: Reload relationship data immediately.
        """
        self.reload = True
        self.cache.clear()
        self.ref_buf.clear()
        self.appended.clear()
        self.removed.clear()
        if now:
            self.loadData()



    def getAllKeys(self):
        """
        Return tuple of application object's and referenced object's
        primary key values.

        Referenced object's primary key value is taken from database with
        appropriate convertor methods.
        
        @see: L{getPairFromBroker} L{bazaar.motor.Convertor.getPair}
        """
        for item in self.broker.convertor.getAllAscData(self):
            yield item


    def appendKey(self, okey, vkey):
        """
        Append referenced object relational data to association data.

        @param okey: Application object's primary key value.
        @param vkey: Referenced object's primary key value.
        """
        obj = self.broker.get(okey)
        if obj not in self.cache:
            keys = sets.Set()
            self.cache[obj] = keys
        else:
            keys = self.cache.dicttype.__getitem__(self.cache, obj)
        assert isinstance(keys, sets.Set)
        keys.add(vkey)


    def loadData(self):
        """
        Load association data from database.

        @see: L{reloadData} L{getPair} L{appendKey}
        """
        log.info('load association %s.%s' % (self.broker.cls, self.col.attr))

        assert len(self.cache) == 0 and len(self.appended) == 0 \
            and len(self.removed) == 0

        for okey, vkey in self.getAllKeys():
            self.appendKey(okey, vkey)

        log.info('application objects of %s.%s = %d' % \
            (self.broker.cls, self.col.attr, len(self.cache)))

        self.reload = False


    def iterObjects(self, obj):
        """
        Return iterator of all referenced objects by application object.

        @param obj: Application object.

        @return: Iterator of all referenced objects.
        """
        # return all objects with defined primary key values
        def getObjects():
            for vkey in list(self.cache[obj]):
                yield self.vbroker.get(vkey)
        

        assert None not in getObjects(), '%s.%s -> %s.%s (obj: %s) iterated objects: %s' % \
            (self.broker.cls, self.col.attr, self.col.vcls, self.col.col, obj, list(getObjects()))

        if obj in self.ref_buf:
            # return all objects
            return itertools.chain(getObjects(), self.ref_buf[obj])
        else:
            # no objects with undefined primary key value
            return getObjects()


    def delPair(self, pairs):
        """
        Remove pair of application object's and referenced object's primary
        key values from m-n relationship's database link relation.

        @see: L{addPairWithDB} L{update}
        """
        self.broker.convertor.delPair(self, pairs)


    def addPair(self, pairs):
        """
        Add pair of application object's and referenced object's primary
        key values into m-n relationship's database link relation.

        @see: L{delPairWithDB} L{update}
        """
        self.broker.convertor.addPair(self, pairs)


    def updateablePair(self, obj, value):
        """
        Return pair of application object's and referenced object's primary
        key values.

        @see: L{update}
        """
        return obj.__key__, value.__key__


    def update(self, obj):
        """
        Update relational data of association of given application object
        in database.

        @param obj: Application object.

        @see: L{updateReferencedObjects} L{addReferencedObjects} L{delReferencedObjects}
            L{addPairWithDB} L{delPairWithDB} L{getObjectPair} L{getKeyPair}
        """
        def getPairs(set):
            if obj in set:
                for value in set[obj]:
                    yield self.updateablePair(obj, value)
                set[obj].clear()

        self.delPair(getPairs(self.removed))
        self.addPair(getPairs(self.appended))


    def append(self, obj, value):
        """
        Append referenced object to association.

        @param obj: Application object.
        @param value: Referenced object.
        """
        juggle(obj, value, self.appended, self.removed)
        self.save(obj, value)


    def justRemove(self, obj, value):
        """
        Remove referenced object from association.

        @param obj: Application object.
        @param value: Referenced object.
        """
        if (obj, value) in self.ref_buf:
            del self.ref_buf[(obj, value)]
        else:
            self.cache[obj].discard(value.__key__)


    def remove(self, obj, value):
        """
        Remove referenced object from association and update information
        about data removal.

        @param obj: Application object.
        @param value: Referenced object.
        """
        #assert obj in self.cache
        juggle(obj, value, self.removed, self.appended)
        self.justRemove(obj, value)


    def len(self, obj):
        """
        Return amount of all referenced objects by application object.
        """
        size = 0
        size += len(self.cache[obj])  # amount of objects with defined primary key value
        if obj in self.ref_buf:       # amount of objects with undefined primary key value
            size += len(self.ref_buf[obj])
        return size


    def contains(self, obj, value):
        """
        Check if object is referenced by application object.

        @param obj: Application object.
        @param value: Object to check.

        @return: True if object is referenced by application object.
        """
        assert isinstance(obj, self.broker.cls)
        assert value is not None and isinstance(value, self.col.vcls)

        keys = self.cache[obj]
        if value.__key__ in keys:
            return True
        else:
            return (obj, value) in self.ref_buf



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
        assert value is not None and isinstance(self.association, AssociationReferenceProxy)
        super(BiDirList, self).append(obj, value)
        self.association.integrateSave(value, obj)


    def remove(self, obj, value):
        """
        Remove referenced object from association and integrate association
        data.

        @param obj: Application object.
        @param value: Referenced object.
        """
        assert isinstance(self.association, AssociationReferenceProxy)
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



class BiDirManyToMany(BiDirList):
    def appendKey(self, okey, vkey):
        """
        Append referenced object relational data to association data
        and update association data of referenced class.

        @param okey: Application object's primary key value.
        @param vkey: Referenced object's primary key value.
        """
        super(BiDirManyToMany, self).appendKey(okey, vkey)
        super(BiDirManyToMany, self.association).appendKey(okey, vkey)


    def loadData(self):
        """
        Load association data from database.

        @see: L{reloadData} L{getPair} L{appendKey}
        """
        super(BiDirManyToMany, self).loadData()
        self.association.reload = False


    def reloadData(self, now = False):
        """
        Request reloading association relational data. Referenced class'
        association data are reloaded, too.

        Association data are removed from memory. If C{now} is set to true, then
        relationship data are loaded from database immediately.

        @param now: Reload relationship data immediately.
        """
        super(BiDirManyToMany, self).reloadData(now)
        super(BiDirManyToMany, self.association).reloadData(False)



class OneToMany(BiDirList):
    def __init__(self, col):
        """
        Create descriptor for one-to-many associations.

        @param col: Referenced application object's class column.

        @see: L{bazaar.assoc.AssociationReferenceProxy.__init__}
        """
        super(OneToMany, self).__init__(col)
        if self.col.update:
            self.addPair = self.updateReferencedObjects
            self.delPair = self.updateReferencedObjects
        else:
            self.addPair = self.addReferencedObjects
            self.delPair = self.delReferencedObjects


    def append(self, obj, value):
        """
        Append referenced object to association and integrate association
        data.

        @param obj: Application object.
        @param value: Referenced object.
        """
        assert value is not None and isinstance(self.association, AssociationReferenceProxy)
        old_obj = getattr(value, self.col.vattr)
        if old_obj is not None:
            self.justRemove(old_obj, value)
        super(OneToMany, self).append(obj, value)


    def getAllKeys(self):
        """
        Return tuple of application object's and referenced object's
        primary key values.

        Referenced object is taken from referenced class broker.
        
        The method is used as C{List.getPair} method with one-to-many
        associations.
        """
        for value in self.vbroker.getObjects():
            yield getattr(value, self.col.vcol), value.__key__


    def reloadData(self, now = False):
        """
        Request reloading association relational data. Referenced objects
        are reloaded, too.

        Association data are removed from memory. If C{now} is set to true, then
        relationship data are loaded from database immediately.

        @param now: Reload relationship data immediately.
        """
        super(OneToMany, self).reloadData(now)
        self.vbroker.reloadObjects(False)


    def addReferencedObjects(self, pairs):
        """
        Add referenced objects into database.

        The method is used as C{addPair} method with one-to-many
        associations when updating relationship.

        @see: L{delReferencedObjects} L{updateReferencedObjects} L{update}
        """
        for obj, value in pairs:
            self.vbroker.add(value)


    def delReferencedObjects(self, pairs):
        """
        Delete referenced objects from database.

        The method is used as C{delPair} method with one-to-many
        associations when updating relationship.

        @see: L{addReferencedObjects} L{updateReferencedObjects} L{update}
        """
        for obj, value in pairs:
            self.vbroker.delete(value)


    def updateReferencedObjects(self, pairs):
        """
        Update referenced objects in database.

        The method is used as C{addPair} and as C{delPair} with one-to-many
        associations when updating relationship.

        @see: L{addReferencedObjects} L{delReferencedObjects} L{update}
        """
        for obj, value in pairs:
            self.vbroker.update(value)


    def updateablePair(self, obj, value):
        """
        Return pair of application object and referenced object.

        @see: L{update}
        """
        return (obj, value)
