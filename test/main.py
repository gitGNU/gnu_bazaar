# $Id: main.py,v 1.3 2003/07/10 23:03:07 wrobell Exp $

import unittest
import logging
import logging.config

"""
<s>Run all bazaar test modules.</s>
<attr name = 'db_module'>Python Database API module.</attr>
<attr name = 'dsn'>
    Database source name (as specified in Python DB API Specification).
</attr>
"""

logging.config.fileConfig('log.ini')
log = logging.getLogger('bazaar.test')


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print """\
Bazaar main test.

usage:
    main.py db_module dsn [test modules...]
"""
        sys.exit(1)

    import app
    app.db_module = __import__(sys.argv[1])
    app.dsn = sys.argv[2]

    log.info('Python DB API module: %s' % app.db_module)
    log.info('data source name: %s' % app.dsn)

    del sys.argv[1:3]

    # import all test modules
    def suite():
        suite = unittest.TestSuite()
        for mod_name in ('conf', 'connection', 'init', 'core'):
            mod = __import__(mod_name)
            suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(mod))
        return suite
        
    unittest.main(defaultTest = 'suite')
