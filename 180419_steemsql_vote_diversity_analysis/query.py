#!/usr/bin/python

import pyodbc
import shelve
import sys
import config

if len(sys.argv) != 3:
    print("ERROR: Invalid command line parameter count")
    print("Usage: %s [year] [month]" % (sys.argv[0]))
    exit()

year = int(sys.argv[1])
month = int(sys.argv[2])

connection = pyodbc.connect(driver=config.driver,
                              server=config.server,
                              database=config.database,
                              uid=config.uid, pwd=config.pwd)
cursor = connection.cursor()

for day in range(2, 9):
    query = "SELECT author, active_votes, created, depth " \
            "FROM Comments (NOLOCK) WHERE " \
            "YEAR(Comments.created) = %s AND " \
            "MONTH(Comments.created) = %s AND " \
            "DAY(Comments.created) = %s" % (year, month, day)
    cursor.execute(query)

    ops = []
    for op in cursor:
        entry = {'author': op[0], 'active_votes': op[1], 'created':
                 op[2], 'depth': op[3]}

        ops.append(entry)

    s = shelve.open("posts-%d%02d%02d.shelf" % (year, month, day))
    s['posts'] = ops
    s.close()
    print(day, len(ops))

connection.close()
