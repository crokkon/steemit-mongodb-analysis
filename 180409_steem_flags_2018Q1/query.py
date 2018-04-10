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
projection = {'_id': 0, 'active_votes.rshares': 1}
posts = {}
comments = {}

query_start = start_date
while query_start < end_date:
    query_stop = query_start + timedelta(days=1)
    created = {"$gte": query_start, "$lt": query_stop}
    conditions = {'created': created}

    pos_post_rshares = 0
    neg_post_rshares = 0
    pos_post_votes = 0
    neg_post_votes = 0

    postcount = 0
    for post in s.Posts.find(conditions, projection=projection):
        postcount += 1
        for v in post['active_votes']:
            rshares = int(v['rshares'])
            if rshares > 0:
                pos_post_votes += 1
                pos_post_rshares += rshares
            if rshares < 0:
                neg_post_votes += 1
                neg_post_rshares += abs(rshares)

    posts[query_start] = [pos_post_rshares, neg_post_rshares,
                          pos_post_votes, neg_post_votes]

    pos_comment_rshares = 0
    neg_comment_rshares = 0
    pos_comment_votes = 0
    neg_comment_votes = 0

    commentcount = 0
    for comment in s.Comments.find(conditions, projection=projection):
        commentcount += 1
        for v in comment['active_votes']:
            rshares = int(v['rshares'])
            if rshares > 0:
                pos_comment_votes += 1
                pos_comment_rshares += rshares
            if rshares < 0:
                neg_comment_votes += 1
                neg_comment_rshares += abs(rshares)

    comments[query_start] = [pos_comment_rshares, neg_comment_rshares,
                             pos_comment_votes, neg_comment_votes]

    print("%s: %d posts, %d comments" % (query_start, postcount,
                                         commentcount))
    query_start = query_stop

s = shelve.open("posts.shelf")
s['posts'] = posts
s['comments'] = comments
s.close()
