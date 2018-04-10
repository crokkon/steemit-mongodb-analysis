#!/usr/bin/python
import shelve
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

from hist import hist
from helpers import get_pending_payout, reputation

flaggers = set()
flagged = set()
flaggerstats = hist()
flaggedstats = hist()

exclude = ['mack-bot', 'quarry', 'cheetah', 'steemcleaners',
           'spaminator', 'prowler', 'blacklist-a', 'adm']

bernie = ['berniesanders', 'charlesmanson', 'chatterbox', 'danknugs',
          'elchapo', 'engagement', 'ghettodweller', 'gonewhaling', 'gotvotes',
          'iflagtrash', 'illbeyourfriend', 'ilovetocomment', 'indica',
          'jacktheripper', 'jeffreydahmer', 'kimjongun', 'liquidity',
          'muhammad', 'nextgen1', 'nextgen10', 'nextgen11', 'nextgen12',
          'nextgen13', 'nextgen16', 'nextgen2', 'nextgen3', 'nextgen6',
          'nextgen7', 'nextgencrypto', 'nextgencrypto100', 'nextgencrypto101',
          'nextgencrypto110', 'nextgencrypto111', 'nextgencrypto120',
          'nextgencrypto121', 'ngc', 'ngcrep', 'nogalert', 'nxtgencrpto10',
          'randomthoughts', 'randovote', 'randowhale0', 'randowhale1',
          'randowhale2', 'randowhale3', 'randowhale4', 'randowhale5',
          'randowhalebonus', 'randowhalefund', 'randowhaletrail',
          'randowhaling', 'rewardkiller', 'sativa', 'sockpuppet',
          'speakyourmind', 'steemittroll', 'steemservices', 'steemservices1',
          'steemservices3', 'steemservices5', 'the.bot', 'thebotkiller',
          'theconnoisseur', 'thecurator', 'thecyclist', 'thedelegator',
          'thedumpster', 'theghost', 'thesloth', 'theterrorist', 'theyeti',
          'whalemart', 'whaleofatime', 'whaleteam6', 'whalevotes',
          'whalewatching', 'wheresrando', 'whereswhaledo', 'yomamasofat',
          'yougotflagged']

bernie.extend(['abusereports', 'randowhale'])

grumpy = ['grumpycat', 'madpuppy']

haejin = ['haejin', 'ranchorelaxo', 'starjuno']

all_reps = [0, 0]
others_reps = [0, 0]

from_bernie = hist()
from_sc = hist()
to_haejin = hist()
from_haejin = hist()
all_others = hist()
all_downvotes = hist()

others_flags = 0
self_flags = 0
self_flag_authors = set()

others_flaggers = set()
others_flagged = set()

flagcount = 0


s = shelve.open("who_flags_who.shelf")
posts = s['posts']
comments = s['comments']
s.close()

# combine posts and comments
posts.extend(comments)

for post in posts:
    created = post['created'].date()
    author = post['author']
    author_rep = reputation(post['author_reputation'])

    for v in post['active_votes']:
        if int(v['rshares']) < 0:
            voter = v['voter']
            rshares = abs(int(v['rshares']))
            voter_rep = reputation(v['reputation'])

            # skip self-flags
            if voter == author:
                self_flags += 1
                self_flag_authors |= set([author])
                continue

            if voter in bernie or voter in grumpy:
                from_bernie.fill(created, rshares)
            if voter in exclude:
                from_sc.fill(created, rshares)
            if author == "haejin":
                to_haejin.fill(created, rshares)
            if voter in haejin:
                from_haejin.fill(created, rshares)
            else:
                from_haejin.fill(created, 0)

            if voter_rep < author_rep:
                all_reps[0] += 1
            else:
                all_reps[1] += 1

            all_downvotes.fill(created, rshares)

            # all other flags
            if voter not in bernie and voter not in exclude and \
               voter not in grumpy and author != 'haejin' and \
               voter not in haejin:
                all_others.fill(created, rshares)
                if voter_rep < author_rep:
                    others_reps[0] += 1
                else:
                    others_reps[1] += 1
                others_flags += 1

                others_flaggers |= set([voter])
                others_flagged |= set([author])
                key = (voter, author)

            flagcount += 1
            flaggers |= set([voter])
            flagged |= set([author])
            flaggerstats.fill(voter)
            flaggedstats.fill(author)


print("unique flaggers:", len(flaggers))
print("unique flagged :", len(flagged))
print("common set     :", len(flaggers & flagged))
print("number of flags:", flagcount)
print("self_flags     :", self_flags)
print("self flaggers  :", len(self_flag_authors))
print("others flags   :", others_flags)
print("others flagged :", len(others_flagged))
print("others flaggers:", len(others_flaggers))
print("common set     :", len(others_flaggers & others_flagged))

print("*** Most frequent flaggers ***")
print(flaggerstats.xrange()[:50])
print(flaggerstats.yrange()[:50])

print("*** Most frequently flagged ***")
print(flaggedstats.xrange()[:50])
print(flaggedstats.yrange()[:50])

###############################################################################
# Reputation Pie
###############################################################################
fig = plt.figure(figsize=(12, 6))
labels = ["Lower rep voter flags\nhigher rep author", \
          "Higher rep voter flags\nlower rep author"]
p1 = fig.add_subplot(121, title="All downvotes")
p1.pie(all_reps, autopct="%.1f%%", labels=labels)
title = "Downvotes excl. those from\n" \
        "Steemit, SteemCleaners, berniesander, grumpycat,\n" \
        "from and to haejin"
p2 = fig.add_subplot(122, title=title)
p2.pie(others_reps, autopct="%.1f%%", labels=labels)
plt.tight_layout()
plt.savefig("reps_pie.png")

###############################################################################
# Breakdown of downvote rshares per day
###############################################################################
args = {'linestyle': '-', 'marker': "."}
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot_date(all_downvotes.xrange('key'), all_downvotes.yrange('key'),
              **args, label="all flags")
ax1.plot_date(from_sc.xrange('key'), from_sc.yrange('key'),
              **args, label="from steemit/steemcleaners et.al.")
ax1.plot_date(to_haejin.xrange('key'), to_haejin.yrange('key'),
              **args, label="to haejin")
ax1.plot_date(from_bernie.xrange('key'), from_bernie.yrange('key'),
              **args, label="from berniesaners/grumpycat et.al.")
ax1.plot_date(from_haejin.xrange('key'), from_haejin.yrange('key'),
              **args, label="from haejin et.al.")
ax1.plot_date(all_others.xrange('key'), all_others.yrange('key'),
              **args, label="all others", color="black")
maxy = max(all_downvotes.yrange('key')) * 1.2
ax1.set_ylim([0, maxy])
ax1.set_ylabel("Rshares")
ax1.set_xlabel("Date")
ax1.legend()
ax1.grid()
ax2 = plt.gca().twinx()
ax2.set_ylim([0, get_pending_payout(maxy)])
ax2.set_ylabel("SBD")
plt.title("Breakdown of downvote rshares per day")
plt.savefig("rshares_from_groups.png")
