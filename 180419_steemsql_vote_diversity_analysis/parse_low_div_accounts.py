#!/usr/bin/python
import shelve
from hist import hist
import json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math
import numpy as np
from hist import hist
from helpers import reputation, parse_time, get_var_log_bins
from steem.amount import Amount
from datetime import datetime

s = shelve.open("account_infos.shelf")
accounts = s['accounts']
s.close()

reputations = []
posts = []
created = []
sp = []
last_root_post = []

steem_per_mvest = 488
sp_limit = 1000

def get_eff_sp(account):
    own = Amount(account['vesting_shares']).amount
    inc = Amount(account['received_vesting_shares']).amount
    dlg = Amount(account['delegated_vesting_shares']).amount
    return (own + inc - dlg)  * steem_per_mvest / 1e6

for a in accounts:
    acc_sp = get_eff_sp(a)
    if acc_sp < sp_limit:
        continue
    reputations.append(reputation(int(a['reputation'])))
    posts.append(int(a['post_count']))
    cdate = parse_time(a['created'])
    created.append(mdates.date2num(cdate))
    sp.append(acc_sp)
    rp = parse_time(a['last_root_post'])
    if rp > datetime(2010, 1, 1):
        last_root_post.append(mdates.date2num(rp))

fig = plt.figure(figsize=(12, 12))
fig.suptitle("Low voting diversity accounts with at least %d SP (%d accounts)" %
             (sp_limit, len(reputations)), fontsize="x-large")
xlabel = "Reputation"
ylabel = "Occurences"
title = "Reputation"
p1 = fig.add_subplot(221, xlabel=xlabel, ylabel=ylabel, title=title)
p1.hist(reputations, bins=100)
p1.grid()

bins = [0] + [2**x for x in range(0, 15)]
xlabel = "Number of posts and comments"
ylabel = "Occurences"
title = "Lifetime post + comment count"
p2 = fig.add_subplot(222, xlabel=xlabel, ylabel=ylabel, title=title)
p2.hist(posts, bins=bins)
p2.grid()
p2.set_xscale("log")

dateFmt = mdates.DateFormatter('%m/%y')
xlabel = "Account creation date"
ylabel = "Occurences"
title = "Account creation dates"
p3 = fig.add_subplot(223, xlabel=xlabel, ylabel=ylabel, title=title)
p3.hist(created, bins=100)
p3.grid()
p3.xaxis.set_major_formatter(dateFmt)
#p3.xaxis.autofmt_xdate(rotation=30)

title = "Effective Account SP"
xlabel = "SteemPower"
ylabel = "Occurences"
p4 = fig.add_subplot(224, xlabel=xlabel, ylabel=ylabel, title=title)
p4.hist(sp, bins=get_var_log_bins(100, 0.1, 1000000))
p4.grid()
p4.set_xscale("log")
p4.set_yscale("log")
plt.savefig("low_div_acccounts_%d.png" % (sp_limit))


plt.figure(figsize=(12, 6))
xbins = [x for x in range(0, 100)]  # 100  # [0] + [2**x for x in range(0, 15)]
ybins = 100
plt.hist2d(posts, reputations, bins=(xbins, ybins), cmin=1)
#plt.gca().set_xscale("log")
plt.colorbar()
plt.title("Low-Diversity Voters: Number of posts vs. Reputation")
plt.xlabel("Number of posts and comments")
plt.ylabel("Reputation")
plt.savefig("low_div_posts_vs_rep.png")


plt.figure(figsize=(12, 6))
xbins = np.logspace(-1, 5, 100)  #get_var_log_bins(100, 0.1, 1000000)
ybins = 100
plt.gca().set_xscale("log")
plt.hist2d(sp, reputations, bins=(xbins, ybins), cmin=1)
plt.colorbar()
plt.title("Low-Diversity Voters: SP vs. Reputation")
plt.xlabel("Effective account SteemPower")
plt.ylabel("Reputation")
plt.savefig("low_div_sp_vs_rep.png")

plt.figure(figsize=(12, 6))
plt.hist(last_root_post, bins=100)
plt.gca().xaxis.set_major_formatter(dateFmt)
plt.grid()
plt.savefig("low_div_acc_last_root_post.png")
