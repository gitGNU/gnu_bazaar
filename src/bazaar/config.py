# $Id: config.py,v 1.1 2003/11/23 20:33:00 wrobell Exp $
"""
Module contains basic classes for Bazaar layer configuration.
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
        application object's primary key value, i.e.
        C{select nextval('%s')}, where C{%s} means name of sequencer.
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
