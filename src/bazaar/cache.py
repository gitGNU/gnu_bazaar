# $Id: cache.py,v 1.7 2003/11/26 00:16:48 wrobell Exp $
"""
Cache classes for application objects.
"""

import weakref
from UserDict import UserDict # weakref inherits from UserDict :-\
import sets

import logging

log = logging.getLogger('bazaar.cache')

class Cache(object):
    """
    Abstract, basic class for different object caches.

    @ivar owner: Owner of the cache - object broker or association object.
    """
    def __init__(self, owner):
        """
        Create cache object.

        @param owner: Owner of the cache - object broker or association object.
        """
        super(Cache, self).__init__()
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
    empty = sets.Set()
    """
    Cache for loading all association data from database.
    """
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
    Cache for loading all association data from database.
    """
    def load(self, key):
        assert self.owner is not None
        pass # fixme
        # return empty set, too
