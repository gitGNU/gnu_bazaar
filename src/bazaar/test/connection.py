# $Id: connection.py,v 1.2 2004/12/20 07:39:52 wrobell Exp $
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

import bazaar.core
import bazaar.config

import bazaar.test.app
import bazaar.test.bzr

"""
Test layer database connection management.
"""

class ConnTestCase(bazaar.test.TestCase):
    """
    Test layer database connection managment.
    """
    def testConnection(self):
        """Test database connection initialization"""

        config = bazaar.config.CPConfig(self.config)
        self.bazaar.connectDB(config.getDSN())
        self.assert_(self.bazaar.motor.conn, 'db connection is missing')
        # simple query
        self.bazaar.motor.conn.cursor().execute('begin; rollback')


    def testConnectionClosing(self):
        """Test database connection closing"""

        config = bazaar.config.CPConfig(self.config)
        self.bazaar.connectDB(config.getDSN())
        self.bazaar.closeDBConn()

        self.assert_(not self.bazaar.motor.conn, 'db connection should not be set')


if __name__ == '__main__':
    bazaar.test.main()
