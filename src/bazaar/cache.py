# $Id: cache.py,v 1.4 2003/09/21 00:56:30 wrobell Exp $
"""
Cache classes for application objects.
"""

import logging

log = logging.getLogger('bazaar.cache')

class Cache(dict):
    """
    Abstract, basic class for different object caches.
    """
    def __init__(self):
        """
        Create object cache.
        """
        dict.__init__(self)
        self.getObjects = self.values


    def append(self, obj):
        """
        Append object to cache.
        """
        self[obj.__key__] = obj


    def remove(self, obj):
        """
        Remove object from cache.
        """
        del self[obj.__key__]
