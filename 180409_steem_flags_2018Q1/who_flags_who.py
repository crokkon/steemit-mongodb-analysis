#!/usr/bin/python

"""
* how many flag rshares wrt. to positive rshares?
* Who flags who? number of voters, flaggers and flag receivers, common set
* are flags countered?
* reputation of flaggers
"""

from steemdata import SteemData
from datetime import datetime, timedelta
import shelve

start_date = datetime(2018, 1, 1)
end_date = datetime(2018, 3, 26)

s = SteemData()
projection = {'_id': 0, 'author': 1, 'active_votes': 1, 'created': 1,
              'author_reputation': 1}
posts = []
comments = []

query_start = start_date
while query_start < end_date:
    query_stop = query_start + timedelta(days=1)
    created = {"$gte": query_start, "$lt": query_stop}
    conditions = {'created': created, 'active_votes.rshares': {"$lt":
                                                               0}}
    postcount = 0
    for post in s.Posts.find(conditions, projection=projection):
        posts.append(post)
        postcount += 1

    commentcount = 0
    for post in s.Comments.find(conditions, projection=projection):
        comments.append(post)
        commentcount += 1

    print("%s: %d posts, %d comments" % (query_start, postcount,
                                         commentcount))
    query_start = query_stop

s = shelve.open("who_flags_who.shelf")
s['posts'] = posts
s['comments'] = comments
s.close()
