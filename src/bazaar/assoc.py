# $Id: assoc.py,v 1.1 2003/09/03 22:48:40 wrobell Exp $
"""
Association classes.
"""

import logging

log = logging.getLogger('bazaar.assoc')

#class Association(object):
#    """
#    Basic association descriptor.
#
#    @ivar cls: Associated application object class.
#    """
#    def __init__(self, cls):
#        """
#        Initialize association descriptor.
#
#        @param cls: Associated application object class.
#        """
#        self.cls = cls


#class OneToOneAssociation(Association):
class OneToOneAssociation(object):
    """
    One to one association descriptor.

    @ivar column: Application class column which defines this association.
    @ivar broker:

    @see: L{bazaar.assoc.Association}
    """
    def __init__(self, column):
        """
        Create one to one association descriptor.

        @param column: Application class column.
        """
        self.column = column
        self.broker = None
        self.buffor = {}


    def __get__(self, obj, cls):
        """
        """
        if not obj: return self
        assert self.broker is not None

        # if the associated object have had no key, then return it from
        # reference buffor; otherwise get it from object cache
        if obj in self.buffor:
            return buffor[obj]
        else:
            return self.broker.cache[getattr(obj, self.column.name)]


    def __set__(self, obj, value):
        """
        """
        # if value is None then just set the value
        if value is None:
            setattr(obj, self.column.name, None)
            return

        assert value is not None

        # check associated object key
        if value.key is None:
            # if key is None then store object in reference buffor
            self.buffor[obj] = value
        else:
            # if key is not None then check if the object exists in reference
            # buffor and when it is true remove it from the buffor
            if obj in self.buffor:
                del self.buffor[obj]
            # finally, assign associated object key to associating object column
            setattr(obj, self.column.name, value.key)
