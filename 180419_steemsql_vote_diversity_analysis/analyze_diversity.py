import shelve
from hist import hist
import json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from helpers import get_var_log_bins

SKIP_DOWNVOTES = False

bots = []
with open("bots.txt") as f:
    for line in f.readlines():
        if line.startswith("#"):
            continue
        bots.append(line[:-1])


voters = {}
distinct_voters = set()
num_votes_per_voter = hist()

total_rshares = 0
for day in range(2, 9):
    filename = "posts-201804%02d.shelf" % (day)
    print("Processing %s..." % (filename))
    s = shelve.open(filename)
    posts = s['posts']
    s.close()

    for post in posts:
        try:
            votes = json.loads(post['active_votes'])
        except:
            print("Failed to parse", post['active_votes'])
            exit()

        ts = post['created'].date()
        author = post['author']
        for v in votes:
            rshares = int(v['rshares'])
            if rshares < 0 and SKIP_DOWNVOTES:
                continue
            rshares = abs(rshares)

            voter = v['voter']
            distinct_voters |= set([voter])
            num_votes_per_voter.fill(voter)

            if voter not in voters:
                voters[voter] = {}
            if author not in voters[voter]:
                voters[voter][author] = 0
            voters[voter][author] += rshares

            total_rshares += rshares


diversity = {}
diversity_count_limit = 6
diversity_percent_limit = 80

total_low_div_accounts = hist()
total_low_div_rshares = 0
vote_diversity = []

total_selfvote_rshares = 0

diversity_hist = hist()
selfvoters = 0

low_div_accounts = set()

for voter in voters:
    total_voter_rshares = sum(voters[voter][a] for a in voters[voter])
    num_votees = len(voters[voter])
    vote_diversity.append(num_votees)
    diversity_hist.fill(voter, num_votees)
    votees = voters[voter].keys()
    if num_votees == 1 and voter in votees:
        selfvoters += 1

    if voter in voters[voter]:
        total_selfvote_rshares += voters[voter][voter]

    low_div_rshares = 0
    for author in sorted(voters[voter], key=lambda k:
                         voters[voter][k], reverse=True)[:diversity_count_limit]:
        low_div_rshares += voters[voter][author]

    if total_voter_rshares > 0:
        div_rate = low_div_rshares * 100 / total_voter_rshares
    else:
        div_rate = 0

    if div_rate >= diversity_percent_limit:
        #print("%16s: %.1f%%" % (voter, div_rate))
        total_low_div_accounts.fill(voter, low_div_rshares)
        total_low_div_rshares += low_div_rshares
        low_div_accounts |= set([voter])

print("low_div_accounts:", len(low_div_accounts))
lds = shelve.open("low_div_accounts.shelf")
lds['accounts'] = low_div_accounts
lds.close()

bins = get_var_log_bins(100, 1, max(vote_diversity))
mean_diversity = np.mean(vote_diversity)
median_diversity = np.median(vote_diversity)

ticks = [1, 10, 100, 1000, 10000]
plt.figure(figsize=(12, 6))
vals, bins, patches = plt.hist(vote_diversity, bins=bins,
                               label="Voting diversity")
plt.bar([1], selfvoters, label="Accounts that only self-vote",
        color="red", width=0.1, align='edge')
label="Mean voting diversity: %d authors" % (mean_diversity)
plt.axvline(mean_diversity, label=label, linestyle="dashed",
            linewidth=2, color="orange")
label="Median voting diversity: %d authors" % (median_diversity)
plt.axvline(median_diversity, label=label, linestyle="dashed",
            linewidth=2, color="green")
plt.grid()
plt.legend()
plt.gca().set_xscale("log")
plt.title("Vote diversity: Number of distinct authors voted per voter\n" \
          "Time range: April 2nd - April 8th 2018")
plt.xlabel("Number of distict authors voted on")
plt.ylabel("Number of accounts")
plt.gca().xaxis.set_ticks(ticks)
plt.gca().xaxis.set_ticklabels(ticks)
plt.savefig("vote_diversity.png")

print("Number of distinct voters: %d" % (len(distinct_voters)))
print("Number of 100%% selfvoters: %d" % (selfvoters))

