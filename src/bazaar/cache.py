# $Id: cache.py,v 1.6 2003/11/25 16:27:48 wrobell Exp $
"""
Cache classes for application objects.
"""

import weakref
from UserDict import UserDict # weakref inherits from UserDict :-\

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
    def __getitem__(self, param):
        """
        Return referenced object or association data.

        @param param: Referenced object primary key value or application object.
        """
        if self.owner.reload:
            self.load(param)
        return dict.__getitem__(self, param)



class FullObject(Full):
    """
    Cache for loading all application class objects from database.
    """
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
            data = self.weak.__getitem__(self, param)
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
        self.weak = weakref.WeakValueDictionary # to know weak dictionary superclass
        weakref.WeakValueDictionary.__init__(self)


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
