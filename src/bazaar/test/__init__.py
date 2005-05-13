# $Id: __init__.py,v 1.10 2005/05/13 20:54:02 wrobell Exp $
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
This module simplifies unit testing of applications and libraries, which use
Bazaar ORM library.

Let's suppose, that C{lib} library is going to be tested and there are
created two modules C{lib.test.a} and C{lib.test.b} with unit tests for the
library.

To run unit tests, which use Bazaar ORM library, application classes should be
specified. To specify application classes set C{bazaar.test.TestCase.cls_list}
attribute, i.e.::

    >>> bazaar.test.TestCase.cls_list = (lib.Class1, lib.Class2)

To run all unit tests C{lib.test.all} module can be created,
C{lib/test/all.py}::

    >>> import bazaar.test

    >>> # set application classes
    >>> bazaar.test.TestCase.cls_list = (lib.Class1, lib.Class2)

    >>> if __name__ == '__main__':
    ...     
    ...     # import all library test cases into lib.test.all module namespace,
    ...     # so the all tests will be run
    ...     from bazaar.test.a import *
    ...     from bazaar.test.b import *
    ...     
    ...     # run all tests
    ...     bazaar.test.main()


Module C{lib.test.a} source code example::

    >>> import bazaar.test
    >>> import lib.test.all # this import sets application classes

    >>> class ATestCase(bazaar.test.DBTestCase):
    ...     pass

    >>> if __name__ == '__main__':
    ...     bazaar.test.main()

Module C{lib.test.b} source code example::

    >>> import bazaar.test
    >>> import lib.test.all # this import sets application classes

    >>> class BTestCase(bazaar.test.DBTestCase):
    ...     pass

    >>> if __name__ == '__main__':
    ...     bazaar.test.main()


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
        self.bazaar = bazaar.core.Bazaar(self.cls_list,
            bazaar.config.CPConfig(self.config))



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



def main(modules = ('__main__', )):
    """
    Set Bazaar ORM library configuration file and run all unit tests.
    """
    import sys
    import logging.config

    import optparse
    parser = optparse.OptionParser('usage: %s [options] <bazaar.ini>' \
        ' [tests...]' % sys.argv[0])
    parser.add_option('-l', '--logfile-conf', dest='logfile_conf',
                      help='logging configuration')
    parser.add_option('-v', '--verbose', action = 'store_true', dest='verbose',
                      help='verbose output')
    parser.add_option('-q', '--quiet', action = 'store_true', dest='quiet',
                      help='quiet output')

    (options, sys.argv) = parser.parse_args(sys.argv)

    if len(sys.argv) < 2:
        parser.error('incorrect number of arguments')

    conf = sys.argv[1]
    del sys.argv[1]

    if options.logfile_conf:
        logging.config.fileConfig(options.logfile_conf)
    else:
        logging.basicConfig()

    log = logging.getLogger('bazaar.test')

    log.info('starting tests, conf = %s', conf)

    globals()['cfg_file'] = conf # set configuration filename

    # load all tests from specified modules
    suite = unittest.TestSuite()
    del sys.argv[0]

    test_found = False

    for modname in modules:
        mod = __import__(modname, globals(), locals(), [''])
        if len(sys.argv) > 0:
            try:
                suite.addTest(unittest.defaultTestLoader.loadTestsFromNames(
                    sys.argv, mod))
                test_found = True
            except AttributeError, ex:
                pass
        else:
            suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(mod))
            test_found = True

    if not test_found:
        print >> sys.stderr, 'Test(s) "%s" not found!' % ', '.join(sys.argv)
        sys.exit(1)

    # set verbosity
    verbosity = 1
    if options.verbose:
        verbosity = 2
    if options.quiet:
        verbosity = 0

    # run tests
    runner = unittest.TextTestRunner(verbosity = verbosity)
    runner.run(suite)


if __name__ == '__main__':
    main()
