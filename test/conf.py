# $Id: conf.py,v 1.8 2003/09/19 14:56:46 wrobell Exp $

import unittest

import bazaar.conf
import bazaar.assoc

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
        try:
            Person.addColumn('name')
        except ValueError, exc:
            self.assertEqual(str(exc), 'column "name" is already defined in class "Person"')
        else:
            self.fail('adding the column twice should fail')

        Person.addColumn('surname')
        Person.addColumn('birthdate')

        for col in cols:
            self.assert_(col in Person.columns, 'column "%s" not found' % col)


    def testKeyDef(self):
        """Test database relation key defining"""

        Person = bazaar.conf.Persistence('Person', relation = 'person')
        Person.addColumn('name')
        Person.addColumn('surname')
        Person.addColumn('birthdate')

        Person.setKey(('name', 'surname', 'birthdate'))
        self.assertEqual(len(Person.key_columns), 3, 'there should be three key columns')
        self.assertEqual(Person.key_columns, \
            ('name', 'surname', 'birthdate'), 'key column mismatch')

        Person.setKey(('name', ))
        self.assertEqual(len(Person.key_columns), 1, 'there should be one key column')
        self.assertEqual(Person.key_columns, ('name', ), 'key column mismatch')

        Person.setKey(('name', 'surname'))
        self.assertEqual(len(Person.key_columns), 2, 'there should be two key columns')
        self.assertEqual(Person.key_columns, ('name', 'surname'), 'key column mismatch')

        try:
            Person.setKey(('foo', 'bar'))
        except ValueError, exc:
            self.assertEqual(str(exc), 'key\'s column "foo" not found on list of relation columns')
        else:
            self.fail('setting key with non-existing columns should fail')

        try:
            Person.setKey(())
        except ValueError, exc:
            self.assertEqual(str(exc), 'list of key\'s columns should not be empty')
        else:
            self.fail('setting empty key should fail')



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
            key_columns = ('a1', )

        class B:
            __metaclass__ = bazaar.conf.Persistence
            relation = 'b'
            columns       = {
                'b1' : bazaar.conf.Column('b1'),
            }
            key_columns = ('b1', )

        class C:
            __metaclass__ = bazaar.conf.Persistence
            relation = 'b'
            columns       = {
                'c1' : bazaar.conf.Column('c1'),
                'c2' : bazaar.conf.Column('c1'),
            }
            key_columns = ('c1', 'c2')

        def check(cls, col, attr, descriptor, msg):
            self.assertEqual(type(cls.columns[col].association), descriptor, \
                'it should be %s association' % msg)
            self.assertEqual(cls.columns[col].association, getattr(cls, attr), \
                'application class association descriptor mismatch')

        A.addColumn('a3_fkey', 'a3', B, ('aa31',))
        A.addColumn('a4_fkey', 'a4', C, ('aa41', 'aa42'))
        check(A, 'a3_fkey', 'a3', bazaar.assoc.UniDirOneToOneAssociation, \
                'uni-directional one-to-one')
        check(A, 'a4_fkey', 'a4', bazaar.assoc.UniDirOneToOneAssociation, \
                'uni-directional one-to-one')

        A.addColumn('a5_fkey', 'a5', B, ('aa51',), bidir = 'b5_fkey')
        B.addColumn('b5_fkey', 'b5', A, ('bb51',), bidir = 'a5_fkey')
        check(A, 'a5_fkey', 'a5', bazaar.assoc.BiDirOneToOneAssociation, \
                'bi-directional one-to-one')
        check(B, 'b5_fkey', 'b5', bazaar.assoc.BiDirOneToOneAssociation, \
                'bi-directional one-to-one')
