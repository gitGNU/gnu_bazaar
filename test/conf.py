# $Id: conf.py,v 1.6 2003/08/27 15:22:38 wrobell Exp $

import unittest

import bazaar.conf

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
        Person = bazaar.conf.Persitence('Person', relation = 'person')
        self.assertEqual(relation, Person.relation,
            'class relation mismatch: %s != %s ' % (relation, Person.relation))

        relation = 'address'
        class Address:
            __metaclass__ = bazaar.conf.Persitence
            relation  = 'address'

        self.assertEqual(relation, Address.relation,
            'class relation mismatch: %s != %s ' % (relation, Address.relation))


    def testColumnDef(self):
        """Test database relation columns defining"""

        cols = ('name', 'surname', 'birthdate')

        Person = bazaar.conf.Persitence('Person', relation = 'person')
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

        Person = bazaar.conf.Persitence('Person', relation = 'person')
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
