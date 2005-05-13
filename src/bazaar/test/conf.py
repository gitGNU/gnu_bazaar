# $Id: conf.py,v 1.7 2005/05/13 17:15:58 wrobell Exp $
#
# Bazaar ORM - an easy to use and powerful abstraction layer between relational
# database and object oriented application.
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

import unittest

import bazaar.conf
import bazaar.assoc

import bazaar.test.app

"""
Test mapping application classes to database relations.
"""

class ConfTestCase(unittest.TestCase):
    """
    Test class defining.
    """

    def testClassDef(self):
        """Test application class to database relation mapping"""

        relation = 'person'
        Person = bazaar.conf.Persistence('Person', 'person', globals())
        self.assertEqual(relation, Person.relation,
            'class relation mismatch: %s != %s ' % (relation, Person.relation))
        self.assertEqual(Person.__module__, __name__,
            'class module mismatch: %s != %s ' % (Person.__module__, __name__))

        relation = 'address'
        class Address:
            __metaclass__ = bazaar.conf.Persistence
            relation  = 'address'

        self.assertEqual(relation, Address.relation,
            'class relation mismatch: %s != %s ' % (relation, Address.relation))
        self.assertEqual(Address.__module__, __name__,
            'class module mismatch: %s != %s ' % (Address.__module__, __name__))

        Person = bazaar.conf.Persistence('Person',
            (bazaar.core.PersistentObject,), globals())
        self.assertEqual('Person', Person.relation,
            'class relation mismatch: %s != %s ' % ('Person', Person.relation))
        self.assertEqual(Person.__bases__, (bazaar.core.PersistentObject,))

        self.assertRaises(bazaar.exc.RelationMappingError,
                bazaar.conf.Persistence, 'name', ['relation'], globals())


    def testColumnDef(self):
        """Test database relation columns defining"""

        cols = ('name', 'surname', 'birthdate')

        Person = bazaar.conf.Persistence('Person', 'person', globals())
        Person.addColumn('name')
        self.assertRaises(bazaar.exc.ColumnMappingError, Person.addColumn, 'name')
        Person.addColumn('surname')
        Person.addColumn('birthdate')

        for col in cols:
            self.assert_(col in Person.columns, 'column "%s" not found' % col)


    def testInheritance(self):
        """Test class inheritance"""
        A = bazaar.conf.Persistence('A', 'a', globals())
        A.addColumn('a1')
        A.addColumn('a2')

        B = bazaar.conf.Persistence('B', 'b', globals(), bases = (A,))
        B.addColumn('b1')
        B.addColumn('b2')
        self.assertEqual(B.defaults, {'a1': None, 'a2': None, 'b1': None, 'b2': None})

        C = bazaar.conf.Persistence('C', 'c', globals())
        C.addColumn('c1')
        C.addColumn('c2')

        D = bazaar.conf.Persistence('D', 'd', globals(), bases = (B, C))
        D.addColumn('d1')
        D.addColumn('d2')
        self.assertEqual(D.defaults, \
            {'a1': None, 'a2': None, 
             'b1': None, 'b2': None,
             'c1': None, 'c2': None, 
             'd1': None, 'd2': None,
        })

        self.assertEqual(list(B.__bases__), [A])

        d_bases = [c.__name__ for c in D.__bases__]
        
        self.assertEqual(d_bases, ['B', 'C'])

        a_cols = A.getColumns().keys()
        a_cols.sort()

        self.assertEqual(a_cols, ['a1', 'a2'])

        b_cols = B.getColumns().keys()
        b_cols.sort()
        self.assertEqual(b_cols, ['a1', 'a2', 'b1', 'b2'])

        c_cols = C.getColumns().keys()
        c_cols.sort()

        self.assertEqual(c_cols, ['c1', 'c2'])

        d_cols = D.getColumns().keys()
        d_cols.sort()
        self.assertEqual(d_cols, ['a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2'])


    def testDefaultValues(self):
        """Test default value setting"""

        A = bazaar.conf.Persistence('A', 'a', globals())
        A.addColumn('a1')
        A.addColumn('a2')
        self.assertEqual(A.defaults, {'a1': None, 'a2': None})

        B = bazaar.conf.Persistence('B', 'b', globals(), bases = (A,))
        B.addColumn('b1')
        B.addColumn('b2')
        self.assertEqual(B.defaults, {'a1': None, 'a2': None, 'b1': None, 'b2': None})

        data = globals().copy()
        data['defaults'] = {'a1': 1}
        A = bazaar.conf.Persistence('A', 'a', data)
        A.addColumn('a1')
        A.addColumn('a2')
        self.assertEqual(A.defaults, {'a1': 1, 'a2': None})

        a = A()
        self.assertEqual(a.a1, 1)
        self.assertEqual(a.a2, None)

        a = A(a1 = 2) # override default value
        self.assertEqual(a.a1, 2)

        B = bazaar.conf.Persistence('B', 'b', globals(), bases = (A,))
        B.addColumn('b1')
        B.addColumn('b2', default = 4)
        self.assertEqual(B.defaults, {'a1': 1, 'a2': None, 'b1': None, 'b2': 4})

        b = B()
        self.assertEqual(b.a1, 1)
        self.assertEqual(b.a2, None)
        self.assertEqual(b.b1, None)
        self.assertEqual(b.b2, 4)

        b = B(a1 = 3) # override default value
        self.assertEqual(b.a1, 3)


