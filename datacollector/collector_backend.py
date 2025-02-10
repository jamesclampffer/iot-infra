"""
  Copyright 2024 Jim Clampffer

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at^M

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""

import json
import uuid
import urllib.parse
import sqlite3
import time

class DBWriter(object):
    """ Responsible for beating stream data into something tabular """

    __slots__ = 'dbconn'
    def __init__(self):
        # Set up a DB with emphemeral storage
        self.dbconn = sqlite3.connect(":memory:")

        # DML to make fact table. Since this is using memory it may assume the table
        # does not already exist.
        dml = "CREATE TABLE Live("
        dml += "  accept_time numeric(10,3), "
        dml += "  topic varchar, "
        dml += "  device_id varchar, "
        dml += "  device_type varchar, "
        dml += "  freemem int, "
        dml += "  data varchar);"

        self.dbconn.execute(dml)
        self.dbconn.commit()

    def __del__(self):
        if self.dbconn:
            self.dbconn.close()

    def acceptData(self, uri_args:dict):
        """ Take query params from the GET request and store them """
        # Time processed - not the same as when the emitter sent data, ok for now
        accept_time = int(time.time()*1000)/1000

        # Extract or generate fields for this request
        topic = 'placeholder_topic'
        val_or = lambda key, default : uri_args[key] if key in uri_args else default
        dev_typ = val_or('device_type', 'NULL')
        dev_mod = val_or('device_model', 'NULL')
        dev_freemem = int(val_or('heapfree', -1))
        databuf = "teststring"

        # Insert the row.
        qstr =  "INSERT INTO Live(accept_time, topic, device_id, device_type, freemem, data)"
        qstr += "   VALUES ({},'{}', '{}', '{}', {}, '{}');".format(accept_time,
                                                              topic,
                                                              dev_typ,
                                                              dev_mod,
                                                              dev_freemem,
                                                              databuf)
        self.dbconn.execute(qstr)
        self.dbconn.commit()

        # - Should the leading column have a NOT NULL constraint? count(*) vs count(1) consideration
        # - None of these aggregates should require materializing the table, so it
        #   should be fast. If it gets bogged down it's time to look at query plans. 
        cursor = self.dbconn.execute('SELECT count(*), min(accept_time), max(accept_time) FROM Live')
        row = cursor.fetchone()

        # Print some basic stats for debug.
        if row[0] % 100 == 0:
            print("\ncommitted qry: cnt {} | mintime {} | maxtime {}|\n".format(row[0], row[1], row[2]))
        cursor.close()

        if row[0] % 10 == 0:
            # Print last 10 entries (debug)
            cursor = self.dbconn.execute('SELECT * FROM Live ORDER BY 1 DESC LIMIT 10')
            for row in cursor:
                print(str(row))
            cursor.close()
