# $Id: init.py,v 1.3 2005/05/12 18:29:58 wrobell Exp $
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

import bazaar.core
import bazaar.motor
import bazaar.config

import bazaar.test.app
import bazaar.test.bzr

"""
Test layer initialization.
"""

class InitTestCase(bazaar.test.bzr.TestCase):
    """
    Test layer initialization.
    """

    def testBazaarInit(self):
        """Test layer initialization"""


        cls_list = (bazaar.test.app.Order, bazaar.test.app.Employee, bazaar.test.app.Article, bazaar.test.app.OrderItem)

        b = bazaar.core.Bazaar(cls_list, bazaar.config.CPConfig(self.config))

        self.assertNotEqual(b.motor, None, 'Motor object does not exist')
        self.assert_(isinstance(b.motor, bazaar.motor.Motor), 'Motor object class mismatch')

        for cls in cls_list:
            self.assert_(cls in b.brokers, 'class "%s" not found in broker list' % cls)
            self.assertEqual(cls, b.brokers[cls].cls, 'broker class mismatch')

        # there should be no connection, now
        self.assert_(not b.motor.conn, 'there should be no db connection')


    def testConnection(self):
        """Test layer initialization and database connection"""


        cls_list = (bazaar.test.app.Order, bazaar.test.app.Employee, bazaar.test.app.Article, bazaar.test.app.OrderItem)

        # init bazaar layer with connection
        b = bazaar.core.Bazaar(cls_list, bazaar.config.CPConfig(self.config))
        b.connectDB()
        self.assert_(b.motor.conn, 'db connection is missing')
        
        # simple query
        b.motor.conn.cursor().execute('begin; rollback')



if __name__ == '__main__':
    bazaar.test.main()
