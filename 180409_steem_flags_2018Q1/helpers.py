#!/usr/bin/python
from steem import Steem
from steem.amount import Amount
import math

def get_pending_payout(rshares):
    s = Steem()
    props = s.steemd.get_dynamic_global_properties()
    feed = s.steemd.get_feed_history()
    rf = s.steemd.get_reward_fund()
    pot = Amount(rf['reward_balance']).amount
    base = feed['current_median_history']['base']
    quote = feed['current_median_history']['quote']
    median_price = Amount(base).amount / Amount(quote).amount
    pot = pot * median_price
    total_r2 = int(rf['recent_claims'])
    r2 = rshares
    r2 *= pot
    r2 /= total_r2
    return r2


def reputation(raw_reputation):
    rep = int(raw_reputation)
    if rep == 0:
        return 25
    score = max([math.log10(abs(rep)) - 9, 0]) * 9 + 25
    if rep < 0:
        score = 50 - score
    return score
