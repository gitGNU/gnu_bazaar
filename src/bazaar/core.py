# $Id: core.py,v 1.9 2003/09/03 22:39:47 wrobell Exp $
"""
This module contains basic Bazaar implementation.

Class L{Bazaar} must be used to get,
modify, find and perform other tasks on application objects.
"""

import logging

import motor
import cache

log = logging.getLogger('bazaar.core')

class PersistentObject(object):
    """
    Parent class of an application class.

    @ivar key: Object's key.
    """
    def __init__(self, data = None):
        """
        Create persistent object with initial data.

        @param data: Dictionary with initial values of object attributes.
        """
        if data is None: data = {}

        # set object attributes
        for col_name in self.__class__.columns:
            if col_name in data:
                self.__dict__[col_name] = data[col_name]
            else:
                self.__dict__[col_name] = None

        # set key
        self.key = None

#        if __debug__: log.debug('object created (key = "%s"): %s' % (self.key, data))



class Broker:
    """
    Application class broker.

    Application class broker is responsible for taking decision on getting
    objects from database or cache, loading application objects from
    database with convertor and manipulating application objects with
    cache.

    @see: L{bazaar.motor.Motor} L{bazaar.motor.Convertor}
          L{bazaar.cache}
    """
    def __init__(self, cls, mtr):
        """
        Create application class broker.

        Method initializes object cache and database data convertor.

        @param cls: Application class.
        @param mtr: Database access object.
        """

        self.reload = True
        self.cls = cls
        
        self.cache = cache.Cache()
        self.convertor = motor.Convertor(cls, mtr)

        log.info('class "%s" broker initialized' % cls)


    def getObjects(self):
        """
        Get list of application objects.

        Objects are returned from object cache. If objects are not loaded
        from database, then database access is performed and objects are
        put into cache, then returned by the method.

        @see: L{reloadObjects}
        """
        if self.reload:
            # clear the cache
            self.cache.clear()

            # load objects from cache
            for obj in self.convertor.getObjects():
                self.cache.append(obj)

            self.reload = False

        return self.cache.getObjects()


    def reloadObjects(self, now = False):
        """
        Reload objects from database.

fixme:  This behaviour can be changed with C{now} method
        parameter.
        
        @param now: Reload objects immediately.
        """
        self.reload = True
        if now:
            self.getObjects()


    def add(self, obj):
        """
        Add object into database.

        @param obj: Object to add.
        """
        self.convertor.add(obj)
        self.cache.append(obj)


    def update(self, obj):
        """
        Update object in database.

        @param obj: Object to update.
        """
        old_key = obj.key
        self.convertor.update(obj)
        if old_key != obj.key:
            del self.cache[old_key]
            self.cache.append(obj)


    def delete(self, obj):
        """
        Delete object from database.

        @param obj: Object to delete.
        """
        self.convertor.delete(obj)
        self.cache.remove(obj)



class Bazaar:
    """
    The interface to get, modify, find and perform other tasks on
    application objects.

    @ivar motor: Database access object.
    @ivar brokers: Dictionary of brokers. Brokers are mapped with its
        class application.

    @see: L{Broker} L{bazaar.motor.Motor}
    """

    def __init__(self, cls_list, db_module, dsn = ''):
        """
        Start the Bazaar layer.

        If database source name is not empty, then database connection is
        created.

        @param cls_list: List of application classes.
        @param db_module: Python DB API module.
        @param dsn: Database source name.

        @see: L{bazaar.core.Bazaar.connectDB}
        """
        if len(cls_list) < 1:
            raise ValueError('list of application classes should not be empty')

        self.motor = motor.Motor(db_module)
        self.brokers = {}

        for c in cls_list:
            self.brokers[c] = Broker(c, self.motor)
#            if len(c.key_columns) < 1:
#                raise bazaar.exc.MappingError('class "%s" key is not defined')
        # again to assign brokers for associations
        for c in cls_list:
            for col in c.columns.values():
                if col.one_to_one:
                    col.association.broker = self.brokers[col.cls]

        if dsn:
            self.connectDB(dsn)

        log.info('bazaar started')


    def connectDB(self, dsn):
        """
        Make new database connection.

        New database connection is created with specified database source
        name, which must conform to Python DB API Specification, i.e.::

            bazaar.connectDB('dbname=addressbook host=localhost port=5432 user=bird')

        @param dsn: Database source name.

        @see: L{bazaar.core.Bazaar.closeDBConn}
        """
        self.motor.connectDB(dsn)
        # fixme: what about password visibility?
        if __debug__: log.debug('connected to database "%s"' % dsn)


    def closeDBConn(self):
        """
        Close database connection.

        @see: L{bazaar.core.Bazaar.connectDB}
        """
        self.motor.closeDBConn()
        if __debug__: log.debug('database connection is closed')


    def getObjects(self, cls):
        """
        Get list of application objects.

        Only objects of specified class are returned.

        @param cls: Application object class.

        @see: L{bazaar.core.Bazaar.reloadObjects} L{bazaar.core.Broker.getObjects}
        """
        return self.brokers[cls].getObjects()


    def reloadObjects(self, cls, now = False):
        """
        Reload objects from database.

        @param now: Reload objects immediately.
        """
        self.brokers[cls].reloadObjects(now)


    def add(self, obj):
        """
        Add object to database.

        @param obj: Object to add.
        """
        self.brokers[obj.__class__].add(obj)


    def update(self, obj):
        """
        Update object in database.

        @param obj: Object to update.
        """
        self.brokers[obj.__class__].update(obj)


    def delete(self, obj):
        """
        Delete object from database.

        @param obj: Object to delete.
        """
        self.brokers[obj.__class__].delete(obj)


    def commit(self):
        """
        Commit pending database transactions.
        """
        self.motor.commit()


    def rollback(self):
        """
        Rollback database transactions.
        """
        self.motor.rollback()
