# $Id: cache.py,v 1.3 2003/08/25 19:01:06 wrobell Exp $
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
        self[obj.key] = obj


    def remove(self, obj):
        """
        Remove object from cache.
        """
        del self[obj.key]
