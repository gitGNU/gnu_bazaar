# $Id: core.py,v 1.22 2003/11/23 20:33:00 wrobell Exp $
"""
This module contains basic Bazaar implementation.

Class L{Bazaar} must be used to get,
modify, find and perform other tasks on application objects.
"""

import logging

import bazaar.assoc
import bazaar.cache
import bazaar.motor

log = logging.getLogger('bazaar.core')

class PersistentObject(object):
    """
    Parent class of an application class.

    @ivar __key__: Object's key.
    """
    def __init__(self, data = None):
        """
        Create persistent object with initial data.

        @param data: Dictionary with initial values of object attributes.
        """
        if data is not None:
            # set object attributes
            self.__dict__.update(data)

#        if __debug__: log.debug('object created (key = "%s"): %s' % (self.key, data))



class Broker:
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
    def __init__(self, cls, mtr):
        """
        Create application class broker.

        Method initializes object cache and database data convertor.
        Database objects loading is requested.

        @param cls: Application class.
        @param mtr: Database access object.
        """

        self.reload = True
        self.cls = cls
        
        self.cache = bazaar.cache.Cache()
        self.convertor = bazaar.motor.Convertor(cls, mtr)

        log.info('class "%s" broker initialized' % cls)


    def loadObjects(self):
        """
        Load application objects from database and put them into cache.

        @see: L{bazaar.core.Broker.getObjects} L{bazaar.core.Broker.reloadObjects}
        """
        for obj in self.convertor.getObjects():
            self.cache.append(obj)

        self.reload = False


    def getObjects(self):
        """
        Get list of application objects.

        If objects reload has been requested, then objects would be loaded
        from database, before returning objects from the cache.
        
        @see: L{bazaar.core.Broker.loadObjects} L{bazaar.core.Broker.reloadObjects}
        """
        if self.reload:
            self.loadObjects()

        return self.cache.getObjects()


    def reloadObjects(self, now = False):
        """
        Request reloading objects from database.

        All objects are removed from cache. If C{now} is set to true, then
        objects are loaded from database immediately.
        
        @param now: Reload objects immediately.

        @see: L{bazaar.core.Broker.loadObjects} L{bazaar.core.Broker.getObjects}
        """
        self.reload = True
        self.cache.clear()
        if now:
            self.loadObjects()


    def find(self, query, dict = None, field = 0):
        """
        Find objects in database.

        @see: L{bazaar.core.Bazaar.find}
        """
        for key in self.convertor.find(query, dict, field):
            # fixme: yield self.cache[key]
            yield self.get(key)


    def get(self, key):
        """
        Get application object of given key.

        Objects is returned from cache. If application objects reload has
        been requested, then objects would be loaded from database.

        @param key: key of object to load

        @return: fixme

        @see: L{bazaar.core.Broker.loadObjects} L{bazaar.core.Broker.reloadObjects}
        """
        if self.reload:
            self.loadObjects()

        if key is None:
            return None
        else:
            return self.cache[key]


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
        old_key = obj.__key__
        self.convertor.update(obj)


    def delete(self, obj):
        """
        Delete object from database.

        @param obj: Object to delete.
        """
        self.convertor.delete(obj)
        self.cache.remove(obj)
#        obj.__key__ = None



