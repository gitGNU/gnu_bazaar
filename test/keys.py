# $Id: keys.py,v 1.1 2003/09/12 14:55:56 wrobell Exp $

import unittest

import bazaar.core
import bazaar.conf

import app

"""
Test object loading and reloading from database.
"""

Bsingle = bazaar.conf.Persistence('Bsingle', relation = 'bsingle')
Bsingle.addColumn('b')
Bsingle.setKey(('b', ))

Bmulti = bazaar.conf.Persistence('Bmulti', relation = 'bmulti')
Bmulti.addColumn('b1')
Bmulti.addColumn('b2')
Bmulti.addColumn('b3')
Bmulti.setKey(('b1', 'b2', 'b3'))

A = bazaar.conf.Persistence('A', relation = 'a')
A.addColumn('a')
A.addColumn('bs_fkey', 'bsingle', Bsingle, ('bs_fkey',))
A.addColumn('bm_fkey', 'bmulti', Bmulti, ('bm1', 'bm2', 'bm3'))
A.setKey(('a', ))


class KeyTestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        """
        Create Bazaar layer instance and connect with database, then
        prepare object checking parameters.
        """
        self.cls_list = (A, Bsingle, Bmulti)
        self.bazaar = bazaar.core.Bazaar(self.cls_list, app.db_module)
        self.bazaar.connectDB(app.dsn)
        self.params = [
            { 
                'cls'     : A,
                'relation': 'a',
                'cols'    : ('a', 'bs_fkey', 'bm1', 'bm2', 'bm3'),
                'test'    : self.checkA
            },
            { 
                'cls'     : Bsingle,
                'relation': 'bsingle',
                'cols'    : ('b', ),
                'test'    : self.checkBsingle
            },
            { 
                'cls'     : Bmulti,
                'relation': 'bmulti',
                'cols'    : ('b1', 'b2', 'b3'),
                'test'    : self.checkBmulti
            }
        ]


    def testNotNullReference(self):
        """Test not null reference assignment"""
        a = A()
        a.a = 1
        bs = Bsingle()
        bs.b = 1
        a.bsingle = bs

        bm = Bmulti()
        bm.b1 = 1
        bm.b2 = 1
        bm.b3 = 1
        a.bmulti = bm

        self.bazaar.add(bs)
        self.bazaar.add(bm)
        self.bazaar.add(a)
        # todo: check if relations contain proper data


    def testNullReference(self):
        """Test null reference assignment"""
        a = A()
        a.a = 1
        a.bsingle = None
        a.bmulti = None
        self.bazaar.add(a)
        # todo: check if relations contain proper data


    def tearDown(self):
        """
        Close database connection.
        """
        self.bazaar.closeDBConn()
