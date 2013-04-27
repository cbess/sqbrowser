#!/usr/bin/env python
# encoding: utf-8
"""
sqlbase.py

Created by Christopher Bess on 2009-03-22.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import sys
import os

try:
    import sqlite3
except ImportError:
    from pysqlite2 import dbapi2 as sqlite3


class SqlBase:
    def __init__(self, dbpath):
        """__init__
        """
        self.db = None
        self.cursor = None
        self.db_path = dbpath
        self.is_connected = False
        self.last_error = ''

    def connect(self):
        """connect
        """
        if self.is_connected:
            return True

        # check for existance
        if not os.path.isfile(self.db_path):
            return False

        ## connect to the db

        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()
        self.is_connected = True
        return self.is_connected

    def execute_query(self, query):
        """Executes the specified query
        @return Tuple of results, upon success or
        None, if error (check self.last_error)
        """
        self.connect()

        ## get the results

        try:
            results = self.cursor.execute(query)
        except Exception, e:
            self.last_error = str(e)
            return None

        # set default query result, used it non-select query executed
        queryResult = {
            'columns': ['?'],
            'rows': (['No rows returned'],),
            'message': ''
        }

        # get the rows
        values = results.fetchall()
        if values:
            # get the     columns names
            cols = [r[0] for r in results.description]

            queryResult = {
                'columns': cols,
                'rows': values,
                'message': '--> Rows returned: %d' % len(values)
            }
        return queryResult

    def disconnect(self):
        """disconnect
        """
        if not self.is_connected:
            return
        # close the connection
        self.cursor.close()
        self.db.close()
        self.is_connected = False

    def commit(self):
        """Commits the query results
        """
        self.db.commit()

if __name__ == '__main__':
    main()

