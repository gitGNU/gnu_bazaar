# $Id: conf.py,v 1.11 2003/09/28 15:56:21 wrobell Exp $

import unittest

import bazaar.conf
import bazaar.assoc

import app

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
        Person = bazaar.conf.Persistence('Person', relation = 'person')
        self.assertEqual(relation, Person.relation,
            'class relation mismatch: %s != %s ' % (relation, Person.relation))

        relation = 'address'
        class Address:
            __metaclass__ = bazaar.conf.Persistence
            relation  = 'address'

        self.assertEqual(relation, Address.relation,
            'class relation mismatch: %s != %s ' % (relation, Address.relation))


    def testColumnDef(self):
        """Test database relation columns defining"""

        cols = ('name', 'surname', 'birthdate')

        Person = bazaar.conf.Persistence('Person', relation = 'person')
        Person.addColumn('name')
        self.assertRaises(bazaar.exc.ColumnMappingError, Person.addColumn, 'name')
        Person.addColumn('surname')
        Person.addColumn('birthdate')

        for col in cols:
            self.assert_(col in Person.columns, 'column "%s" not found' % col)



class AssociationTestCase(unittest.TestCase):
    """
    Test association defining.
    """

    def testAssociationDef(self):
        """Test association defining"""

        class A:
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

        def check(cls, attr, descriptor, msg):
            self.assertEqual(type(cls.columns[attr].association), descriptor, \
                'it should be %s association' % msg)
            self.assertEqual(cls.columns[attr].association, getattr(cls, attr), \
                'application class association descriptor mismatch')

        cls_list = (A, B, C)

        A.addColumn('a3', 'a3_fkey', B)
        bzr = bazaar.core.Bazaar(cls_list, app.db_module)
        check(A, 'a3', bazaar.assoc.OneToOne, 'uni-directional one-to-one')

        A.addColumn('a5', 'a5_fkey', B, vattr = 'b5')
        B.addColumn('b5', 'b5_fkey', A, vattr = 'a5')
        bzr = bazaar.core.Bazaar(cls_list, app.db_module)
        check(A, 'a5', bazaar.assoc.BiDirOneToOne, 'bi-directional one-to-one')
        check(B, 'b5', bazaar.assoc.BiDirOneToOne, 'bi-directional one-to-one')

        A.addColumn('a6', 'a61', B, 'a__b', 'b61')
        bzr = bazaar.core.Bazaar(cls_list, app.db_module)
        check(A, 'a6', bazaar.assoc.List, 'bi-directional many-to-many')

        A.addColumn('a7', vcls = B, vcol = 'b71', vattr = 'b7')
        B.addColumn('b7', 'b71', A, vattr = 'a7')
        bzr = bazaar.core.Bazaar(cls_list, app.db_module)
        check(A, 'a7', bazaar.assoc.BiDirList, 'many side bi-dir one-to-many')
        check(B, 'b7', bazaar.assoc.BiDirOneToOne, 'one side bi-dir one-to-many')

        A.addColumn('a8', vcls = B, vcol = 'b81', vattr = 'b8')
        B.addColumn('b8', 'b81', A, vattr = 'a8')
        bzr = bazaar.core.Bazaar((C, B, A), app.db_module)
        check(A, 'a8', bazaar.assoc.BiDirList, 'many side bi-dir one-to-many')
        check(B, 'b8', bazaar.assoc.BiDirOneToOne, 'one side bi-dir one-to-many')
