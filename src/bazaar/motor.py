# $Id: motor.py,v 1.7 2003/08/07 17:42:53 wrobell Exp $

import logging

log = logging.getLogger('bazaar.motor')

"""
<s>Database access objects.</s>
<p>
</p>
"""

class Convertor:
    """
    <s>Database data convertor.</s>

    <attr name = 'queries'>Queries to modify data in database.</attr>
    <attr name = 'cls'>Application class, which objects are converted.</attr>
    <attr name = 'motor'>Database access object.</attr>
    <attr name = 'columns'>List of columns used with database queries.</attr>
    """
    def __init__(self, cls, mtr):
        """
        """
        self.queries = {}
        self.cls = cls
        self.motor = mtr

        self.columns = [col.name for col in self.cls.columns.values()]

        #
        # set convert key method for single or multicolumn relation key;
        # convert key methods creates tupple from object key data
        #

        # multicolumn key
        def getMKey(key):
            return key

        # single column key
        def getKey(key):
            return (key, )

        if len(self.cls.key_columns) == 1:
            self.convertKey = getKey
        else:
            self.convertKey = getMKey

        #
        # prepare queries
        #
        self.queries[self.getObjects] = 'select %s from "%s"' \
            % (', '.join(['"%s"' % col for col in self.columns]), self.cls.relation)

        if __debug__: log.debug('get object query: "%s"' % self.queries[self.getObjects])

        self.queries[self.add] = 'insert into "%s" (%s) values (%s)' \
            % (self.cls.relation,
               ', '.join(['"%s"' % col for col in self.columns]),
               ', '.join(['%%(%s)s' % col for col in self.columns])
              )

        if __debug__: log.debug('add object query: "%s"' % self.queries[self.add])

        self.queries[self.update] = 'update "%s" set %s where %s' \
            % (self.cls.relation,
               ', '.join(['"%s" = %%s' % col for col in self.columns]),
               ' and '.join(['"%s" = %%s' % col for col in self.cls.key_columns])
              )
        if __debug__: log.debug('update object query: "%s"' % self.queries[self.update])

        self.queries[self.delete] = 'delete from "%s" where %s' \
            % (self.cls.relation,
               ' and '.join(['"%s" = %%s' % col for col in self.cls.key_columns])
              )
        if __debug__: log.debug('delete object query: "%s"' % self.queries[self.delete])


    def getObjects(self):
        """
        <s>Load objects from database.</s>
        """
        for data in self.motor.getData(self.queries[self.getObjects], self.columns):
            obj = self.cls(data)   # create object instance
            yield obj


    def add(self, obj):
        """
        <s>Add object to database.</s>

        <attr name = 'obj'>Object to add.</attr>
        """
        self.motor.add(self.queries[self.add], obj.__dict__)
 

    def update(self, obj):
        """
        <s>Update object in database.</s>

        <attr name = 'obj'>Object to update.</attr>
        """
        self.motor.update(self.queries[self.update], \
            [obj.__dict__[col] for col in self.columns], self.convertKey(obj.key))


    def delete(self, obj):
        """
        <s>Delete object from database.</s>

        <attr name = 'obj'>Object to delete.</attr>
        """
        self.motor.delete(self.queries[self.delete], self.convertKey(obj.key))



class Motor:
    """
    <s>Database access object.</s>

    <attr name = 'db_module'></attr>
    <attr name = 'db_conn'></attr>
    <attr name = 'dbc'></attr>
    """
    def __init__(self, db_module):
        """
        <s>Initialize database access object.</s>
        """
        self.db_module = db_module
        self.db_conn = None
        self.dbc = None
        log.info('Motor object initialized')


    def connectDB(self, dsn):
        """
        <s>Connect with database.</s>
        
        <attr name = 'dsn'>Data source name.</attr>

        <see>
            <r method = 'closeDBConn'>
        </see>
        """
        self.db_conn = self.db_module.connect(dsn)
        self.dbc = self.db_conn.cursor()
        if __debug__: log.debug('connected to database with dsn "%s"' % dsn)


    def closeDBConn(self):
        """
        <s>Close database connection.</s>

        <see>
            <r method = 'connectDB'>
        </see>
        """
        self.db_conn.close()
        self.db_conn = None
        self.dbc = None
        if __debug__: log.debug('close database connection')


    def getData(self, query, cols):
        """
        <s>Get list of rows from database.</s>
        <p>
            Method returns dictionary per databse relation row. The
            dictionary keys are relation column names and dictionary values
            are column values for the relation row.
        </p>

        <attr name = 'query'>Database SQL query.</s>
        <attr name = 'cols'>List of relation columns.</s>
        """
        if __debug__: log.debug('query "%s": executing' % query)

        self.dbc.execute(query)

        if __debug__: log.debug('query "%s": executed, rows = %d' % (query, self.dbc.rowcount))

        iter = range(len(cols))
        row = self.dbc.fetchone()
        while row:
            data = {}

            for i in iter: data[cols[i]] = row[i]
            yield data

            row = self.dbc.fetchone()

        if __debug__: log.debug('query "%s": got all data, len = %d' % (query, self.dbc.rowcount))


    def add(self, query, data):
        """
        <s>Insert row into database relation.</s>

        <attr name = 'query'>SQL query.</attr>
        <attr name = 'data'>Row data to insert.</attr>
        """
        if __debug__: log.debug('query "%s", data = %s: executing' % (query, data))
        self.dbc.execute(query, data)
        if __debug__: log.debug('query "%s", data = %s: executed' % (query, data))


    def update(self, query, data, key):
        """
        <s>Update row in database relation.</s>

        <attr name = 'query'>SQL query.</attr>
        <attr name = 'data'>Tuple of new values for the row.</attr>
        <attr name = 'key'>Key of the row to update.</attr>
        """
        if __debug__: log.debug('query "%s", data = %s, key = %s: executing' % (query, data, key))
        self.dbc.execute(query, tuple(data) + tuple(key))
        if __debug__: log.debug('query "%s", data = %s, key = %s: executed' % (query, data, key))


    def delete(self, query, key):
        """
        <s>Delete row from database relation.</s>

        <attr name = 'query'>SQL query.</attr>
        <attr name = 'key'>Key of the row to delete.</attr>
        """
        if __debug__: log.debug('query "%s", key = %s: executing' % (query, key))
        self.dbc.execute(query, key)
        if __debug__: log.debug('query "%s", key = %s: executed' % (query, key))


    def commit(self):
        """
        <s>Commit pending database transactions.</s>
        """
        self.db_conn.commit()


    def rollback(self):
        """
        <s>Rollback database transactions.</s>
        """
        self.db_conn.rollback()
