#!/usr/bin/python

from steemdata import SteemData
import datetime as dt
import shelve

s = SteemData()

transfers = []
start_date = dt.datetime(2017, 10, 19, 0, 0, 0, 0)
end_date = dt.datetime(2017, 11, 19, 0, 0, 0, 0)

while start_date < end_date:
    stop_date = start_date + dt.timedelta(days=1)

    time_constraints = {
        '$gte': start_date,
        '$lt': stop_date,
    }
    conditions = {
        'timestamp': time_constraints,
        'type': 'transfer',
    }
    projection = {
        '_id': 0,
        'amount' : 1,
        'memo': 1,
        'timestamp': 1,
        'from' : 1,
        'to': 1,
    }
    transferlist = list(s.Operations.find(conditions, projection))
    transfers.extend(transferlist)
    print(start_date, len(transferlist))
    start_date = stop_date

shelf = shelve.open("/steemdata/steem-transfers.shelf")
shelf['transfers'] = transfers
shelf.close()
