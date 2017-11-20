#!/usr/bin/python

import shelve
import re
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math

class hist:
    def __init__(self):
        self.hist = {}
        self.list_of_values = {}

    def fill(self, key, incr = 1):
        if not key in self.hist:
            self.hist[key] = 0
            self.list_of_values[key] = []
        self.hist[key] += incr
        self.list_of_values[key].append(incr)

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


shelf = shelve.open("/steemdata/steem-transfers.shelf")
transfers = shelf['transfers']
shelf.close()

def get_domain(url):
    split_url = url.split('/')
    if len(split_url) < 3:
        return None
    return split_url[2].lower()

def strip_www(url):
    if url.startswith("www."):
        return url[4:]
    return url

def get_urls(memo):
    return re.findall('http[s]*://[^\s"><]+', memo)

def is_url(memo):
    if re.search('^http[s]*://[^\s"><]+$', memo):
        return True
    else:
        return False

url_only_domains = hist()
contains_url_domains = hist()
memo_type = hist()
memo_type_val = hist()
from_accounts = hist()
to_accounts = hist()
from_accounts_sbd = hist()
to_accounts_sbd = hist()
transfers_per_day = hist()
sbd_per_day = hist()

welcome_list = []

from_accounts_rem = hist()
to_accounts_rem = hist()

keys = []
users = []
amounts = []

for tx in transfers:
    if not tx['amount']['asset'] == "SBD":
        continue
    memo = tx['memo']
    amount =  tx['amount']['amount']
    amounts.append(math.log(amount, 10))
    transfers_per_day.fill(tx['timestamp'].date())
    sbd_per_day.fill(tx['timestamp'].date(), amount)
    from_accounts.fill(tx['from'])
    to_accounts.fill(tx['to'])
    from_accounts_sbd.fill(tx['from'], amount)
    to_accounts_sbd.fill(tx['to'], amount)
    #print(tx)

    if memo == "":
        memo_type.fill("no-memo")
        memo_type_val.fill("no-memo", amount)
        continue

    if memo[0]=="5" and len(memo)==51:
        memo_type.fill("private-key")
        memo_type_val.fill("private-key", amount)
        continue

    if memo.startswith("STM") and len(memo)==53:
        memo_type.fill("public-key")
        memo_type_val.fill("public-key", amount)
        continue

    # only URL
    if is_url(memo):
        domain = strip_www(get_domain(memo))
        url_only_domains.fill(domain)
        memo_type.fill("url-only")
        memo_type_val.fill("url-only", amount)
        continue

    # contains URL
    urls = get_urls(memo)
    if urls:
        for url in urls:
            domain = strip_www(get_domain(url))
            contains_url_domains.fill(domain)
        memo_type.fill("contains-url")
        memo_type_val.fill("contains-url", amount)
        continue

    # encrypted memo
    if memo.startswith("#"):
        memo_type.fill("encrypted")
        continue

    # from or to exchanges
    exchanges = ['bittrex', 'blocktrades', 'changelly', 'poloniex',
                 'hitbtc-exchange', 'openledger-dex', 'tradeqwik', 'privex']
    is_exchange_related = False
    for exchange in exchanges:
        if tx['from'] == exchange or tx['to'] == exchange:
            memo_type.fill("exchange")
            memo_type_val.fill("exchange", amount)
            is_exchange_related = True
            break
    if is_exchange_related:
        continue

    if tx['to'] == "null":
        memo_type.fill("null")
        memo_type_val.fill("null", amount)
        continue

    # from or to special accounts
    accounts = ['minnowbooster', 'boomerang', 'booster', 'steemdice1',
                'randowhale', 'bellyrub', 'tipu', 'resteembot',
                'steemfollower', 'steemauto', 'streemian',
                'minnowsupport', 'banjo', 'justyy', 'buildawhale',
                'steemdunk', 'lovejuice', 'curiositybot', 'steemiex',
                'pushup', 'appreciator', 'upgoater', 'minnowpowerup',
                'polsza', 'reblogger', 'morwhale', 'minnowhelper']
    is_account_related = False
    for account in accounts:
        if tx['from'] == account or tx['to'] == account:
            memo_type.fill("bot-interactions")
            memo_type_val.fill("bot-interactions", amount)
            is_account_related = True
            break
    if is_account_related:
        continue

    # contests/giveaways
    keywords = ['winner', 'congratulation', 'giveaway', 'contest',
                'challenge', 'lucksacks.com', 'congrats', 'winning',
                'gewinn', 'award', 'reward']
    is_constest_related = False
    for keyword in keywords:
        if keyword in memo.lower():
            memo_type.fill("contests-giveaways")
            memo_type_val.fill("contests-giveaways", amount)
            is_constest_related = True
            break
    if is_constest_related:
        continue

    # known giveaway users
    accounts = ['juicypop', 'uxair', 'honolulu', 'lazarescu.irinel',
                'karmashine', 'uxair', 'ralph-rennoldson',
                'lotterysbd', 'steemsports']
    is_constest_related = False
    for account in accounts:
        if account == tx['from']:
            memo_type.fill("contests-giveaways")
            memo_type_val.fill("contests-giveaways", amount)
            is_constest_related = True
            break
    if is_constest_related:
        continue

    # bank related
    keywords = ["deposit", "withdraw", "balance", "saldo", "payout", "dividend"]
    is_bank_related = False
    for keyword in keywords:
        if keyword in memo.lower():
            memo_type.fill("bank")
            memo_type_val.fill("bank", amount)
            is_bank_related = True
            break
    if is_bank_related:
        continue

    # re-steem related
    is_resteem_related = False
    keywords = ["resteem", "re-steem", 'trump3t']
    for keyword in keywords:
        if keyword in memo.lower():
            memo_type.fill("service-ads")
            memo_type_val.fill("service-ads", amount)
            is_resteem_related = True
            break
    if is_resteem_related:
        continue

    # Error messages
    #if memo.lower().startswith("sorry"):
    #    memo_type.fill("errors")
    #    continue

    errors = ['refund', 'invalid', 'error', 'sorry']
    is_error_related = False
    for error in errors:
        if error in memo.lower():
            memo_type.fill("bot-interactions")
            memo_type_val.fill("bot-interactions", amount)
            is_error_related = True
            break
    if is_error_related:
        continue

    # Welcome to Steem
    keywords = ["welcome to steem"]
    is_welcome_related = False
    for keyword in keywords:
        if keyword in memo.lower():
            is_welcome_related = True
            break
    if is_welcome_related:
        memo_type.fill("welcome")
        memo_type_val.fill("welcome", amount)
        welcome_list.append(tx['amount']['amount'])
        #print(tx)
        continue

    # Upvote advertisments
    keywords = ["up-vote", "upvote"]
    is_upvote_related = False
    for keyword in keywords:
        if keyword in memo.lower():
            is_upvote_related = True
            break
    if is_upvote_related:
        #print(tx['from'], tx['to'], tx['amount'], memo)
        memo_type.fill("service-ads")
        memo_type_val.fill("service-ads", tx['amount']['amount'])
        continue

    # steemthat
    if "steemthat.com" in memo.lower() or \
       "now steem like." in memo.lower():
        memo_type.fill("service-ads")
        memo_type_val.fill("service-ads", tx['amount']['amount'])
        continue

    memo_type.fill("other")
    memo_type_val.fill("other", tx['amount']['amount'])
    from_accounts_rem.fill(tx['from'])
    to_accounts_rem.fill(tx['to'])
    #print(tx['from'], tx['to'], tx['amount'], memo)

