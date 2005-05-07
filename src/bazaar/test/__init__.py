# $Id: __init__.py,v 1.6 2005/05/07 00:26:15 wrobell Exp $
#
# Bazaar ORM - an easy to use and powerful abstraction layer between
# relational database and object oriented application.
#
# Copyright (C) 2000-2004 by Artur Wroblewski <wrobell@pld-linux.org>
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
This module simplifies unit testing of applications and libraries, which use
Bazaar ORM library.

Let's suppose, that C{lib} library is going to be tested and there are
created two modules C{lib.test.a} and C{lib.test.b} with unit tests for the
library.

To run unit tests, which use Bazaar ORM library, application classes should
be specified. To specify application classes set C{bazaar.test.TestCase.cls_list} attribute,
i.e.::

    bazaar.test.TestCase.cls_list = (lib.Class1, lib.Class2)

To run all unit tests C{lib.test.all} module can be created, C{lib/test/all.py}::

    import bazaar.test

    bazaar.test.TestCase.cls_list = (lib.Class1, lib.Class2) # set application classes

    if __name__ = '__main__'
        
        # import all library test cases into lib.test.all module namespace,
        # so the all tests will be run
        from bazaar.test.a import *
        from bazaar.test.b import *
        
        # run all tests
        bazaar.test.main()


Module C{lib.test.a} source code example::

    import bazaar.test
    import lib.test.all # this import sets application classes

    class ATestCase(bazaar.test.DBTestCase):
        pass

    if __name__ == '__main__':
        bazaar.test.main()

Module C{lib.test.b} source code example::

    import bazaar.test
    import lib.test.all # this import sets application classes

    class BTestCase(bazaar.test.DBTestCase):
        pass

    if __name__ == '__main__':
        bazaar.test.main()


To run all tests::

    python lib/test/all.py bazaar.ini

To run tests contained in C{lib.test.a} module::

    python lib/test/a.py bazaar.ini
"""


import unittest

import bazaar.cache
import bazaar.core
import bazaar.test.app

class TestCase(unittest.TestCase):
    """
    Base class for Bazaar ORM layer tests.

    List of application classes should be set in modules, which use
    this class.

    @ivar bazaar: Bazaar ORM layer object.
    @ivar cls_list: List of test application classes.
    """
    def setUp(self):
        """
        Create Bazaar ORM layer object.
        """
        from ConfigParser import ConfigParser
        import bazaar.config
        self.config = ConfigParser()
        self.config.read(cfg_file)
        self.bazaar = bazaar.core.Bazaar(self.cls_list, bazaar.config.CPConfig(self.config))



class DBTestCase(TestCase):
    """
    Base class for Bazaar ORM layer tests with database connection.
    """
    def setUp(self):
        """
        Create Bazaar ORM layer instance and connect with database.
        """
        TestCase.setUp(self)
        self.bazaar.connectDB()


    def tearDown(self):
        """
        Close database connection.
        """
        self.bazaar.closeDBConn()



def main():
    """
    Set Bazaar ORM library configuration file and run all unit tests.
    """
    import sys
    import logging.config

    import optparse
    parser = optparse.OptionParser('usage: bzr.py [options] <bazaar.ini>')
    parser.add_option("-l", "--logfile-conf", dest="logfile_conf",
                      help="logging configuration")

    (options, sys.argv) = parser.parse_args(sys.argv)
    logfile_conf = options.logfile_conf

    if len(sys.argv) != 2:
        parser.error('incorrect number of arguments')

    conf = sys.argv[1]
    del sys.argv[1]

    if logfile_conf:
        logging.config.fileConfig(logfile_conf)
    else:
        logging.basicConfig()

    log = logging.getLogger('bazaar.test')

    log.info('starting tests, conf = %s', conf)

    globals()['cfg_file'] = conf # set configuration filename

    unittest.main()


if __name__ == '__main__':
    main()
