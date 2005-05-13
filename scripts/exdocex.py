#!/usr/bin/python
#
# $Id: exdocex.py,v 1.7 2005/05/13 00:40:06 wrobell Exp $
#
# Bazaar - an easy to use and powerful abstraction layer between relational
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

import unittest
import doctest

import logging.config

logging.config.fileConfig('log.ini')

suite = unittest.TestSuite()

mods = ('bazaar', 'bazaar.conf', 'bazaar.assoc', 'bazaar.cache',
        'bazaar.config', 'bazaar.core', 'bazaar.exc', 'bazaar.motor')

for modname in mods:
    mod = __import__(modname, globals(), locals(), [''])
    suite.addTest(doctest.DocTestSuite(mod))

runner = unittest.TextTestRunner()
runner.run(suite)
