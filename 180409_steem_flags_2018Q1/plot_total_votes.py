#!/usr/bin/python
import shelve
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from helpers import get_pending_payout

s = shelve.open("posts.shelf")
posts = s['posts']
comments = s['comments']
s.close()

args = {'linestyle': '-', 'marker': '.'}
dates = posts.keys()
pos_post_rshares = [posts[date][0] for date in posts.keys()]
neg_post_rshares = [posts[date][1] for date in posts.keys()]
pos_post_votes = [posts[date][2] for date in posts.keys()]
neg_post_votes = [posts[date][3] for date in posts.keys()]
rel_neg_post_rshares = [(neg * 100 / (pos + neg)) for (pos, neg) in
                        zip(pos_post_rshares, neg_post_rshares)]
rel_neg_post_votes = [(neg * 100 / (pos + neg)) for (pos, neg) in zip
                      (pos_post_votes, neg_post_votes)]

pos_comment_rshares = [comments[date][0] for date in comments.keys()]
neg_comment_rshares = [comments[date][1] for date in comments.keys()]
pos_comment_votes = [comments[date][2] for date in comments.keys()]
neg_comment_votes = [comments[date][3] for date in comments.keys()]
rel_neg_comment_rshares = [(neg * 100 / (pos + neg)) for (pos, neg) in
                           zip(pos_comment_rshares,
                               neg_comment_rshares)]
rel_neg_comment_votes = [(neg * 100 / (pos + neg)) for (pos, neg) in
                         zip(pos_comment_votes, neg_comment_votes)]

###############################################################################
# relative number of negative rshares
###############################################################################
plt.figure(figsize=(12, 6))
label = "Relative value of downvotes on posts"
plt.plot_date(dates, rel_neg_post_rshares, **args, label=label)
label = "Relative number of downvotes on posts"
plt.plot_date(dates, rel_neg_post_votes, **args, label=label)
label = "Relative value of downvotes on comments"
plt.plot_date(dates, rel_neg_comment_rshares, **args, label=label)
label = "Relative number of downvotes on comments"
plt.plot_date(dates, rel_neg_comment_votes, **args, label=label)
plt.grid()
plt.legend()
plt.xlabel("Date")
plt.ylabel("Percent")
plt.title("Relative number and value of downvotes per day wrt. all votes")
plt.ylim([0, max(rel_neg_post_rshares + rel_neg_post_votes +
                 rel_neg_comment_rshares + rel_neg_comment_votes) *
          1.2])
plt.savefig("rel_neg_rshares.png")

###############################################################################
# absolute number of negative rshares
###############################################################################
fig, ax1 = plt.subplots(figsize=(12, 6))
label = "Downvotes on posts"
ax1.plot_date(dates, neg_post_rshares, **args, label=label)
label = "Downvotes on comments"
ax1.plot_date(dates, neg_comment_rshares, **args, label=label)
ax1.legend()
plt.grid()
plt.ylim([0, max(neg_post_rshares + neg_comment_rshares) * 1.2])
ax1.set_xlabel("Date")
ax1.set_ylabel("rshares")
ax2 = ax1.twinx()
ax2.set_ylim([0, get_pending_payout(max(neg_post_rshares +
                                        neg_comment_rshares) * 1.2)])
ax2.set_ylabel("SBD")
plt.title("Absolute rshare value of downvotes per day")
plt.savefig("abs_neg_rshares.png")