print("Num transfers: ", len(amounts))
print("url_only_domains: ", url_only_domains.xrange(), url_only_domains.yrange())
print("contains url: ", contains_url_domains.xrange(), contains_url_domains.yrange())
print("from rem: ", from_accounts_rem.xrange()[:20])
print("to rem: ", to_accounts_rem.xrange()[:20])
print("memo_type", memo_type.xrange(), memo_type.yrange())


# Amount histo
labels = [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000, 100000]
plt.figure(figsize=(12, 6))
plt.hist(amounts, bins=100, log=True)
plt.grid()
plt.gca().xaxis.set_ticks(range(-3, 5))
plt.gca().set_xticklabels(labels)
plt.title("Number of transactions per transfer amount")
plt.xlabel("Transfer amount (SBD)")
plt.ylabel("Number of transactions")
plt.savefig("amounts.png")

# transfers per day
plt.figure(figsize=(12, 6))
plt.bar(transfers_per_day.xrange(), transfers_per_day.yrange())
plt.title("Number of transactions per day")
plt.xlabel("Date")
plt.ylabel("Number of transactions")
plt.ylim([0, max(transfers_per_day.yrange()) * 1.1])
plt.savefig("transactions_per_day.png")

# SBD per day
plt.figure(figsize=(12, 6))
plt.bar(sbd_per_day.xrange(), sbd_per_day.yrange())
plt.title("Accumulated amounts of SBD transferred per day")
plt.xlabel("Date")
plt.grid()
plt.ylabel("daily sum of transfer amounts (SBD)")
plt.ylim([0, max(sbd_per_day.yrange()) * 1.1])
plt.savefig("sbd_per_day.png")

# transfers per day
plt.figure(figsize=(12, 6))
plt.bar(transfers_per_day.xrange(), transfers_per_day.yrange())
plt.title("Number of transactions per day")
plt.xlabel("Date")
plt.ylabel("Number of transactions")
plt.ylim([0, max(transfers_per_day.yrange()) * 1.1])
plt.savefig("transactions_per_day.png")


# Transfers per category
plt.figure(figsize=(12,6))
xrange = range(len(memo_type.xrange()))
plt.bar(xrange, memo_type.yrange(), log=True)
plt.gca().xaxis.set_ticks(xrange)
plt.gca().set_xticklabels(memo_type.xrange())
plt.gcf().autofmt_xdate(rotation=30)
plt.title("Overall number of SBD transfers per category")
plt.ylabel("Number of transfers")
plt.grid()
plt.savefig("memo_types.png")