class Bazaar:
    """
    The interface to get, modify, find and perform other tasks on
    application objects.

    @ivar motor: Database access object.
    @ivar brokers: Dictionary of brokers. Brokers are mapped with its class application.
    @ivar dsn: Python DB API database source name.
    @ivar cls_list: List of application classes.
    @ivar db_module: Python DB API module.

    @see: L{Broker} L{bazaar.motor.Motor}
    """

    def __init__(self, cls_list, config = None, dsn = '', db_module = None):
        """
        Start the Bazaar layer.

        If database source name is not empty, then database connection is
        created.

        @param cls_list: List of application classes.
        @param db_module: Python DB API module.
        @param dsn: Database source name.

        @see: L{bazaar.core.Bazaar.connectDB}
        """
        self.cls_list = cls_list
        self.config = config
        self.dsn = dsn
        self.db_module = db_module

        if config is not None:
            self.parseConfig(config)

        self.init()

        if dsn:
            self.connectDB(dsn)

        log.info('bazaar started')


    def init(self):
        """
        Initialize the Bazaar layer.
        """
        self.motor = bazaar.motor.Motor(self.db_module)
        self.brokers = {}

        # first, kill existing associations
        for c in self.cls_list:
            for col in c.columns.values():
                col.association = None

        # create association objects
        for c in self.cls_list:
            for col in c.columns.values():
                if col.vcls is None: continue

                if col.association is not None: continue

                if col.is_one_to_one:
                    asc_cls = bazaar.assoc.OneToOne
                elif col.is_one_to_many:
                    asc_cls = bazaar.assoc.OneToMany
                elif col.is_many_to_many:
                    asc_cls = bazaar.assoc.List
                else:
                    assert False

                assert issubclass(asc_cls, bazaar.assoc.AssociationReferenceProxy)

                def setAssociation(cls, col, asc_cls):
                    col.association = asc_cls(col)
                    setattr(cls, col.attr, col.association)

                # bi-directional association
                if col.is_bidir:
                    if col.vattr not in col.vcls.getColumns():
                        raise ColumnMappingError('column of referenced class is not defined', \
                            c, col)

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

                    assert issubclass(asc_vcls, bazaar.assoc.AssociationReferenceProxy)

                    # create association classes
                    setAssociation(c, col, asc_cls)
                    setAssociation(col.vcls, vcol, asc_vcls)
                    col.association.association = vcol.association
                    vcol.association.association = col.association

                    assert col.association is not None
                    assert col.is_bidir and hasattr(col.association, 'association')
                    assert hasattr(col.association, 'col')
                    assert isinstance(col.association, bazaar.assoc.AssociationReferenceProxy)
                    assert isinstance(vcol.association, bazaar.assoc.AssociationReferenceProxy)

                    if __debug__: log.info('bi-directional association %s.%s <-> %s.%s' \
                                % (c, col.attr, col.vcls, col.vattr))
                else:
                    # uni-directional associations
                    # create association classes
                    setAssociation(c, col, asc_cls)
                    col.association.association = None

                    if __debug__: log.debug('uni-directional (%s) association %s.%s -> %s' \
                                    % (asc_cls, c, col.attr, col.vcls))

        for c in self.cls_list:
            self.brokers[c] = Broker(c, self.motor)

        # again to assign brokers for associations
        for c in self.cls_list:
            for col in c.columns.values():
                if col.association is not None:
                    col.association.broker = self.brokers[c]
                    col.association.vbroker = self.brokers[col.vcls]


    def parseConfig(self, config):
        """
        Parse Bazaar configuration.

        @param config: Bazaar configuration.

        @see: L{setConfig} L{bazaar.config.Config} L{bazaar.config.CPConfig}
        """
        dbmod = config.getDBModule()
        if dbmod is not None:
            self.db_module = __import__(dbmod)

        dsn = config.getDSN()
        if dsn is not None: self.dsn = dsn

        seqpattern = config.getSeqPattern()
        if seqpattern is not None: self.seqpattern = seqpattern

        for c in self.cls_list:
            fname = c.__module__ + '.' + c.__name__ # get full name of class
            relation = config.getClassRelation(fname)
            if relation: c.relation = relation

            sequencer = config.getClassSequencer(fname)
            if sequencer: c.sequencer = sequencer
#fixme            c.cache = bazaar.cache....


    def setConfig(self, config):
        """
        Set Bazaar configuration.

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


    def find(self, cls, query, param = None, field = 0):
        """
        Find objects in database.
        """ # fixme: finish description
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
