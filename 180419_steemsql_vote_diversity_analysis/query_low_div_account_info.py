#!/usr/bin/python

from steem import Steem
import shelve
import sys

s = shelve.open("low_div_accounts.shelf")
accounts = list(s['accounts'])
s.close()

count = len(accounts)
i = 0
acc_infos = []
batch = 100
s = Steem()
while i < len(accounts):
    accnames = accounts[i:i+batch]
    print(accnames)
    accs = s.steemd.call('get_accounts', accnames)
    acc_infos.extend(accs)
    #print(accs)
    i += batch
    #break
#     acc_infos.append(dict(Account(a)))
#     index += 1
#     sys.stdout.write("\r%d / %d (%.1f%%)" % (index, count, index * 100 /count))

s = shelve.open("account_infos.shelf")
s['accounts'] = acc_infos
s.close()
