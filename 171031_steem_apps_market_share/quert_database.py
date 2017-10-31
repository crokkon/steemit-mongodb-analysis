#!/usr/bin/python

from steemdata import SteemData
import datetime as dt
import shelve

s = SteemData()

posts = {}
comments = {}
start_date = dt.datetime(2017, 8, 1, 0, 0, 0, 0)
end_date = dt.datetime(2017, 10, 31, 0, 0, 0, 0)

while start_date.date() < dt.datetime.now().date():
    stop_date = start_date + dt.timedelta(days=1)

    time_constraints = {
        '$gte': start_date,
        '$lt': stop_date,
    }
    conditions = {
        'created': time_constraints,
    }
    projection = {
        '_id': 0,
        'json_metadata.app': 1,
        'created': 1,
        'category': 1,
        'author': 1,
    }
    postlist = list(s.Posts.find(conditions, projection))
    posts[start_date.date()] = postlist
    #commentlist = list(s.Comments.find(conditions, projection))
    #comments[start_date.date()] = commentlist
    print(start_date.date(), len(postlist))#, len(commentlist))
    start_date = stop_date
    
shelf = shelve.open("/steemdata/steem-apps.shelf")
shelf['posts'] = posts
#shelf['comments'] = comments
shelf.close()