print("Highest vote diversity by number of votes to distinct authors:")
print(diversity_hist.xrange()[:20])
print(diversity_hist.yrange()[:20])

print("Total vote rshares: %.1f tn" % (total_rshares/1e12))
print("diversity_count_limit: %d, diversity_percent_limit: %d %%" %
      (diversity_count_limit, diversity_percent_limit))
print("Low diversity rshares: %.1f tn" % (total_low_div_rshares /
                                          1e12))
print("Low div rate: %.2f %%" % (total_low_div_rshares * 100 /
                                 total_rshares))
print("Selfvote rshares: %.1f tn" % (total_selfvote_rshares / 1e12))
print("Selfvote rate (all): %.2f %%" % (total_selfvote_rshares * 100 /
                                        total_rshares))

print("vote diversity hist vals:", vals)

###############################################################################
# number of votes per voter
###############################################################################
bins = [2**x for x in range(0, 15)]
plt.figure(figsize=(12, 6))
plt.hist(num_votes_per_voter.yrange(), bins=bins)
plt.grid()
plt.title("Number of votes per voter")
plt.xlabel("Number of votes")
plt.ylabel("Number of accounts")
plt.gca().set_xscale("log")
plt.savefig("number_of_votes.png")

###############################################################################
# total, selfvote and low-div rshares
###############################################################################
all_vote_rshares = hist()
all_vote_rshares_excl_bots = hist()
total_rshares_excl_bots = 0
self_vote_rshares = hist()
low_div_rshares = hist()
low_div_account_rshares = hist()

for day in range(2, 9):
    filename = "posts-201804%02d.shelf" % (day)
    print("Processing %s..." % (filename))
    s = shelve.open(filename)
    posts = s['posts']
    s.close()

    for post in posts:
        try:
            votes = json.loads(post['active_votes'])
        except:
            print("Failed to parse", post['active_votes'])
            exit()

        ts = post['created'].date()
        author = post['author']
        for v in votes:
            rshares = int(v['rshares'])
            voter = v['voter']
            if rshares < 0 and SKIP_DOWNVOTES:
                continue
            rshares = abs(rshares)

            all_vote_rshares.fill(ts, rshares)
            if voter not in bots:
                all_vote_rshares_excl_bots.fill(ts, rshares)
                total_rshares_excl_bots += rshares
            if voter == post['author']:
                self_vote_rshares.fill(ts, rshares)
            if voter in low_div_accounts:
                low_div_rshares.fill(ts, rshares)
                low_div_account_rshares.fill(voter, rshares)

args = {'linestyle': '-', 'marker':'.'}

plt.figure(figsize=(12, 6))
label = "All vote rshares"
plt.plot_date(all_vote_rshares.xrange('key'),
              all_vote_rshares.yrange('key'), label=label, **args)
label = "All vote rshares excluding bid-bots, dapps & cleaners"
plt.plot_date(all_vote_rshares_excl_bots.xrange('key'),
              all_vote_rshares_excl_bots.yrange('key'), label=label,
              **args)
label = "Low diversity vote rshares"
plt.plot_date(low_div_rshares.xrange('key'),
              low_div_rshares.yrange('key'), label=label, **args)
label = "Self vote rshares"
plt.plot_date(self_vote_rshares.xrange('key'),
              self_vote_rshares.yrange('key'), label=label, **args)

plt.grid()
plt.legend()
plt.title("Number of total upvote rshares, self-vote rshares and " \
          "low-diversity vote rshares")
plt.xlabel("Date")
plt.ylabel("Rshares")
plt.savefig("rshares.png")

print("low_div_account_rshares:")
print(low_div_account_rshares.xrange()[:100])

print("Total rshares excl. bots:", total_rshares_excl_bots)
print("Selfvote rate wrt excl. bots: %.2f%%" % (total_selfvote_rshares
                                                * 100 / total_rshares_excl_bots))
print("low-div rate wrt excl. bots: %.2f%%" % (total_low_div_rshares *
                                               100 / total_rshares_excl_bots))
#print(low_div_account_rshares.yrange()[:20])
