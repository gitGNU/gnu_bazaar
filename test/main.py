# $Id: main.py,v 1.6 2003/08/27 15:22:38 wrobell Exp $

import unittest
import logging.config

"""
Bazaar module test suites runner.

@var db_module: Python Database API module.
@var dsn: Database source name (as specified in Python DB API Specification).
"""

logging.config.fileConfig('log.ini')

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print """\
All test suites for Bazaar module.

usage: main.py db_module dsn [tests...]

options:
    db_module   Python DB API 2.0 module
    dsn         database connection parameters

examples:
    main.py psycopg 'dbname = testdb'
    main.py psycopg 'dbname = testdb' core
    main.py psycopg 'dbname = testdb' core.ObjectLoadTestCase
    main.py psycopg 'dbname = testdb' core.ObjectLoadTestCase.testObjectReload
"""
        sys.exit(1)

    import app
    app.db_module = __import__(sys.argv[1])
    app.dsn = sys.argv[2]

    del sys.argv[1:3]

    # import all test modules into global scope and find all test cases
    all_tests = unittest.TestSuite()
    for mod_name in ('conf', 'connection', 'init', 'core'):
        mod = __import__(mod_name)
        all_tests.addTest(unittest.findTestCases(mod))
        globals()[mod_name] = mod 


    def suite():
        """
        Return all test cases.
        """
        return all_tests

    unittest.main(defaultTest = 'suite')