plt.figure(figsize=(12,6))
xrange = range(len(memo_type_val.xrange()))
plt.bar(xrange, memo_type_val.yrange(), log=True)
plt.gca().xaxis.set_ticks(xrange)
plt.gca().set_xticklabels(memo_type_val.xrange())
plt.gcf().autofmt_xdate(rotation=30)
plt.title("Sum of SBD transferred per category")
plt.ylabel("Sum of SBD transferred")
plt.grid()
plt.savefig("memo_types_values.png")

# URL-Only posts distribution
plt.figure(figsize=(12,6))
xrange = range(len(url_only_domains.xrange()[:20]))
plt.bar(xrange, url_only_domains.yrange()[:20], log=True)
plt.gca().xaxis.set_ticks(xrange)
plt.gca().set_xticklabels(url_only_domains.xrange()[:20])
plt.gcf().autofmt_xdate(rotation=30)
plt.title("Domains in URL-only transfer memos")
plt.ylabel("Number of occurences")
plt.grid()
plt.savefig("url_only_distribution.png")

# posts with URL distribution
plt.figure(figsize=(12,6))
xrange = range(len(contains_url_domains.xrange()[:20]))
plt.bar(xrange, contains_url_domains.yrange()[:20], log=True)
plt.gca().xaxis.set_ticks(xrange)
plt.gca().set_xticklabels(contains_url_domains.xrange()[:20])
plt.gcf().autofmt_xdate(rotation=30)
plt.title("Domains included in transfer memos")
plt.ylabel("Number of occurences")
plt.grid()
plt.savefig("contains_url_distribution.png")

# median transfer size per category
plt.figure(figsize=(12,6))
xrange = range(len(memo_type_val.xrange()))
yrange = [np.median(memo_type_val.list_of_values[x]) for x in memo_type_val.xrange()]
plt.bar(xrange, yrange, log=True)
plt.gca().xaxis.set_ticks(xrange)
plt.gca().set_xticklabels(memo_type_val.xrange())
plt.gcf().autofmt_xdate(rotation=30)
plt.title("Median SBD value per transfer for each category")
plt.ylabel("Median SBD value")
plt.grid()
plt.savefig("avg_transaction_sizes.png")

print(len(welcome_list), np.mean(welcome_list), np.median(welcome_list), min(welcome_list), max(welcome_list))


# from accounts
top = 30
plt.figure(figsize=(12,6))
xrange = range(len(from_accounts.xrange()[:top]))
plt.bar(xrange, from_accounts.yrange()[:top], log=False)
plt.gca().xaxis.set_ticks(xrange)
plt.gca().set_xticklabels(from_accounts.xrange()[:top])
plt.gcf().autofmt_xdate(rotation=30)
plt.title("TOP%d senders (number of transactions)" % top)
plt.ylabel("Number of transactions as sender")
plt.grid()
#plt.ylim([1, max(from_accounts.yrange())*1.1])
plt.savefig("from_accounts.png")

# to accounts
plt.figure(figsize=(12,6))
xrange = range(len(to_accounts.xrange()[:top]))
plt.bar(xrange, to_accounts.yrange()[:top], log=False)
plt.gca().xaxis.set_ticks(xrange)
plt.gca().set_xticklabels(to_accounts.xrange()[:top])
plt.gcf().autofmt_xdate(rotation=30)
plt.title("TOP20 receivers (number of transactions)")
plt.ylabel("Number of received transactions")
plt.grid()
plt.savefig("to_accounts.png")

# from accounts SBD
top = 30
plt.figure(figsize=(12,6))
xrange = range(len(from_accounts_sbd.xrange()[:top]))
plt.bar(xrange, from_accounts_sbd.yrange()[:top], log=False)
plt.gca().xaxis.set_ticks(xrange)
plt.gca().set_xticklabels(from_accounts_sbd.xrange()[:top])
plt.gcf().autofmt_xdate(rotation=30)
plt.title("TOP%d senders (sum of SBD amounts)" % top)
plt.ylabel("Total SBD sent")
plt.grid()
#plt.ylim([1, max(from_accounts.yrange())*1.1])
plt.savefig("from_accounts.png")

# to accounts
plt.figure(figsize=(12,6))
xrange = range(len(to_accounts_sbd.xrange()[:top]))
plt.bar(xrange, to_accounts_sbd.yrange()[:top], log=False)
plt.gca().xaxis.set_ticks(xrange)
plt.gca().set_xticklabels(to_accounts_sbd.xrange()[:top])
plt.gcf().autofmt_xdate(rotation=30)
plt.title("TOP20 receivers (sum of SBD amounts)")
plt.ylabel("Total SBD received")
plt.grid()
plt.savefig("to_accounts.png")
