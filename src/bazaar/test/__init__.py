# $Id: __init__.py,v 1.2 2004/05/23 00:26:37 wrobell Exp $
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

import bazaar.cache
import bazaar.core
import bazaar.test.app

class TestCase(unittest.TestCase):
    """
    Base class for Bazaar layer tests.

    @ivar bazaar: Bazaar layer object.
    @ivar cls_list: List of test application classes.
    """
    def setUp(self):
        """
        Create Bazaar layer object.
        """
        from ConfigParser import ConfigParser
        import bazaar.config
        self.config = ConfigParser()
        self.config.read(cfg_file)
        self.bazaar = bazaar.core.Bazaar(self.cls_list, bazaar.config.CPConfig(self.config))

        # bazaar.test.cache tests for lazy cache!
        assert not self.config.has_section('bazaar.cls')
        assert not self.config.has_section('bazaar.asc')
        assert bazaar.test.app.Article.cache == bazaar.cache.FullObject
        assert bazaar.test.app.Order.getColumns()['items'].cache == bazaar.cache.FullAssociation
        assert bazaar.test.app.Employee.getColumns()['orders'].cache == bazaar.cache.FullAssociation


class DBTestCase(TestCase):
    """
    Base class for Bazaar layer tests with enabled database connection.
    """
    def setUp(self):
        """
        Create Bazaar layer instance and connect with database.
        """
        TestCase.setUp(self)
        self.bazaar.connectDB()


    def tearDown(self):
        """
        Close database connection.
        """
        self.bazaar.closeDBConn()



def main():
    import sys

    globals()['cfg_file'] = sys.argv[1] # get configuration filename
    del sys.argv[1]

    unittest.main()


if __name__ == '__main__':
    main()
