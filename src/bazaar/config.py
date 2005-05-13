# $Id: config.py,v 1.7 2005/05/13 17:15:58 wrobell Exp $
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
Module contains basic classes for Bazaar ORM layer configuration.

Bazaar ORM layer is configurable. It is possible to specify several parameters
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
L{bazaar.config.CPConfig} loads Bazaar ORM configuration with C{ConfigParser}
class (ini files). Every configuration class method returns an option
or C{None} if specified parameter is not found in config source.

Of course, it is possible to implement other configuration classes, i.e.
for U{GConf<http://www.gnome.org/projects/gconf/>} configuration system.
"""

from ConfigParser import NoSectionError, NoOptionError

import bazaar
log = bazaar.Log('bazaar.config')

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
    Bazaar ORM configuration using C{ConfigParser} module.

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
            mod = self.cfg.get('bazaar', 'module')
        except NoOptionError:
            mod = None
        except NoSectionError:
            mod = None

        return mod


    def getSeqPattern(self):
        """
        Return pattern of SQL query, which is used to get next value of
        application object's primary key value, i.e.
        C{select nextval('%s')}, where C{%s} means name of sequencer.
        """
        try:
            seqpattern = self.cfg.get('bazaar', 'seqpattern')
        except NoOptionError:
            seqpattern = None
        except NoSectionError:
            seqpattern = None

        return seqpattern


    def getDSN(self):
        """
        Return Python DB API data source name.
        """
        try:
            dsn = self.cfg.get('bazaar', 'dsn')
        except NoOptionError:
            dsn = None
        except NoSectionError:
            dsn = None

        return dsn
    

    def getObjectCache(self, cls):
        """
        Get name of application objects cache class.

        @param cls: Class name of application objects.
        """
        try:
            cache = self.cfg.get('bazaar.cls', '%s.cache' % cls)
        except NoOptionError:
            cache = None
        except NoSectionError:
            cache = None

        return cache


    def getClassSequencer(self, cls):
        """
        Get name of sequencer used to get application objects primary key
        values.

        @param cls: Class name of application objects.
        """
        try:
            sequencer = self.cfg.get('bazaar.cls', '%s.sequencer' % cls)
        except NoOptionError:
            sequencer = None
        except NoSectionError:
            sequencer = None

        return sequencer


    def getClassRelation(self, cls):
        """
        Get name of application class' relation.

        @param cls: Class name.
        """
        try:
            relation = self.cfg.get('bazaar.cls', '%s.relation' % cls)
        except NoOptionError:
            relation = None
        except NoSectionError:
            relation = None

        return relation
    

    def getAssociationCache(self, attr):
        """
        Get name of association cache.

        @param attr: Association attribute name, i.e. C{Order.items}.
        """
        try:
            cache = self.cfg.get('bazaar.asc', '%s.cache' % attr)
        except NoOptionError:
            cache = None
        except NoSectionError:
            cache = None

        return cache
