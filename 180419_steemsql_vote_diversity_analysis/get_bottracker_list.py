#!/usr/bin/python
import requests

bid_bots_url = 'https://steembottracker.net/bid_bots'
other_bots_url = 'https://steembottracker.net/other_bots'

own_bots = ['busy.pay', 'minnowbooster', 'smartmarket']
dapps = ['esteemapp', 'busy.org', 'utopian-io', 'dlive', 'dmania', 'dtube', 'dsound', 'zappl']
cleaners = ['steemcleaners', 'spaminator', 'blacklist-a', 'mack-bot', 'cheetah']

r = requests.get(bid_bots_url)
data = r.json()
botlist = ""
for entry in data:
    botlist += entry['name'] + "\n"
    #bid_bots.append(entry['name'])

r = requests.get(other_bots_url)
data = r.json()
for entry in data:
    botlist += entry['name'] + "\n"
    #other_bots.append(entry['name'])

for acc in own_bots:
    botlist += acc + "\n"

for acc in dapps:
    botlist += acc + "\n"

for acc in cleaners:
    botlist += acc + "\n"

with open("bots.txt", "w") as f:
    f.write(botlist)
