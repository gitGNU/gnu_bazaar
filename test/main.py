# $Id: main.py,v 1.1 2003/06/18 21:27:03 wrobell Exp $

import unittest
import logging
import logging.config

logging.config.fileConfig('log.ini')
log = logging.getLogger('bazaar.test')

if __name__ == '__main__':
    import conf
    unittest.main(conf)
