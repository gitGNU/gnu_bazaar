# $Id: motor.py,v 1.37 2005/05/29 18:41:11 wrobell Exp $
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
"""
Data convertor and database access classes.
"""

import bazaar.core   # it is required to check if objects are
                     # PersistentObject class' instances

log = bazaar.Log('bazaar.motor')

class Convertor(object):
    """
    Relational and object data convertor.

    The class creates all required SQL queries. It converts relational data
    to object oriented form and vice versa.
    
    L{Motor} class is used to connect and execute commands in database.

    @ivar queries: Queries to modify data in database.
    @ivar cls: Application class, which objects are converted.
    @ivar motor: Database access object.
    @ivar columns: List of columns used with database queries.
    """
    def __init__(self, cls, mtr, seqpattern = None):
        """
        Create data convertor object.

        @param cls: Application class.
        @param mtr: L{Motor} class object.
        """
        self.queries = {}
        self.cls = cls
        self.motor = mtr

        cls_columns = self.cls.getColumns().values()

        self.columns = \
            [col for col in cls_columns if col.association is None]

        self.oto_ascs = [col for col in cls_columns if col.is_one_to_one]
        for col in self.oto_ascs:
            self.columns.append(col)

        if __debug__:
            log.debug('class %s columns: %s' \
                % (self.cls, [col.col for col in self.columns]))

        self.masc = [col for col in cls_columns if col.is_many]

        self.load_cols = ['__key__'] \
            + [col.col for col in self.columns if col.readable]
        self.save_cols = [col.col for col in self.columns if col.writable]

        # used to get values of object's loaded data
        self.itercols = range(len(self.load_cols))

        #
        # prepare queries
        #
        self.queries[self.getKey] = seqpattern % self.cls.sequencer
        if __debug__: log.debug('get next value of sequencer query: "%s"' % \
            self.queries[self.getKey])

        self.queries[self.getObjects] = 'select %s from "%s"' \
            % (', '.join(['"%s"' % col for col in self.load_cols]),
                self.cls.relation)

        if __debug__:
            log.debug('get objects query: "%s"' % self.queries[self.getObjects])

        self.queries[self.get] = self.queries[self.getObjects] \
            + ' where __key__ = %s'

        if __debug__:
            log.debug('get single object query: "%s"' % self.queries[self.get])

        self.queries[self.add] = \
            'insert into "%s" (__key__, %s) values (%%(__key__)s, %s)' \
            % (self.cls.relation,
               ', '.join(['"%s"' % col for col in self.save_cols]),
               ', '.join(['%%(%s)s' % col for col in self.save_cols])
              )

        if __debug__:
            log.debug('add object query: "%s"' % self.queries[self.add])

        self.queries[self.update] = 'update "%s" set %s where __key__ = %%s' \
            % (self.cls.relation,
            ', '.join(['"%s" = %%s' % col for col in self.save_cols]))

        if __debug__:
            log.debug('update object query: "%s"' % self.queries[self.update])

        self.queries[self.delete] = \
            'delete from "%s" where __key__ = %%s' % self.cls.relation

        if __debug__:
            log.debug('delete object query: "%s"' % self.queries[self.delete])

        self.asc_cols = {}

        for col in self.masc:
            assert col.association.col.vcls == col.vcls

            asc = col.association
            self.queries[asc] = {}

            if col.is_many_to_many:
                self.asc_cols[asc] = (col.col, col.vcol)
                relation = col.link

                self.queries[asc][self.getAscData] = \
                    'select "%s" from "%s" where "%s" = %%(key)s' % \
                    (self.asc_cols[asc][1], relation, \
                    self.asc_cols[asc][0])

            elif col.is_one_to_many:
                self.asc_cols[asc] = ('__key__', col.vcol)
                relation = col.vcls.relation

                self.queries[asc][self.getAscData] = \
                    'select "%s" from "%s" where "%s" = %%(key)s' % \
                    (self.asc_cols[asc][0], relation, \
                    self.asc_cols[asc][1])
            else:
                assert False

            self.queries[asc][self.addAscData] = \
                'insert into "%s" (%s) values(%s)' \
                % (relation,
                ', '.join(['"%s"' % c for c in self.asc_cols[asc]]),
                ', '.join(('%s', ) * len(self.asc_cols[asc])))

            self.queries[asc][self.delAscData] = 'delete from "%s" where %s' \
                % (relation,
                ' and '.join(['"%s" = %%s' % c for c in self.asc_cols[asc]]))

            self.queries[asc][self.getAllAscData] = 'select %s from "%s"' \
                % (', '.join(['"%s"' % c for c in self.asc_cols[asc]]),
                relation)

            if __debug__:
                log.debug('association load query: "%s"' \
                    % self.queries[asc][self.getAllAscData])

            if __debug__:
                log.debug('association load query: "%s"' \
                    % self.queries[asc][self.getAscData])

            if __debug__:
                log.debug('association insert query: "%s"' \
                    % self.queries[asc][self.addAscData])

            if __debug__:
                log.debug('association delete query: "%s"' \
                    % self.queries[asc][self.delAscData])

        self.queries[self.find] = \
            'select __key__ from "%s" where %%s' % self.cls.relation

        if __debug__:
            log.debug('object OO find query: "%s"' % self.queries[self.find])


    def getData(self, obj):
        """
        Extract relational data from application object.

        @param obj: Application object.

        @return: Dictionary of object's relational data.
        """
        # get attribute values
        data = obj.__dict__.copy()

        # get one-to-one association foreign key values
        for col in self.oto_ascs:
            value = getattr(obj, col.attr)
            if value is None:
                data[col.col] = None
            else:
                data[col.col] = value.__key__
        return data


    def dictToSQL(self, param):
        """
        Convert dictionary into C{WHERE} SQL clause.

        All dictionary items are glued with C{AND} operator.

        @see: L{bazaar.core.Bazaar.find}
        """
        cols = self.cls.getColumns()
        cond = []
        for attr in param:
            if attr in cols:
                col = cols[attr].col
            else:
                col = attr
            cond.append('"%s" = %%(%s)s' % (col, attr))
        return ' and '.join(cond)


    def objToData(self, param):
        """
        Convert object oriented parameters to pure relational data.

        @see: L{bazaar.core.Bazaar.find}
        """
        data = {}
        if param is not None:
            for attr, value in param.items():
                # change persistent objects with primary key value
                if isinstance(value, bazaar.core.PersistentObject):
                    value = value.__key__

                data[attr] = value

        return data


    def addAscData(self, asc, pairs):
        """
        Add association relational data into database.

        Adding the data means adding data into link table of many to many
        association or updating appropriate column of one to many
        association.

        @param asc: Association descriptor object.
        @param pairs: List of association data - pairs of primary and
            foreign key values.
        """
        if __debug__:
            log.debug('association %s.%s->%s: adding pairs' \
                % (asc.broker.cls, asc.col.attr, asc.col.vcls))

        self.motor.executeMany(self.queries[asc][self.addAscData], pairs)

        if __debug__:
            log.debug('association %s.%s->%s: pairs added' \
                % (asc.broker.cls, asc.col.attr, asc.col.vcls))


    def delAscData(self, asc, pairs):
        """
        Delete association relational data from database.

        Deleting the data means removing data from link table of many to
        many association. In case of one to many association it means
        deleting rows of relation on "many" side or updating
        appropriate column of one to many association to None value
        (it depends on relationship configuration).

        @param asc: Association descriptor object.
        @param pairs: List of association data - pairs of primary and
            foreign key values.
        """
        if __debug__:
            log.debug('association %s.%s->%s: deleting pairs' \
                % (asc.broker.cls, asc.col.attr, asc.col.vcls))

        self.motor.executeMany(self.queries[asc][self.delAscData], pairs)

        if __debug__:
            log.debug('association %s.%s->%s: pairs deleted' \
                % (asc.broker.cls, asc.col.attr, asc.col.vcls))


    def getAllAscData(self, asc):
        """
        Get all association data from database.

        @param asc: Association object.
        """
        for data in self.motor.getData(self.queries[asc][self.getAllAscData]):
            yield data[0], data[1]


    def getAscData(self, asc, obj):
        """
        Get association relational data for the application object.

        @param asc: Association object.
        @param obj: Application object.
        """
        for data in self.motor.getData(self.queries[asc][self.getAscData],
                { 'key': obj.__key__ }):
            yield data[0]


    def find(self, query, param = None, field = 0):
        """
        Find objects in database.

        @param query: SQL query or dictionary.
        @param param: SQL query parameters.
        @param field: SQL column number which describes found objects' primary
            key values.

        @see: L{bazaar.core.Bazaar.find}
        """
        # parameter mangling, part 1
        # two cases:
        # - when query argument is SQL query (string) then do nothing
        # - when query argument is dict, then SQL query will be created with
        #   magic - query argument specifies SQL query parametrs then
        if isinstance(query, dict):
            param = query

        param = self.objToData(param)

        # parameter mangling, part 2
        # - create SQL query
        if isinstance(query, dict):
            query = self.queries[self.find] % self.dictToSQL(param)

        assert isinstance(query, str) and isinstance(param, dict) \
            and isinstance(field, int)

        if __debug__:
            log.debug('find objects with query: \'%s\', params %s, field %d' \
                % (query, param, field))

        # get primary key values which denote objects
        for data in self.motor.getData(query, param):
            yield data[field]


    def createObject(self, data):
        """
        Create object from relational data.

        @param data: Relational data.

        @return: Created object.
        """
        obj = self.cls()              # create object instance
        for i in self.itercols:       # set values of object's attributes
            setattr(obj, self.load_cols[i], data[i])
        return obj


    def getObjects(self):
        """
        Load objects from database.
        """
        for data in self.motor.getData(self.queries[self.getObjects]):
            yield self.createObject(data)


    def get(self, key):
        """
        Load object from database.

        If there is no object, then C{None} is returned.

        @param key: Primary key value of object to load.
        """
        try:
            obj = self.createObject( \
                self.motor.getData(self.queries[self.get], (key, )).next())
        except StopIteration:
            obj = None
        return obj


    def getKey(self):
        """
        Create new primary key value with sequencer.

        @return: New primary key value.
        """
        return self.motor.getData(self.queries[self.getKey]).next()[0]


    def add(self, obj):
        """
        Add object to database.

        @param obj: Object to add.
        """
        data = self.getData(obj)
        key = self.getKey()       # create primary key value
        data['__key__'] = key
        self.motor.add(self.queries[self.add], data)
        obj.__key__ = key         # set primary key value
 

    def update(self, obj):
        """
        Update object in database.

        @param obj: Object to update.
        """
        data = self.getData(obj)
        
        self.motor.update(self.queries[self.update],
            [data[col] for col in self.save_cols],
            obj.__key__)


    def delete(self, obj):
        """
        Delete object from database.

        @param obj: Object to delete.
        """
        self.motor.delete(self.queries[self.delete], obj.__key__)



