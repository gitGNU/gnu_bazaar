# $Id: cache.py,v 1.5 2003/11/24 16:42:17 wrobell Exp $
"""
Cache classes for application objects.
"""

import weakref

import logging

log = logging.getLogger('bazaar.cache')

class Cache(object):
    """
    Abstract, basic class for different object caches.

    @ivar owner: Owner of the cache - object broker or association object.
    """
    def __init__(self, owner):
        """
        Create cache class.

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
    def load(self, key):
        """
        Load all association data from database.

        @see: L{bazaar.assoc.List.loadData}
        """
        assert self.owner is not None
        self.owner.loadData()


class Lazy(Cache, dict):
    """
    Abstract, basic cache class for lazy objects and association data
    loading.
    """
    def __getitem__(self, param):
        """
        Return referenced object or association data.

        @param param: Referenced object primary key value or application object.
        """
        if param not in self:
            self.load(param)
        return super(Lazy, self).__getitem__(param)



class LazyObject(Lazy):
    """
    Cache for lazy referenced object loading.
    """
    def load(self, key):
        """
        Load referenced object with primary key value C{key}.
        """
        assert self.owner is not None
        pass #fixme



class LazyAssociation(Lazy):
    """
    Cache for loading all association data from database.
    """
    def load(self, key):
        assert self.owner is not None
        pass # fixme
