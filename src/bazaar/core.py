# $Id: core.py,v 1.43 2005/05/29 18:37:03 wrobell Exp $
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
This module contains basic Bazaar ORM implementation.

Every application object should derive from L{PersistentObject} class.

Class L{Bazaar} is designed to to get, modify, find and perform other
operations on objects of any application class.

Brokers (L{Broker} class) are responsible for operations on objects of
specific application class.
"""

import bazaar.assoc
import bazaar.cache
import bazaar.motor

log = bazaar.Log('bazaar.core')

class PersistentObject(object):
    """
    Parent class of an application class.

    @ivar __key__: Object's key.
    """
    def __init__(self, **data):
        """
        Create persistent object with attributes set to C{None} value until
        specified in C{data}.

        @param data: Initial values of object attributes.
        """
        self.__dict__.update(self.__class__.defaults)
        if data != {}:
            for attr in data:
                # set object attributes
                setattr(self, attr, data[attr])

#        if __debug__:
#            log.debug('object created (key = "%s"): %s' % (self.key, data))



class Broker(object):
    """
    Application class broker.

    Application class broker is responsible for taking decision on getting
    objects from database or cache, loading application objects from
    database with convertor and manipulating application objects with
    cache.

    @ivar cls: Application class.
    @ivar cache: Cache of application objects.
    @ivar convertor: Relational and object data convertor.
    @ivar reload: If true, then application object's reload has been
        requested.

    @see: L{bazaar.motor.Motor} L{bazaar.motor.Convertor}
          L{bazaar.cache}
    """
    def __init__(self, cls, mtr, seqpattern = None):
        """
        Create application class broker.

        Method initializes object cache and database data convertor.
        Database objects loading is requested.

        @param cls: Application class.
        @param mtr: Database access object.
        """
        self.reload = True
        self.cls = cls
        
        log.info('class "%s" using cache "%s"' \
            % (self.cls, self.cls.cache))
        self.cache = self.cls.cache(self)

        self.convertor = bazaar.motor.Convertor(cls, mtr, seqpattern)

        log.info('class "%s" broker initialized' % cls)


    def loadObjects(self):
        """
        Load application objects from database and put them into cache.

        @see: L{bazaar.core.Broker.getObjects} L{bazaar.core.Broker.reloadObjects}
        """
        for obj in self.convertor.getObjects():
            self.cache[obj.__key__] = obj

        self.reload = False
        return self.cache.itervalues()


    def getObjects(self):
        """
        Get list of application objects.

        If objects reload has been requested, then objects would be loaded
        from database before returning objects from the cache.
        
        @see: L{bazaar.core.Broker.loadObjects} L{bazaar.core.Broker.reloadObjects}
        """
        if self.reload:
            objects = self.loadObjects()
        else:
            objects = self.cache.values()

        for obj in objects:
            yield obj


    def reloadObjects(self, now = False):
        """
        Request reloading objects from database.

        All objects are removed from cache. If C{now} is set to true, then
        objects are loaded from database immediately.

        If objects immediate reload is requested, then method returns iterator
        of objects being loaded from database.
        
        @param now: Reload objects immediately.

        @see: L{bazaar.core.Broker.loadObjects} L{bazaar.core.Broker.getObjects}
        """
        self.reload = True
        self.cache.clear()
        if now:
            return self.loadObjects()


    def find(self, query, param = None, field = 0):
        """
        Find objects in database.

        @param query: SQL query or dictionary.
        @param param: SQL query parameters.
        @param field: SQL column number which describes found objects' primary
            key values.

        @see: L{bazaar.core.Bazaar.find}
        """
        for key in self.convertor.find(query, param, field):
            yield self.cache[key]


    def get(self, key):
        """
        Get application object.

        Object is returned from cache.

        @param key: Object's primary key value.

        @return: Object with primary key value equal to C{key}.

        @see: L{bazaar.cache}
        """
        return self.cache[key]


    def reload(self, key):
        """
        Reload application object of given key from database.

        If application object does not exist in database, then it will be
        removed from cache.

        If reloaded object exists in database and in cache, then application
        object will be replaced with new instance in cache.
        """
        obj = self.convertor.get(key)
        if obj is None:
            # object is no more in database, remove it from cache
            if key in self.cache:
                del self.cache[key]
        else:
            self.cache[key] = obj

        # fixme: what about associations?


    def add(self, obj):
        """
        Add object into database.

        @param obj: Object to add.
        """
        self.convertor.add(obj)
        self.cache[obj.__key__] = obj


    def update(self, obj):
        """
        Update object in database.

        @param obj: Object to update.
        """
        self.convertor.update(obj)


    def delete(self, obj):
        """
        Delete object from database.

        Object's primary key value is set to C{None}.

        @param obj: Object to delete.
        """
        self.convertor.delete(obj)
        del self.cache[obj.__key__]
        obj.__key__ = None



class Bazaar(object):
    """
    The interface to get, modify, find and perform other tasks on
    application objects.

    @ivar motor: Database access object.
    @ivar brokers: Dictionary of brokers. Brokers are mapped with its class application.
    @ivar dsn: Python DB API database source name.
    @ivar cls_list: List of application classes.
    @ivar dbmod: Python DB API module.

    @see: L{Broker} L{bazaar.motor.Motor}
    """

    def __init__(self, cls_list, config = None, dsn = '', dbmod = None,
            seqpattern = None):
        """
        Start the Bazaar ORM layer.

        If database source name is not empty, then database connection is
        created.

        @param cls_list: List of application classes.
        @param config: Configuration object.
        @param dsn: Database source name.
        @param dbmod: Python DB API module.
        @param seqpattern: Sequence command pattern.

        @see: L{bazaar.core.Bazaar.connectDB}, L{bazaar.config}
        """
        self.cls_list = cls_list
        self.config = config
        self.dsn = dsn
        self.dbmod = dbmod
        self.seqpattern = 'select next value for \'%s\''
        self.motor = None
        self.brokers = None

        if config is not None:
            self.parseConfig(config)

        if seqpattern is not None:
            self.seqpattern = seqpattern

        self.init()

        if dsn:
            self.connectDB(dsn)

        log.info('bazaar started')


    def init(self):
        """
        Initialize the Bazaar ORM layer.
        """
        self.motor = bazaar.motor.Motor(self.dbmod)
        self.brokers = {}

        # first, kill existing associations
        for c in self.cls_list:
            for col in c.getColumns().values():
                col.association = None

        # create association objects
        for c in self.cls_list:
            for col in c.getColumns().values():
                if col.vcls is None:
                    continue

                if col.association is not None:
                    continue

                if col.is_one_to_one:
                    asc_cls = bazaar.assoc.OneToOne
                elif col.is_one_to_many:
                    asc_cls = bazaar.assoc.OneToMany
                elif col.is_many_to_many:
                    asc_cls = bazaar.assoc.List
                else:
                    assert False

                assert \
                    issubclass(asc_cls, bazaar.assoc.AssociationReferenceProxy)

                def set_association(cls, col, asc_cls):
                    col.association = asc_cls(col)
                    setattr(cls, col.attr, col.association)

                # bi-directional association
                if col.is_bidir:
                    if col.vattr not in col.vcls.getColumns():
                        raise bazaar.exc.ColumnMappingError(
                            'column of referenced class is not defined', c, col)

                    vcol = col.vcls.getColumns()[col.vattr]
                    
                    # specialized classes for bi-directional associations
                    if issubclass(asc_cls, bazaar.assoc.OneToOne):
                        asc_cls = bazaar.assoc.BiDirOneToOne
                        if vcol.is_one_to_one:
                            asc_vcls = asc_cls
                        elif vcol.is_one_to_many:   
                            asc_vcls = bazaar.assoc.OneToMany
                    elif issubclass(asc_cls, bazaar.assoc.List):
                        if vcol.is_one_to_one or vcol.is_one_to_many:
                            asc_vcls = bazaar.assoc.BiDirOneToOne
                        elif vcol.is_many_to_many:
                            asc_vcls = bazaar.assoc.BiDirManyToMany

                    assert issubclass(asc_vcls,
                        bazaar.assoc.AssociationReferenceProxy)

                    # create association classes
                    set_association(c, col, asc_cls)
                    set_association(col.vcls, vcol, asc_vcls)
                    col.association.association = vcol.association
                    vcol.association.association = col.association

                    assert col.association is not None
                    assert col.is_bidir \
                        and hasattr(col.association, 'association')
                    assert hasattr(col.association, 'col')
                    assert isinstance(col.association, 
                        bazaar.assoc.AssociationReferenceProxy)
                    assert isinstance(vcol.association,
                        bazaar.assoc.AssociationReferenceProxy)

                    if __debug__:
                        log.info('bi-directional association %s.%s <-> %s.%s' \
                            % (c, col.attr, col.vcls, col.vattr))
                else:
                    # uni-directional associations
                    # create association classes
                    set_association(c, col, asc_cls)
                    col.association.association = None

                    if __debug__:
                        log.debug('uni-directional (%s) association' \
                            '%s.%s -> %s' % (asc_cls, c, col.attr, col.vcls))

        for c in self.cls_list:
            self.brokers[c] = Broker(c, self.motor, self.seqpattern)

        # again to assign brokers for associations
        for c in self.cls_list:
            for col in c.getColumns().values():
                if col.association is not None:
                    col.association.broker = self.brokers[c]
                    col.association.vbroker = self.brokers[col.vcls]


    def parseConfig(self, config): #fixme: debug messages
        """
        Parse Bazaar ORM configuration.

        @param config: Bazaar ORM configuration.

        @see: L{setConfig} L{bazaar.config.Config} L{bazaar.config.CPConfig}
        """
        dbmod = config.getDBModule()
        if dbmod is not None:
            self.dbmod = __import__(dbmod, globals(), locals(), [''])
            log.info('DB API module: %s' % self.dbmod.__name__)

        dsn = config.getDSN()
        if dsn is not None:
            self.dsn = dsn
            log.info('data source name loaded from configuration file')

        seqpattern = config.getSeqPattern()
        if seqpattern is not None:
            self.seqpattern = seqpattern
            log.info('sequencer pattern: "%s"' % self.seqpattern)

        def get_class(path): # get class
            items = path.split('.')
            mod = '.'.join(items[:-1])
            cls = items[-1]
            return __import__(mod, globals(), locals(), ['']).__dict__[cls]

        # check configuration for every class
        for c in self.cls_list:
            fname = c.__module__ + '.' + c.__name__ # get full name of class
            relation = config.getClassRelation(fname)
            if relation:
                c.relation = relation
                log.info('%s relation: %s' % (c, c.relation))

            sequencer = config.getClassSequencer(fname)
            if sequencer:
                c.sequencer = sequencer
                log.info('%s sequencer: %s' % (c, c.sequencer))

            if __debug__:
                log.debug('get class %s cache' % fname)
            cache = config.getObjectCache(fname)
            if __debug__:
                log.debug('got class %s cache: %s' % (fname, cache))

            if cache:
                c.cache = get_class(cache)
            else:
                c.cache = bazaar.cache.FullObject
            log.info('%s cache: %s' % (c, c.cache))
            
            # check configuration for every attribute
            for col in c.getColumns().values():
                aname = fname + '.' + col.attr
                if __debug__:
                    log.debug('get association %s cache' % aname)
                cache = config.getAssociationCache(aname)
                if __debug__:
                    log.debug('got association %s cache: %s' % (aname, cache))
                if cache:
                    col.cache = get_class(cache)
                else:
                    col.cache = bazaar.cache.FullAssociation
                log.info('association "%s" cache: %s' % (aname, c.cache))
            

    def setConfig(self, config):
        """
        Set Bazaar ORM configuration.

        @see: L{parseConfig} L{init} L{bazaar.config.Config} L{bazaar.config.CPConfig}
        """
        self.parseConfig(config)
        self.init()


    def connectDB(self, dsn = None):
        """
        Make new database connection.

        New database connection is created with specified database source
        name, which must conform to Python DB API Specification, i.e.::

            bazaar.connectDB('dbname=addressbook host=localhost port=5432 user=bird')

        It is possible to reconnect with previous database source name, too::
            
            bazaar.connectDB()

        @param dsn: Database source name.

        @see: L{bazaar.core.Bazaar.closeDBConn}
        """
        if dsn is not None:
            self.dsn = dsn

        # fixme: raise exception when dsn is none?

        self.motor.connectDB(self.dsn)
        # fixme: what about password visibility?
        if __debug__:
            log.debug('connected to database "%s"' % dsn)


    def closeDBConn(self):
        """
        Close database connection.

        @see: L{bazaar.core.Bazaar.connectDB}
        """
        self.motor.closeDBConn()
        if __debug__:
            log.debug('database connection is closed')


    def get(self, cls, key):
        """
        Get object with key.

        @param cls: Application class.
        @param key: Object key.
        """
        return self.brokers[cls].get(key)


    def getObjects(self, cls):
        """
        Get list of application objects.

        Only objects of specified class are returned.

        @param cls: Application class.

        @see: L{bazaar.core.Bazaar.reloadObjects}
        """
        return self.brokers[cls].getObjects()


    def reloadObjects(self, cls, now = False):
        """
        Reload objects from database.

        If objects immediate reload is requested, then method returns iterator
        of objects being loaded from database.

        @param cls: Application class.
        @param now: Reload objects immediately.

        @see: L{bazaar.core.Bazaar.getObjects}
        """
        return self.brokers[cls].reloadObjects(now)


    def find(self, cls, query, param = None, field = 0):
        """
        Find objects of given class in database.

        The method can be used in two ways.

        First, simple dictionary can be passed as query::

            # iterator is returned, so its next() method is used to get
            # the object
            apple = bazaar.find(Article, {'name': 'apple'}).next()

        Dictionary can contain objects as values, i.e.::

            bazaar.find(OrderItem, {'article': art})


        Second, it is possible to use full power of SQL language::

            # find orders and their articles if order amount is greater
            # than 50$

            # find orders with the query
            query = \"""
                select O.__key__ from "order" O
                left outer join order_item OI on O.__key__ = OI.order_fkey
                left outer join article A on OI.article_fkey = A.__key__
                group by O.__key__ having sum(A.price) > 50
            \"""

            for ord in  bzr.find(Order, query):
                print ord                     # show order
                for oi in ord.items:          # show order's articles
                    print oi.article


        @param   cls: Application class.
        @param query: SQL query or dictionary.
        @param param: SQL query parameters.
        @param field: SQL column number which describes found objects' primary
            key values.

        @return: Iterator of found objects.
        """
        return self.brokers[cls].find(query, param, field)


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

        Object's primary key value is set to C{None}.

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
