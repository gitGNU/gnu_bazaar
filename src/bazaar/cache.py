# $Id: cache.py,v 1.8 2003/11/26 02:34:32 wrobell Exp $
"""
Cache classes for application objects.
"""

import weakref
from UserDict import UserDict # weakref inherits from UserDict :-\
import sets

import logging

log = logging.getLogger('bazaar.cache')



class ReferenceBuffer(weakref.WeakKeyDictionary):
    """
    Simple reference buffer class.

    The class is used to save referenced objects, which has no primary key
    value.

    It is dictionary with application objects as keys and referenced
    objects as values.
    @see: l{bazaar.assoc.ListReferenceBuffer}
    """
    def __contains__(self, item):
        """
        Check if application object is stored in reference buffer.

        @param item: Tuple of application object and referenced object.

        @return: Returns true if application object is in reference buffer.
        """
        if isinstance(item, tuple):
            return weakref.WeakKeyDictionary.__contains__(self, item[0])
        else:
            return weakref.WeakKeyDictionary.__contains__(self, item)



    def __delitem__(self, (obj, value)):
        """
        Remove application object from reference buffer. 
        """
        weakref.WeakKeyDictionary.__delitem__(self, obj)



class ListReferenceBuffer(ReferenceBuffer):
    """
    Reference buffer for set of objects.

    It is dictionary with application objects as keys and set of referenced
    objects as value.

    @see: L{bazaar.cache.ReferenceBuffer}
    """
    def __contains__(self, item):
        """
        Check if application object referenced objects are in reference
        buffer. Operator ``in'' can be used in two ways::

            # buffer contains minimum one referenced value by application
            # object obj (len(ref_buf[obj]) > 0):
            obj in ref_buf
            (obj, None) in ref_buf

            # referenced object value is referenced by obj and exists in
            # buffer:
            (obj, value) in ref_buf

        @param item: Application object or pair of application object and referenced object.
        """
        if isinstance(item, tuple):
            obj, value = item
            if value is None:
                return weakref.WeakKeyDictionary.__contains__(self, obj)
            else:
                return weakref.WeakKeyDictionary.__contains__(self, obj) and value in self[obj]
        else:
            return weakref.WeakKeyDictionary.__contains__(self, item)


    def __setitem__(self, obj, value):
        """
        Add referenced object to the aplication object's set of referenced
        objects.

        The set is created if it does not exist.

        @param obj: Application object.
        @param value: Referenced object.
        """
        assert obj is not None and value is not None

        if obj not in self:
            ref_buf = ReferenceBuffer.__setitem__(self, obj, sets.Set())
        key_set = self[obj]

        assert isinstance(key_set, sets.Set)
        key_set.add(value)


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

        self[obj].remove(value)
        if len(self[obj]) == 0:
            ReferenceBuffer.__delitem__(self, (obj, None))

        assert (obj not in self or len(self[obj]) > 0) \
            and (obj, value) not in self




class Cache:
#class Cache(object):
    """
    Abstract, basic class for different object caches.

    @ivar owner: Owner of the cache - object broker or association object.
    """
    def __init__(self, owner):
        """
        Create cache object.

        @param owner: Owner of the cache - object broker or association object.
        """
        #super(Cache, self).__init__()
        self.owner = owner


    def load(self, key):
        """
        Load referenced objects or association data from database.
        """
        raise NotImplementedError


    def __getitem__(self, param):
        """
        Return referenced object or association data.

        @param param: Referenced object primary key value or application object.
        """
        raise NotImplementedError


class Full(Cache, dict):
    """
    Abstract, basic cache class for loading all objects and association data.
    """
    def __init__(self, param):
        Cache.__init__(self, param)
        dict.__init__(self)
        self.dicttype = dict


    def __getitem__(self, param):
        """
        Return referenced object or association data.

        @param param: Referenced object primary key value or application object.
        """
        if self.owner.reload:
            self.load(param)
        if param in self:
            return dict.__getitem__(self, param)
        else:
            return self.empty



class FullObject(Full):
    empty = None

    def load(self, key):
        """
        Load all application class objects from database.

        @see: L{bazaar.core.Broker.loadObjects}
        """
        assert self.owner is not None
        self.owner.loadObjects()



class FullAssociation(Full):
    """
    Cache for loading all association data from database.
    """

    empty = sets.Set()

    def load(self, obj):
        """
        Load all association data from database.

        @see: L{bazaar.assoc.List.loadData}
        """
        assert self.owner is not None
        self.owner.loadData()



class Lazy(Cache):
    """
    Abstract, basic cache class for lazy objects and association data
    loading.
    """
    def __getitem__(self, param):
        """
        Return referenced object or association data.

        @param param: Referenced object primary key value or application object.
        """
        # keep strong reference to data until returned,
        # so data will not be wiped out
        if param not in self:
            data = self.load(param)
        else:
            data = self.dicttype.__getitem__(self, param)
        return data



class LazyObject(Lazy, weakref.WeakValueDictionary):
    """
    Cache for lazy referenced object loading.
    """
    def __init__(self, owner):
        """
        Create object lazy cache.

        @param owner: Owner of the cache - object broker or association object.
        """
        Lazy.__init__(self, owner)
        weakref.WeakValueDictionary.__init__(self)
        self.dicttype = weakref.WeakValueDictionary # to know weak dictionary superclass


    def load(self, key):
        """
        Load referenced object with primary key value C{key}.
        """
        assert self.owner is not None
        obj = self.owner.convertor.get(key)
        self[key] = obj
        return obj



class LazyAssociation(Lazy, weakref.WeakKeyDictionary):
    """
    Cache for lazy loading all association data from database.
    """
    def __init__(self, owner):
        """
        Create object lazy cache.

        @param owner: Owner of the cache - object broker or association object.
        """
        Lazy.__init__(self, owner)
        weakref.WeakKeyDictionary.__init__(self)
        self.dicttype = weakref.WeakKeyDictionary # to know weak dictionary superclass


    def load(self, obj):
        assert self.owner is not None
        data = sets.Set()
        for vkey in self.owner.broker.convertor.getAscData(self.owner, obj):
            data.add(vkey)
        self[obj] = data
        return data
