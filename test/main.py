# $Id: main.py,v 1.2 2003/06/18 21:30:57 wrobell Exp $

import unittest
import logging
import logging.config

"""
<s>Run all bazaar test modules.</s>
"""

logging.config.fileConfig('log.ini')
log = logging.getLogger('bazaar.test')

if __name__ == '__main__':
    # import all test modules
    import conf
    unittest.main(conf)
