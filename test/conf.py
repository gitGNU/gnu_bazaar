# $Id: conf.py,v 1.1 2003/06/18 23:33:53 wrobell Exp $

import unittest
import logging

import bazaar.conf

"""
<s>Test mapping application classes to database relations.</s>
"""

log = logging.getLogger('bazaar.test.core')

class ConfTestCase(unittest.TestCase):
    """
    <s>Test class defining.</s>
    """

    def testClassDef(self):
        """
        <s>Test application class to database relation mapping.</s>
        """

        log.info('begin testing class defining')

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

        log.info('finished testing class defining')


    def testColumnDef(self):
        """
        <s>Test database relation columns defining.</s>
        """

        log.info('begin testing db relation columns defining')

        cols = ('name', 'surname', 'birthdate')

        Person = bazaar.conf.Persitence('Person', relation = 'person')
        Person.addColumn('name')
        try:
            Person.addColumn('name')
        except AttributeError, exc:
            log.info('adding the column twice failed <- it is ok!')
        else:
            self.fail('adding the column twice should fail')

        Person.addColumn('surname')
        Person.addColumn('birthdate')

        for col in cols:
            self.assert_(col in Person.columns, 'column "%s" not found' % col)

        log.info('finished testing db relation columns defining')


    def testKeyDef(self):
        """
        <s>Test database relation key defining.</s>
        """
        log.info('begin testing db relation key defining')

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

        log.info('finished testing db relation key defining')



if __name__ == '__main__':
    unittest.main()
