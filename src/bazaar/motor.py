# $Id: motor.py,v 1.24 2003/11/25 16:27:48 wrobell Exp $
"""
Data convertor and database access classes.
"""

import logging

log = logging.getLogger('bazaar.motor')

class Convertor:
    """
    Relational and object data convertor.

    @ivar queries: Queries to modify data in database.
    @ivar cls: Application class, which objects are converted.
    @ivar motor: Database access object.
    @ivar columns: List of columns used with database queries.
    """
    def __init__(self, cls, mtr):
        """
        Create data convert object.
        """
        self.queries = {}
        self.cls = cls
        self.motor = mtr

        cls_columns = self.cls.getColumns().values()
        self.columns = [col.col for col in cls_columns if col.association is None]

        self.oto_ascs = [col for col in cls_columns if col.is_one_to_one]
        for col in self.oto_ascs:
            self.columns.append(col.col)

        if __debug__: log.debug('class %s columns: %s' % (self.cls, self.columns))

        self.mtm_ascs = [col for col in cls_columns if col.is_many_to_many]

        self.load_cols = ['__key__'] + self.columns

        # used to get values of object's loaded data
        self.itercols = range(len(self.load_cols))

        #
        # prepare queries
        #
        self.queries[self.getObjects] = 'select %s from "%s"' \
            % (', '.join(['"%s"' % col for col in self.load_cols]), self.cls.relation)
        if __debug__: log.debug('get objects query: "%s"' % self.queries[self.getObjects])

        self.queries[self.get] = self.queries[self.getObjects] \
            + ' where __key__ = %s'
        if __debug__: log.debug('get single object query: "%s"' % self.queries[self.get])

        self.queries[self.add] = 'insert into "%s" (__key__, %s) values (%%(__key__)s, %s)' \
            % (self.cls.relation,
               ', '.join(['"%s"' % col for col in self.columns]),
               ', '.join(['%%(%s)s' % col for col in self.columns])
              )
        if __debug__: log.debug('add object query: "%s"' % self.queries[self.add])

        self.queries[self.update] = 'update "%s" set %s where __key__ = %%s' \
            % (self.cls.relation, ', '.join(['"%s" = %%s' % col for col in self.columns]))
        if __debug__: log.debug('update object query: "%s"' % self.queries[self.update])

        self.queries[self.delete] = 'delete from "%s" where __key__ = %%s' % self.cls.relation
        if __debug__: log.debug('delete object query: "%s"' % self.queries[self.delete])

        self.queries[self.motor.getKey] = 'select nextval(\'%s\')' % self.cls.sequencer # fixme, use seqpattern
        if __debug__: log.debug('get primary key value query: "%s"' % self.queries[self.motor.getKey])

        self.asc_cols = {}
        for col in self.mtm_ascs:

            assert col.association.col.vcls == col.vcls

            asc = col.association
            self.queries[asc] = {}

            self.asc_cols[asc] = (col.col, col.vcol)
            relation = col.link

            self.queries[asc][self.addPair] = 'insert into "%s" (%s) values(%s)' % \
                (relation,
                 ', '.join(['"%s"' % c for c in self.asc_cols[asc]]),
                 ', '.join(('%s', ) * len(self.asc_cols[asc]))
                )
            self.queries[asc][self.delPair] = 'delete from "%s" where %s' % \
                (relation, ' and '.join(['"%s" = %%s' % c for c in self.asc_cols[asc]]))

            self.queries[asc][self.getPair] = 'select %s from "%s"' % \
                (', '.join(['"%s"' % c for c in self.asc_cols[asc]]), relation)

            if __debug__:
                log.debug('association load query: "%s"' % \
                        self.queries[asc][self.getPair])
            if __debug__:
                log.debug('association insert query: "%s"' % \
                        self.queries[asc][self.addPair])

            if __debug__:
                log.debug('association delete query: "%s"' % \
                        self.queries[asc][self.delPair])

        self.queries[self.find] = 'select __key__ from "%s" where %%s' % self.cls.relation
        if __debug__: log.debug('object OO find query: "%s"' % self.queries[self.find])


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
        return ' and '.join(['"%s" = %%(%s)s' % (col, col) for col in param])


    def objToData(self, param):
        """
        Convert object oriented parameters to pure relational data.

        @see: L{bazaar.core.Bazaar.find}
        """
        import bazaar.core # fixme

        data = {}
        cols = self.cls.columns
        for attr, value in param.items():
            # change class attribute and object value pair into relation
            # column and primary key value
            if attr in cols:
                attr = cols[attr].col
            if isinstance(value, bazaar.core.PersistentObject):
                value = value.__key__

            data[attr] = value

        return data


    def addPair(self, asc, pairs):
        """
        fixme
        """
        if __debug__: log.debug('association %s.%s->%s: adding pairs' % (asc.broker.cls, asc.col.attr, asc.col.vcls))
        self.motor.executeMany(self.queries[asc][self.addPair], pairs)
        if __debug__: log.debug('association %s.%s->%s: pairs added' % (asc.broker.cls, asc.col.attr, asc.col.vcls))


    def delPair(self, asc, pairs):
        """
        fixme
        """
        if __debug__: log.debug('association %s.%s->%s: deleting pairs' % (asc.broker.cls, asc.col.attr, asc.col.vcls))
        self.motor.executeMany(self.queries[asc][self.delPair], pairs)
        if __debug__: log.debug('association %s.%s->%s: pairs deleted' % (asc.broker.cls, asc.col.attr, asc.col.vcls))


    def getPair(self, asc):
        """
        fixme
        """
        okey, vkey = self.asc_cols[asc] # fixme: is this still required
        for data in self.motor.getData(self.queries[asc][self.getPair]):
            yield data[0], data[1]


    def find(self, query, param = None, field = 0):
        """
        Find objects in database.

        @see L{bazaar.core.Bazaar.find}
        """
        if isinstance(query, dict):
            param = query

        param = self.objToData(param)

        if isinstance(query, dict):
            query = self.queries[self.find] % self.dictToSQL(param)

        assert isinstance(query, str) and isinstance(param, dict) \
            and isinstance(field, int)

        if __debug__:
            log.debug('find objects with query: \'%s\', params %s, field %d' \
                % (query, param, field))

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

        @param key: Primary key value of object to load.
        """
        return self.createObject( \
            self.motor.getData(self.queries[self.get], (key, )).next())


    def add(self, obj):
        """
        Add object to database.

        @param obj: Object to add.
        """
        data = self.getData(obj)
        key = self.motor.getKey(self.queries[self.motor.getKey])
        data['__key__'] = key
        self.motor.add(self.queries[self.add], data)
        obj.__key__ = key
 

    def update(self, obj):
        """
        Update object in database.

        @param obj: Object to update.
        """
        data = self.getData(obj)
        
        self.motor.update(self.queries[self.update], [data[col] for col in self.columns], obj.__key__)


    def delete(self, obj):
        """
        Delete object from database.

        @param obj: Object to delete.
        """
        self.motor.delete(self.queries[self.delete], obj.__key__)



class Motor:
    """
    Database access object.

    @ivar dbmod: Python DB API module.
    @ivar conn: Python DB API connection object.
    """
    def __init__(self, dbmod):
        """
        Initialize database access object.
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
        if __debug__: log.debug('connected to database with dsn "%s"' % dsn)


    def closeDBConn(self):
        """
        Close database connection.

        @see: L{bazaar.motor.Motor.connectDB}
        """
        self.conn.close()
        self.conn = None
        if __debug__: log.debug('close database connection')


    def getData(self, query, param = None):
        """
        Get list of rows from database.

        Method returns dictionary per databse relation row. The
        dictionary keys are relation column names and dictionary values
        are column values for the relation row.

        @param query: Database SQL query.
        """
        if __debug__: log.debug('query "%s", params %s: executing' % (query, param))

        if param is None: param = {}

        dbc = self.conn.cursor()
        dbc.execute(query, param)

        if __debug__: log.debug('query "%s": executed, rows = %d' % (query, dbc.rowcount))

        row = dbc.fetchone()
        while row:
            yield row
            row = dbc.fetchone()

        if __debug__: log.debug('query "%s": got all data, len = %d' % (query, dbc.rowcount))


    def add(self, query, data):
        """
        Insert row into database relation.

        @param query: SQL query.
        @param data: Row data to insert.
        """
        if __debug__: log.debug('query "%s", data = %s: executing' % (query, data))
        dbc = self.conn.cursor()
        dbc.execute(query, data)
        if __debug__: log.debug('query "%s", data = %s: executed' % (query, data))


    def update(self, query, data, key):
        """
        Update row in database relation.

        @param query: SQL query.
        @param data: Tuple of new values for the row.
        @param key: Key of the row to update.
        """
        if __debug__: log.debug('query "%s", data = %s, key = %s: executing' % (query, data, key))
        dbc = self.conn.cursor()
        dbc.execute(query, tuple(data) + (key, ))
        if __debug__: log.debug('query "%s", data = %s, key = %s: executed' % (query, data, key))


    def delete(self, query, key):
        """
        Delete row from database relation.

        @param query: SQL query.
        @param key: Key of the row to delete.
        """
        if __debug__: log.debug('query "%s", key = %s: executing' % (query, key))
        dbc = self.conn.cursor()
        dbc.execute(query, (key, ))
        if __debug__: log.debug('query "%s", key = %s: executed' % (query, key))


    def executeMany(self, query, iterator):
        """
        fixme
        """
        if __debug__: log.debug('query "%s": executing' % query)
        dbc = self.conn.cursor()
        dbc.executemany(query, iterator)
        if __debug__: log.debug('query "%s": executed' % query)


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


    def getKey(self, query):
        """
        """
        dbc = self.conn.cursor()
        dbc.execute(query)
        return dbc.fetchone()[0]
