# $Id: motor.py,v 1.14 2003/09/22 00:21:05 wrobell Exp $
"""
Data convertor and database access objects.
"""

import logging

log = logging.getLogger('bazaar.motor')

class Convertor:
    """
    Data convertor.

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

        cls_columns = self.cls.columns.values()
        self.columns = [col.col for col in cls_columns if col.association is None]

        self.one_to_one_associations = [col for col in cls_columns if col.is_one_to_one]
        for col in self.one_to_one_associations:
            self.columns.append(col.col)

        if __debug__: log.debug('class %s columns: %s' % (self.cls, self.columns))

        self.many_to_many_associations = [col for col in cls_columns if col.is_many]

        #
        # prepare queries
        #
        self.queries[self.getObjects] = 'select "__key__", %s from "%s"' \
            % (', '.join(['"%s"' % col for col in self.columns]), self.cls.relation)

        if __debug__: log.debug('get object query: "%s"' % self.queries[self.getObjects])

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

        self.association_columns = {}
        for col in self.many_to_many_associations:

            assert col.association.col.vcls == col.vcls

            self.queries[col] = {}

            if col.is_many_to_many:
                self.association_columns[col] = (col.col, col.vcol)
                relation = col.link

                self.queries[col][self.addPair] = 'insert into "%s" (%s) values(%s)' % \
                    (relation,
                     ', '.join(['"%s"' % c for c in self.association_columns[col]]),
                     ', '.join(['%%(%s)s' % c for c in self.association_columns[col]])
                    )

            elif col.is_one_to_many:
                self.association_columns[col] = (col.vcol, '__key__')
                relation = col.vcls.relation
                self.queries[col][self.addPair] = \
                    'update "%s" set %s = %%(%s)s where __key__ = %%(__key__)s' \
                    % (relation, col.vcol, col.vcol)
            else:
                assert False # fixme: throw MappingError exception

            self.queries[col][self.getPair] = 'select %s from "%s"' % \
                (', '.join(['"%s"' % c for c in self.association_columns[col]]), relation)

            if __debug__:
                log.debug('association load query: "%s"' % \
                        self.queries[col][self.getPair])
            if __debug__:
                log.debug('association insert query: "%s"' % \
                        self.queries[col][self.addPair])


    def getObjects(self):
        """
        Load objects from database.
        """
        for data in self.motor.getData(self.queries[self.getObjects], ['__key__'] + self.columns):
#            for col in self.one_to_one_associations:
#                data[col.name] = data[col.afkey]

            obj = self.cls(data)      # create object instance
            obj.__key__ = data['__key__'] # and set object key

            yield obj


    def getData(self, obj):
        """
        Extract relational data from application object.

        @param obj: Application object.

        @return: Dictionary of object's relational data.
        """
        # get attribute values
        data = obj.__dict__.copy()

        # get one-to-one association foreign key values
        for col in self.one_to_one_associations:
            value = getattr(obj, col.attr)
            if value is None:
                data[col.col] = None
            else:
                data[col.col] = value.__key__
        return data


    def addPair(self, col, okey, vkey):
        """
        fixme
        """
        data = dict(zip(self.association_columns[col], (okey, vkey))) #fixme
        self.motor.add(self.queries[col][self.addPair], data)


    def getPair(self, col):
        """
        fixme
        """
        okey, vkey = self.association_columns[col] # fixme
        for data in self.motor.getData(self.queries[col][self.getPair], \
                self.association_columns[col]):
            yield data[okey], data[vkey]


    def add(self, obj):
        """
        Add object to database.

        @param obj: Object to add.
        """
        data = self.getData(obj)
        key = self.motor.getKey(self.cls.relation + '_seq') # fixme
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

    @ivar db_module: Python DB API module.
    @ivar db_conn: Python DB API connection object.
    """
    def __init__(self, db_module):
        """
        Initialize database access object.
        """
        self.db_module = db_module
        self.db_conn = None
        log.info('Motor object initialized')


    def connectDB(self, dsn):
        """
        Connect with database.
        
        @param dsn: Data source name.

        @see: L{bazaar.motor.Motor.closeDBConn}
        """
        self.db_conn = self.db_module.connect(dsn)
        if __debug__: log.debug('connected to database with dsn "%s"' % dsn)


    def closeDBConn(self):
        """
        Close database connection.

        @see: L{bazaar.motor.Motor.connectDB}
        """
        self.db_conn.close()
        self.db_conn = None
        if __debug__: log.debug('close database connection')


    def getData(self, query, cols):
        """
        Get list of rows from database.

        Method returns dictionary per databse relation row. The
        dictionary keys are relation column names and dictionary values
        are column values for the relation row.

        @param query: Database SQL query.
        @param cols: List of relation columns.
        """
        if __debug__: log.debug('query "%s": executing' % query)

        dbc = self.db_conn.cursor()
        dbc.execute(query)

        if __debug__: log.debug('query "%s": executed, rows = %d' % (query, dbc.rowcount))

        iter = range(len(cols))
        row = dbc.fetchone()
        while row:
            data = {}

            for i in iter: data[cols[i]] = row[i]
            yield data

            row = dbc.fetchone()

        if __debug__: log.debug('query "%s": got all data, len = %d' % (query, dbc.rowcount))


    def add(self, query, data):
        """
        Insert row into database relation.

        @param query: SQL query.
        @param data: Row data to insert.
        """
        if __debug__: log.debug('query "%s", data = %s: executing' % (query, data))
        dbc = self.db_conn.cursor()
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
        dbc = self.db_conn.cursor()
        dbc.execute(query, tuple(data) + (key, ))
        if __debug__: log.debug('query "%s", data = %s, key = %s: executed' % (query, data, key))


    def delete(self, query, key):
        """
        Delete row from database relation.

        @param query: SQL query.
        @param key: Key of the row to delete.
        """
        if __debug__: log.debug('query "%s", key = %s: executing' % (query, key))
        dbc = self.db_conn.cursor()
        dbc.execute(query, (key, ))
        if __debug__: log.debug('query "%s", key = %s: executed' % (query, key))


    def commit(self):
        """
        Commit pending database transactions.
        """
        self.db_conn.commit()


    def rollback(self):
        """
        Rollback database transactions.
        """
        self.db_conn.rollback()


    # fixme
    def getKey(self, seq):
        dbc = self.db_conn.cursor()
        dbc.execute('select nextval(%s)', (seq, ))
        return dbc.fetchone()[0]
