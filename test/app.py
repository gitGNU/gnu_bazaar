# $Id: app.py,v 1.1 2003/07/10 23:03:43 wrobell Exp $

"""
<s>Sample test application for Bazaar layer testing purposes.</s>
"""

import bazaar.conf

db_module = None
dsn = ''

# define test application classes
Person = bazaar.conf.Persitence('Person', relation = 'person')
Person.addColumn('id')
Person.addColumn('name')
Person.setKey(('id', ))

Address = bazaar.conf.Persitence('Address', relation = 'address')
