# $Id: cache.py,v 1.21 2005/05/12 18:29:58 wrobell Exp $
#
# Bazaar ORM - an easy to use and powerful abstraction layer between
# relational database and object oriented application.
#
# Copyright (C) 2000-2005 by Artur Wroblewski <wrobell@pld-linux.org>
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Cache and reference buffer classes.

Cache classes are used to buffer objects and association data loaded from
database. There are two types of cache:
    - full:
        - objects - all objects of their class are loaded from database at
          once
        - association data - all data (for all application objects of given
          relationship between two classes) are loaded from database at
          once
    - lazy:
        - objects - only one object is loaded from database
        - association data - data are loaded for given application object

Cache and buffer classes are dictionaries. A dictionary contains pairs of
primary key value and object identified by the primary key (object cache)
or application object and set of primary key values of referenced objects
(one-to-many and many-to-many association data cache).

Reference buffers contains objects, which does not have priamry key values
(are not in database).

Every class and association has its own cache, which is configurable, see
L{bazaar.config} module documentation.
"""

import weakref

import bazaar

log = bazaar.Log('bazaar.cache')



class ReferenceBuffer(weakref.WeakKeyDictionary):
    """
    Simple reference buffer class.

    The class is used to save referenced objects, which has no primary key
    value.

    It is dictionary with application objects as keys and referenced
    objects as values.

    @see: L{bazaar.cache.ListReferenceBuffer}
    """
    def __contains__(self, item):
        """
        Check if application object is stored in reference buffer.

        @param item: Tuple of application object and referenced object.

        @return: Returns true if application object is in reference buffer.
        """
        if isinstance(item, tuple):
            in_ref_buf = weakref.WeakKeyDictionary.__contains__(self, item[0])
        else:
            in_ref_buf = weakref.WeakKeyDictionary.__contains__(self, item)
        return in_ref_buf


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
        Check if object is in reference buffer. Operator C{in} can be used
        in two ways::

            # buffer contains minimum one referenced value by application
            # object obj (len(ref_buf[obj]) > 0):
            obj in ref_buf
            # or
            (obj, None) in ref_buf

            # referenced object value is referenced by obj and exists in
            # buffer:
            (obj, value) in ref_buf

        @param item: Application object or pair of application object and referenced object.
        """
        if isinstance(item, tuple):
            obj, value = item
            if value is None:
                in_ref_buf = weakref.WeakKeyDictionary.__contains__(self, obj)
            else:
                in_ref_buf = weakref.WeakKeyDictionary.__contains__(self, obj) \
                    and value in self[obj]
        else:
            in_ref_buf = weakref.WeakKeyDictionary.__contains__(self, item)

        return in_ref_buf 


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
            ReferenceBuffer.__setitem__(self, obj, set())
        key_set = self[obj]

        assert isinstance(key_set, set)
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



class Cache(object):
    """
    Abstract, basic class for different data caches.

    @ivar owner: Owner of the cache - object broker or association object.
    """
    def __init__(self, owner):
        """
        Create cache object.

        @param owner: Owner of the cache - object broker or association object.
        """
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
        super(Full, self).__init__(param)
        self.dicttype = dict


    def __getitem__(self, param):
        """
        Return referenced object or association data.

        @param param: Referenced object primary key value or application object.

        @return: Referenced object or association data (depends on cache type).
            If data is not found then C{None}.

        @see: L{bazaar.cache.FullObject} L{bazaar.cache.FullAssociation}
        """
        if self.owner.reload:
            self.load(param)
        if param in self:
            return dict.__getitem__(self, param)
        else:
            return None



class FullObject(Full):
    """
    Cache class for loading all objects of application class from database.
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
    Cache for loading all association data of relationship from database.
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

    @ivar dicttype: Weak dictionary superclass, i.e. C{WeakValueDictionary}
        or C{WeakKeyDictionary}.
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
        # to know weak dictionary superclass, fixme: super should be used?
        self.dicttype = weakref.WeakValueDictionary


    def load(self, key):
        """
        Load referenced object with primary key value C{key}.
        """
        assert self.owner is not None
        self[key] = obj = self.owner.convertor.get(key)
        return obj


    def itervalues(self):
        """
        Return all application class objects from database.

        Method load objects from database, then checks if specific object
        exists in cache. If exists then object from cache is returned
        instead of object from database.
        """
        for obj in self.owner.convertor.getObjects():
            if obj.__key__ in self:
                obj = self[obj.__key__] # get existing instance
            else:
                # there is no object instance, so add it to cache
                self[obj.__key__] = obj

            yield obj



class LazyAssociation(Lazy, weakref.WeakKeyDictionary):
    """
    Cache for lazy loading of association data from database.
    """
    def __init__(self, owner):
        """
        Create object lazy cache.

        @param owner: Owner of the cache - object broker or association object.
        """
        Lazy.__init__(self, owner)
        weakref.WeakKeyDictionary.__init__(self)
        # to know weak dictionary superclass, fixme: super should be used?
        self.dicttype = weakref.WeakKeyDictionary


    def load(self, obj):
        """
        Load association data from database for application object C{obj}.

        @param obj: Application object.

        @return: Loaded association data from database.
        """
        assert self.owner is not None
        data = set()
        for vkey in self.owner.broker.convertor.getAscData(self.owner, obj):
            data.add(vkey)
        self[obj] = data
        return data
