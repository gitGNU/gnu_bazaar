# $Id: main.py,v 1.14 2004/01/22 23:21:41 wrobell Exp $
#
# Bazaar - an easy to use and powerful abstraction layer between relational
# database and object oriented application.
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

import unittest
import logging.config

"""
Bazaar module test suites runner.

@var dbmod: Python Database API module.
@var dsn: Database source name (as specified in Python DB API Specification).
"""

logging.config.fileConfig('log.ini')

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print """\
All test suites for Bazaar module.

usage: main.py dbmod dsn [tests...]

options:
    dbmod   Python DB API 2.0 module
    dsn         database connection parameters

examples:
    main.py psycopg 'dbname = testdb'
    main.py psycopg 'dbname = testdb' core
    main.py psycopg 'dbname = testdb' core.ObjectLoadTestCase
    main.py psycopg 'dbname = testdb' core.ObjectLoadTestCase.testObjectReload
"""
        sys.exit(1)

    import app
    app.dbmod = __import__(sys.argv[1])
    app.dsn = sys.argv[2]

    del sys.argv[1:3]

    # import all test modules into global scope and find all test cases
    all_tests = unittest.TestSuite()
    for mod_name in ('conf', 'connection', 'init', 'core', 'assoc', \
            'find', 'config', 'cache'):
        mod = __import__(mod_name)
        all_tests.addTest(unittest.findTestCases(mod))
        globals()[mod_name] = mod 


    def suite():
        """
        Return all test cases.
        """
        return all_tests

    unittest.main(defaultTest = 'suite')
