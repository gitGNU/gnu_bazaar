# $Id: core.py,v 1.2 2003/07/10 23:18:09 wrobell Exp $

import logging

import motor
import cache

log = logging.getLogger('bazaar.core')

"""
<s>
    Bazaar is an easy to use and powerful abstraction layer between
    relational database and object oriented application.
</s>
<p>
    Bazaar maps tables into classes, table rows into class objects and
    creates one-to-one, one-to-many and many-to-many associations between
    objects. Several tasks on objects can be performed, such as filtering
    (querying) and sorting objects using database query language.
</p>
<p>
    Bazaar supports GUI development with set of powerful widgets designed
    to simplify development of objects presentation, manipulation and
    searching.
</p>
<p>
    This module contains basic Bazaar implementation.
</p>
<p>
    Class <r class = "Bazaar"/> must be used to get,
    modify, find and perform other tasks on application objects.
</p>
"""


class PersistentObject(object):
    """
    <s>Parent class of an application class.</s>
    <p>
    </p>
    """
    def __init__(self, data = {}):
        """
        <s>Create persistent object.</s>
        <p>
        </p>
        <attr name = 'data'></attr>
        """
        # set object attributes

        self.__dict__.update(data)

        # create object key, if possible
        self.key = self.__class__.getKey(self)

        if __debug__: log.debug('object created (key = "%s"): %s' % (self.key, data))



class Broker:
    """
    <s></s>
    """
    def __init__(self, cls, mtr):
        """
        <s>Create application class broker.</s>

        <p>
            Method initializes object cache and database data convertor.
        </p>

        <attr name = 'cls'>Application class.</s>
        <attr name = 'mtr'>Database access object.</s>

        <see>
            <r class = 'Motor'/>
            <r class = 'Convertor'/>
            <r class = 'Bazaar'/>
        </see>
        """

        self.reload = True
        self.cls = cls
        
        self.cache = cache.Cache()
        self.convertor = motor.Convertor(cls, mtr)

        log.info('class "%s" broker initialized' % cls)


    def getObjects(self):
        """
        <s>Get list of application objects.</s>
        <p>
            Objects are returned from object cache. If objects are not
            loaded from database, then database access is performed and
            objects are put into cache, then returned by the method.
        </p>
        <see>
            <r method = 'reload'/>
        </see>
        """
        if self.reload:
            # clear the cache
            self.cache.clear()

            # load objects from cache
            for obj in self.convertor.getObjects():
                self.cache.append(obj)

            self.reload = False

        return self.cache.getObjects()



class Bazaar:
    """
    <s>
    The interface to get, modify, find and perform other tasks on
    application objects.
    </s>

    <attr name = 'motor'>Database access object.</attr>
    <attr name = 'brokers'>List of brokers.</attr>

    <see>
        <r class = 'Broker'/>
        <r class = 'Motor'/>
    </see>
    """

    def __init__(self, cls_list, db_module, dsn = ''):
        """
        <s>Start the Bazaar layer.</s>

        <p>
        If database source name is not empty, then database connection is
        created.
        </p>

        <attr name = 'cls_list'>List of application classes.</attr>
        <attr name = 'db_module'>Python DB API module.</attr>
        <attr name = 'dsn'>Database source name.</attr>

        <see><r class = 'Bazaar' method = 'connectDB'/></see>
        """
        if len(cls_list) < 1:
            raise AttributeError('application class list cannot be empty')

        self.motor = motor.Motor(db_module)
        self.brokers = {}

        for c in cls_list:
            self.brokers[c] = Broker(c, self.motor)

        if dsn:
            self.connectDB(dsn)

        log.info('bazaar started')


    def connectDB(self, dsn):
        """
        <s>Make new database connection.</s>

        <p>
            New database connection is created with specified database
            source name, which must conform to Python DB API Specification, i.e.
            <code>
                bazaar.connectDB('dbname=addressbook host=localhost port=5432 user=bird')
            </code>
        </p>

        <attr name = 'dsn'>Database source name.</attr>

        <see><r method = 'closeDBConn'/></see>
        """
        self.motor.connectDB(dsn)
        # fixme: what about password visibility?
        if __debug__: log.debug('connected to database "%s"' % dsn)


    def closeDBConn(self):
        """
        <s>Close database connection.</s>
        <see><r method = 'connectDB'/></see>
        """
        self.motor.closeDBConn()
        if __debug__: log.debug('database connection is closed')


    def getObjects(self, cls):
        """
        <s>Get list of application objects.</s>

        <p>Only objects of specified class are returned.</p>

        <attr name = 'cls'>Application object class.</attr>

        <see>
            <r method = 'reload'/>
            <r class = 'Broker' method = 'getObjects'/>
        </see>
        """
        return self.brokers[cls].getObjects()