class Motor(object):
    """
    Database access object.

    The class depends od database API module - Python DB-API 2.0 in this
    case.

    @ivar dbmod: Python DB API module.
    @ivar conn: Python DB API connection object.
    """
    def __init__(self, dbmod):
        """
        Initialize database access object.

        @param dbmod: DB-API 2.0 module.
        """
        self.dbmod = dbmod
        self.conn = None
        log.info('Motor object initialized')


    def connectDB(self, dsn):
        """
        Connect with database.
        
        @param dsn: Data source name.

        @see: L{bazaar.motor.Motor.closeDBConn}
        """
        self.conn = self.dbmod.connect(dsn)
# what about password?
#        if __debug__: log.debug('connected to database with dsn "%s"' % dsn)
        if __debug__:
            log.debug('connected to database"')


    def closeDBConn(self):
        """
        Close database connection.

        @see: L{bazaar.motor.Motor.connectDB}
        """
        self.conn.close()
        self.conn = None
        if __debug__:
            log.debug('close database connection')


    def getData(self, query, param = None):
        """
        Get list of rows from database.

        Method returns dictionary per database relation row. The
        dictionary keys are relation column names and dictionary values
        are column values of the relation row.

        @param query: Database SQL query.
        """
        if __debug__:
            log.debug('query "%s", params %s: executing' % (query, param))

        if param is None:
            param = {}

        dbc = self.conn.cursor()
        dbc.execute(query, param)

        if __debug__:
            log.debug('query "%s": executed, rows = %d' % (query, dbc.rowcount))

        row = dbc.fetchone()
        while row:
            yield row
            row = dbc.fetchone()

        if __debug__:
            log.debug('query "%s": got all data, len = %d' \
                % (query, dbc.rowcount))


    def add(self, query, data):
        """
        Insert row into database relation.

        @param query: SQL query.
        @param data: Row data to insert.
        """
        if __debug__:
            log.debug('query "%s", data = %s: executing' % (query, data))

        dbc = self.conn.cursor()
        dbc.execute(query, data)

        if __debug__:
            log.debug('query "%s", data = %s: executed' % (query, data))


    def update(self, query, data, key):
        """
        Update row in database relation.

        @param query: SQL query.
        @param data: Tuple of new values for the row.
        @param key: Key of the row to update.
        """
        if __debug__:
            log.debug('query "%s", data = %s, key = %s: executing' \
                % (query, data, key))

        dbc = self.conn.cursor()
        dbc.execute(query, tuple(data) + (key, ))

        if __debug__:
            log.debug('query "%s", data = %s, key = %s: executed' \
                % (query, data, key))


    def delete(self, query, key):
        """
        Delete row from database relation.

        @param query: SQL query.
        @param key: Key of the row to delete.
        """
        if __debug__:
            log.debug('query "%s", key = %s: executing' % (query, key))

        dbc = self.conn.cursor()
        dbc.execute(query, (key, ))

        if __debug__:
            log.debug('query "%s", key = %s: executed' % (query, key))


    def executeMany(self, query, data_list):
        """
        Execute batch query with list of data parameters.

        @param query: Query to execute.
        @param data_list: List of query's data.
        """
        if __debug__:
            log.debug('query "%s": executing' % query)

        dbc = self.conn.cursor()
        dbc.executemany(query, data_list)

        if __debug__:
            log.debug('query "%s": executed' % query)


    def commit(self):
        """
        Commit pending database transactions.
        """
        self.conn.commit()


    def rollback(self):
        """
        Rollback database transactions.
        """
        self.conn.rollback()
