# $Id: config.py,v 1.2 2004/01/21 23:06:28 wrobell Exp $
"""
Module contains basic classes for Bazaar layer configuration.

Bazaar layer is configurable. It is possible to specify several parameters
in configuration file such as DB-API module, database connection string,
cache classes, relations, etc.

All parameters are presented in table below::

    +-----------------------------------------------------------------------------+
    |Group         | Section     | Parameter       | Default value                |
    +-----------------------------------------------------------------------------+
    | basic        | bazaar      | module          |          ---                 |
    |              |             | dsn             |          ---                 |
    |              |             | seqpattern      | select nextval for %s        |
    +-----------------------------------------------------------------------------+
    | classes      | bazaar.cls  | <cls>.relation  | application class name       |
    |              |             | <cls>.sequencer | <cls>.relation + '_seq'      |
    |              |             | <cls>.cache     | bazaar.cache.FullObject      |
    +-----------------------------------------------------------------------------+
    | associations | bazaar.asc  | <attr>.cache    | bazaar.cache.FullAssociation |
    +-----------------------------------------------------------------------------+

Sample configuration file using L{bazaar.config.CPConfig} class::

    [bazaar]
    dsn:        dbname = ord port = 5433
    module:     psycopg
    seqpattern: select nextval('%s');

    [bazaar.cls]
    app.Article.sequencer: article_seq
    app.Article.relation:  article
    app.Article.cache:     bazaar.cache.FullObject
    app.OrderItem.cache:   bazaar.cache.LazyObject

    [bazaar.asc]
    app.Department.boss.cache: bazaar.cache.FullAssociation
    app.Order.items.cache:     bazaar.cache.LazyAssociation


It is possible to implement different configuration classes. This module
contains abstract config class L{bazaar.config.Config}. Class
L{bazaar.config.CPConfig} loads Bazaar configuration with C{ConfigParser}
class (ini files). Every configuration class method returns an option
or C{None} if specified parameter is not found in config source.

Of course, it is possible to implement other configuration classes, i.e.
for U{GConf<http://www.gnome.org/projects/gconf/>} configuration system.
"""

from ConfigParser import ConfigParser, NoSectionError, NoOptionError

class Config(object):
    """
    Basic, abstract configuration class.
    """
    def getDBModule(self):
        """
        Return Python DB API module.
        """
        raise NotImplementedError


    def getSeqPattern(self):
        """
        Return pattern of SQL query, which is used to get next value of
        application object's primary key value, i.e.  C{select nextval('%s')},
        where C{%s} means name of sequencer.
        """
        raise NotImplementedError


    def getDSN(self):
        """
        Return Python DB API data source name.
        """
        raise NotImplementedError
    

    def getObjectCache(self, cls):
        """
        Get name of application objects cache class.

        @param cls: Class name of application objects.
        """
        raise NotImplementedError


    def getClassSequencer(self, cls):
        """
        Get name of sequencer used to get application objects primary key
        values.

        @param cls: Class name of application objects.
        """
        raise NotImplementedError


    def getClassRelation(self, cls):
        """
        Get name of application class' relation.

        @param cls: Class name.
        """
        raise NotImplementedError
    

    def getAssociationCache(self, attr):
        """
        Get name of association cache.

        @param attr: Association attribute name, i.e. C{Order.items}.
        """
        raise NotImplementedError


class CPConfig(Config):
    """
    Bazaar configuration using C{ConfigParser} module.

    @ivar cfg: C{ConfigParser} object.
    """
    def __init__(self, cfg):
        """
        Create instance of configuration.

        @param cfg: C{ConfigParser} object.
        """
        self.cfg = cfg


    def getDBModule(self):
        """
        Return Python DB API module.
        """
        try:
            return self.cfg.get('bazaar', 'module')
        except NoOptionError:
            return None
        except NoSectionError:
            return None


    def getSeqPattern(self):
        """
        Return pattern of SQL query, which is used to get next value of
        application object's primary key value, i.e.
        C{select nextval('%s')}, where C{%s} means name of sequencer.
        """
        try:
            return self.cfg.get('bazaar', 'seqpattern')
        except NoOptionError:
            return None
        except NoSectionError:
            return None


    def getDSN(self):
        """
        Return Python DB API data source name.
        """
        try:
            return self.cfg.get('bazaar', 'dsn')
        except NoOptionError:
            return None
        except NoSectionError:
            return None
    

    def getObjectCache(self, cls):
        """
        Get name of application objects cache class.

        @param cls: Class name of application objects.
        """
        try:
            return self.cfg.get('bazaar.cls', '%s.cache' % cls)
        except NoOptionError:
            return None
        except NoSectionError:
            return None


    def getClassSequencer(self, cls):
        """
        Get name of sequencer used to get application objects primary key
        values.

        @param cls: Class name of application objects.
        """
        try:
            return self.cfg.get('bazaar.cls', '%s.sequencer' % cls)
        except NoOptionError:
            return None
        except NoSectionError:
            return None


    def getClassRelation(self, cls):
        """
        Get name of application class' relation.

        @param cls: Class name.
        """
        try:
            return self.cfg.get('bazaar.cls', '%s.relation' % cls)
        except NoOptionError:
            return None
        except NoSectionError:
            return None
    

    def getAssociationCache(self, attr):
        """
        Get name of association cache.

        @param attr: Association attribute name, i.e. C{Order.items}.
        """
        try:
            return self.cfg.get('bazaar.asc', '%s.cache' % attr)
        except NoOptionError:
            return None
        except NoSectionError:
            return None
