# $Id: cache.py,v 1.2 2003/07/10 23:14:15 wrobell Exp $

import logging

log = logging.getLogger('bazaar.cache')

"""
<s></s>
<p>
</p>
"""

class Cache(dict):
    """
    <s>Abstract, basic class for different object caches.</s>
    """
    def __init__(self):
        """
        <s>Create object cache.</s>
        """
        dict.__init__(self)
        self.getObjects = self.values


    def append(self, obj):
        """
        <s>Append object to cache.</s>
        """
        self[obj.key] = obj


    def remove(self, obj):
        """
        <s>Remove object from cache.</s>
        """
        del self[obj.key]