class AssociationTestCase(unittest.TestCase):
    """
    Test association defining.
    """

    def testAssociationDef(self):
        """Test association defining"""
        class Abase:
            __metaclass__ = bazaar.conf.Persistence
            relation = 'abase'

        class A(Abase):
            __metaclass__ = bazaar.conf.Persistence
            relation = 'a'
            columns       = {
                'a1' : bazaar.conf.Column('a1'),
                'a2' : bazaar.conf.Column('a2'),
            }

        class B:
            __metaclass__ = bazaar.conf.Persistence
            relation = 'b'
            columns       = {
                'b1' : bazaar.conf.Column('b1'),
            }

        class C:
            __metaclass__ = bazaar.conf.Persistence
            relation = 'b'
            columns       = {
                'c1' : bazaar.conf.Column('c1'),
                'c2' : bazaar.conf.Column('c1'),
            }

        def check(cls, attr, descriptor, properties, msg):
            col = cls.getColumns()[attr]
            self.assertEqual(type(col.association), \
                descriptor, 'it should be %s association' % msg)
            self.assertEqual(col.association, getattr(cls, attr), \
                'application class association descriptor mismatch')
            for prop in properties:
                self.assertEqual(getattr(col, prop), True, 'it should be %s association: %s' % (msg, prop))


        cls_list = (A, B, C)

        A.addColumn('a3', 'a3_fkey', B)
        bzr = bazaar.core.Bazaar(cls_list)
        check(A, 'a3', bazaar.assoc.OneToOne, ['is_one_to_one'], 'uni-directional one-to-one')

        A.addColumn('a5', 'a5_fkey', B, vattr = 'b5')
        B.addColumn('b5', 'b5_fkey', A, vattr = 'a5')
        bzr = bazaar.core.Bazaar(cls_list)
        check(A, 'a5', bazaar.assoc.BiDirOneToOne, ['is_one_to_one'], 'bi-directional one-to-one')
        check(B, 'b5', bazaar.assoc.BiDirOneToOne, ['is_one_to_one'], 'bi-directional one-to-one')

        A.addColumn('a6', 'a61', B, 'a__b', 'b61')
        bzr = bazaar.core.Bazaar(cls_list)
        check(A, 'a6', bazaar.assoc.List, ['is_many_to_many', 'is_many'], 'uni-directional many-to-many')

        A.addColumn('a7', vcls = B, vcol = 'b71', vattr = 'b7')
        B.addColumn('b7', 'b71', A, vattr = 'a7')
        bzr = bazaar.core.Bazaar(cls_list)
        check(A, 'a7', bazaar.assoc.OneToMany, ['is_one_to_many', 'is_many'], 'many side bi-dir one-to-many')
        check(B, 'b7', bazaar.assoc.BiDirOneToOne, ['is_one_to_one', 'is_bidir'], 'one side bi-dir one-to-many')

        A.addColumn('a8', vcls = B, vcol = 'b81', vattr = 'b8')
        B.addColumn('b8', 'b81', A, vattr = 'a8')
        bzr = bazaar.core.Bazaar((C, B, A))
        check(A, 'a8', bazaar.assoc.OneToMany, ['is_one_to_many', 'is_many'], 'many side bi-dir one-to-many')
        check(B, 'b8', bazaar.assoc.BiDirOneToOne, ['is_one_to_one', 'is_bidir'], 'one side bi-dir one-to-many')

        # test associations inherited from base classes
        Abase.addColumn('a9', 'a9_fkey', B)
        bzr = bazaar.core.Bazaar(cls_list)
        check(A, 'a9', bazaar.assoc.OneToOne, ['is_one_to_one'], 'uni-directional one-to-one')


if __name__ == '__main__':
    import bazaar.test
    bazaar.test.main()
