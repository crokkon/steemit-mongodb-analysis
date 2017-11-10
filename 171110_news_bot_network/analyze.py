#!/usr/bin/python

from steemdata import SteemData
import datetime as dt
from steem.converter import Converter
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


s = SteemData()

posts = []
start_date = dt.datetime(2017, 10, 25, 0, 0, 0, 0)
end_date = dt.datetime(2017, 11, 9, 0, 0, 0, 0)

while start_date < end_date:
    stop_date = start_date + dt.timedelta(days=1)

    time_constraints = {
        '$gte': start_date,
        '$lt': stop_date,
    }
    conditions = {
        'created': time_constraints,
        # TODO: --> add magic here <--
    }
    projection = {
        '_id': 0,
        'created': 1,
        'category': 1,
        'permlink' : 1,
        'title': 1,
        'author': 1,
    }
    postlist = list(s.Posts.find(conditions, )) #projection))
    posts.extend(postlist)
    start_date = stop_date

authorlist = set([p['author'] for p in posts])


accounts = {}
for author in authorlist:
    accounts[author] = s.Accounts.find_one({'name':author})



class hist:
    def __init__(self):
        self.hist = {}
        
    def fill(self, key, incr = 1):
        if not key in self.hist:
            self.hist[key] = 0
        self.hist[key] += incr

    def xrange(self, sort='value'):
        if sort!='value':
            return [x for x in sorted(self.hist, reverse=True)]
        else:
            return [x for x in sorted(self.hist, key=lambda k: self.hist[k], reverse=True)]

    def yrange(self, sort='value'):
        if sort!='value':
            return [self.hist[x] for x in sorted(self.hist, reverse=True)]
        else:
            return [self.hist[x] for x in sorted(self.hist, key=lambda k: self.hist[k], reverse=True)]

    def entries(self, key=None):
        if key:
            return self.hist[key]
        else:
            return sum([self.hist[key] for key in self.hist])

class Aliases:
    def __init__(self):
        self.aliases = {}
        self.id = 0

    def add(self, name):
        if not name in self.aliases:
            self.aliases[name] = {'alias':"user%d" % (self.id)}
            self.id += 1

    def get_alias(self, name):
        if name in self.aliases:
            return self.aliases[name]['alias']
        else:
            return None

    def get_alias_sp(self, name):
        return self.get_account_sp(self.get_account(name))
        
    def get_account_sp(self, name):
        if name in self.aliases and 'sp' in self.aliases[name]:
            return self.aliases[name]['sp']
        account = s.Accounts.find_one({'name': name})#, projection={'_id':0, 'vesting_shares':1})
        if not account:
            return -1
        vests = account['vesting_shares']['amount'] + \
                account['received_vesting_shares']['amount'] - \
                account['delegated_vesting_shares']['amount']
        
        sp = Converter().vests_to_sp(vests)
        sp_str = str(int(sp))
        sp_obf = sp_str[0] + "x"*(len(sp_str)-1)
        self.aliases[name]['sp'] = sp_obf
        return sp_obf

    def get_account(self, name):
        for n in self.aliases:
            if self.aliases[n]['alias'] == name:
                return n
        return None            
            

print("Number of posts", len(posts))
authors = set([p['author'] for p in posts])
print("Number of authors", len(authors))

num_votes = hist()
num_votes_100pc = hist()
upvoters = hist()
upvoters_100pc = hist()
payout_per_day = hist()
posts_per_day = hist()
beneficiaries = hist()
posts_per_author = hist()
posts_per_author_and_day = {}

for author in authors:
    posts_per_author_and_day[author] = hist()

aliases = Aliases()
for post in posts:
    author = post['author']
    aliases.add(author)
    num_votes.fill(len(post['active_votes']))
    for b in post['beneficiaries']:
        aliases.add(b['account'])
        beneficiaries.fill(aliases.get_alias(b['account']))
    if len(post['beneficiaries']) == 0:
        beneficiaries.fill("None")
    posts_per_author.fill(aliases.get_alias(author))
    posts_per_author_and_day[author].fill(post['created'].date())

    votecount_100pc = 0
    for vote in post['active_votes']:
        aliases.add(vote['voter'])
        if vote['percent'] == 10000:
            votecount_100pc += 1
            upvoters_100pc.fill(aliases.get_alias(vote['voter']))
        upvoters.fill(aliases.get_alias(vote['voter']))

    if votecount_100pc > 0:
        num_votes_100pc.fill(votecount_100pc)
    tpv = post['total_payout_value']
    payout_per_day.fill(post['created'].date(), tpv['amount'])
    posts_per_day.fill(post['created'].date())
    

# Beneficaries
plt.figure(figsize=(12,6))
xrange = range(len(beneficiaries.xrange()))
xlabels = [ "%s (%s SP)" % (alias, aliases.get_alias_sp(alias)) for alias in beneficiaries.xrange()]
plt.bar(xrange, beneficiaries.yrange())
plt.title("Post beneficaries")
plt.xlabel("beneficiary")
plt.ylabel("Occurences")
plt.grid()
plt.gca().xaxis.set_ticks(xrange)
plt.gca().set_xticklabels(xlabels)
plt.gcf().autofmt_xdate(rotation=30)
plt.savefig("beneficiaries.png")

# Number of votes per post
plt.figure(figsize=(12,6))
plt.bar(num_votes.xrange('key'), num_votes.yrange('key'), label="Total number of votes per post")
plt.title("Number of votes per post")
plt.xlabel("Number of votes")
plt.ylabel("Occurences")
plt.grid()
plt.bar(num_votes_100pc.xrange('key'), num_votes_100pc.yrange('key'), label="Number of 100% votes")
plt.legend()
plt.savefig("num_votes_per_post.png")

# Most frequent upvoters
plt.figure(figsize=(12,6))
xrange = range(len(upvoters_100pc.xrange()))[:20]
xlabels = [ "%s (%s SP)" % (alias, aliases.get_alias_sp(alias)) for alias in upvoters_100pc.xrange()[:20]]
plt.bar(xrange, upvoters_100pc.yrange()[:20])
plt.title("TOP 20 Most frequent 100% upvoters")
plt.xlabel("Voter")
plt.ylabel("Number of 100% votes")
plt.grid()
plt.gca().xaxis.set_ticks(xrange)
plt.gca().set_xticklabels(xlabels)
plt.gcf().autofmt_xdate(rotation=30)
plt.savefig("most_frequent_100pc_upvoters.png")

# Posts per author and day
plt.figure(figsize=(12,6))
for author in authors:
    plt.plot_date(posts_per_author_and_day[author].xrange('key'), \
                  posts_per_author_and_day[author].yrange('key'), \
                  label="%s (%s SP)" % (aliases.get_alias(author), aliases.get_account_sp(author)), \
                  linestyle='-')
plt.legend()
plt.grid()
plt.ylim([0, 300])
plt.title("Posts per author and day")
plt.xlabel("Date")
plt.ylabel("Posts per day")
plt.savefig("posts_per_author_and_day.png")

plt.figure(figsize=(12,6))
plt.bar(payout_per_day.xrange('key'), payout_per_day.yrange('key'))
plt.title("Payout per day")
plt.grid()
plt.xlabel("Date")
plt.ylabel("Payout per day (SBD)")
plt.savefig("payout_per_day.png")


for author in authors:
    alias = aliases.get_alias(author)
    sp = aliases.get_account_sp(author)
    num_posts = posts_per_author.entries(alias)
    print("User: %s (%s SP), posts: %d" % (alias, sp, num_posts))

print("user1 SP:", aliases.get_alias_sp("user1"))
