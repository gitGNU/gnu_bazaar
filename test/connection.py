# $Id: connection.py,v 1.6 2004/01/22 23:21:41 wrobell Exp $
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

import bazaar.core

import app
import btest

"""
Test layer database connection management.
"""

class ConnTestCase(btest.BazaarTestCase):
    """
    Test layer database connection managment.
    """
    def testConnection(self):
        """Test database connection initialization"""

        self.bazaar.connectDB(app.dsn)
        self.assert_(self.bazaar.motor.conn, 'db connection is missing')
        # simple query
        self.bazaar.motor.conn.cursor().execute('begin; rollback')


    def testConnectionClosing(self):
        """Test database connection closing"""

        self.bazaar.connectDB(app.dsn)
        self.bazaar.closeDBConn()

        self.assert_(not self.bazaar.motor.conn, 'db connection should not be set')
