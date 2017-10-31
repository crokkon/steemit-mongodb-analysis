#!/usr/bin/python

import datetime as dt
import shelve
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

shelf = shelve.open("/steemdata/steem-apps.shelf")
posts = shelf['posts']
#comments = shelf['comments']
shelf.close()

def sort_by_value(dict, reverse=False):
    return sorted(dict.items(), key=lambda k: (k[1], k[0]), reverse=reverse)

def increment_kv(dict, key, increment=1):
    if not key in dict:
        dict[key] = 0
    dict[key] += increment

postdates = sorted(posts)
pltvals = {}
pltdates = {}
dailypostdates = []
dailytotalposts = []
dailysteemitposts = []
dailyotherposts = []
appcategories = {}

for date in postdates:
    appcounts = {}
    totalposts = len(posts[date])
    totalsteemitposts = 0
    totalotherposts = 0
    for post in posts[date]:
        app = "unknown"
        if 'json_metadata' in post and 'app' in post['json_metadata']:
            app = post['json_metadata']['app']
            if type(app) == list:
                app = app[0]            
            if "/" in app:
                app = app.split("/")[0]
            if app == "":
                app = "unknown"
        increment_kv(appcounts, app)
        if "steemit" in app:
            totalsteemitposts += 1
        else:
            totalotherposts += 1

        category = post['category']
        if not app in appcategories:
            appcategories[app] = {}
        increment_kv(appcategories[app], category)

    for app in appcounts:
        if not app in pltvals:
            pltvals[app] = []
            pltdates[app] = []
        pltvals[app].append(appcounts[app])
        pltdates[app].append(date)
        
    dailypostdates.append(date)
    dailytotalposts.append(totalposts)
    dailysteemitposts.append(totalsteemitposts)
    dailyotherposts.append(totalotherposts)

from_date_str = dt.datetime.strftime(min(dailypostdates), "%b/%d %Y")
to_date_str = dt.datetime.strftime(max(dailypostdates), "%b/%d %Y")
xFmt = mdates.DateFormatter('%m/%d')


###################################################
# Total posts per app
###################################################
total_app_posts = []
total_app_posts_labels = []
for app in sorted(pltvals, key=lambda k: sum(pltvals[k]), reverse=True):
    total = sum(pltvals[app])
    if total > 20:
        total_app_posts.append(total)
        total_app_posts_labels.append(app)

xticks = range(0, len(total_app_posts))
plt.figure(figsize=(12, 6))
plt.grid()
plt.bar(xticks, total_app_posts, label="Total posts per app", log=True)
plt.text(len(total_app_posts)/3*2, max(total_app_posts)/10, \
         "Total number of unique apps: %d" % len(pltvals), \
         fontsize=12, bbox={'facecolor':'white'})
plt.gca().xaxis.set_ticks(xticks)
plt.gca().set_xticklabels(total_app_posts_labels)
plt.gcf().autofmt_xdate(rotation=30)
plt.ylim([1e1, 2*total_app_posts[0]])
plt.legend()
plt.ylabel("Number of posts")
plt.title("Number of posts per app (%s - %s)" % (from_date_str, to_date_str))
plt.figtext(0.99, 0.01, "@crokkon", horizontalalignment="right", verticalalignment="bottom")
plt.savefig("/steemdata/total_posts_per_app.png")


###################################################
# Post per day
###################################################
plt.figure(figsize=(12, 6))
plt.grid()
plt.plot_date(dailypostdates, dailytotalposts, linestyle='-', marker="None", label="Total posts per day")
plt.plot_date(dailypostdates, dailysteemitposts, linestyle='-', marker="None", label="Posts per day from steemit")
plt.plot_date(dailypostdates, dailyotherposts, linestyle='-', marker="None", label="Posts per day from other apps")
plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_formatter(xFmt)
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
plt.ylim([0, 1.2*max(dailytotalposts)])
plt.legend()
plt.xlabel("Date")
plt.ylabel("Number of posts")
plt.title("Total number of posts per day from steemit and other apps (%s - %s)" % (from_date_str, to_date_str))
plt.figtext(0.99, 0.01, "@crokkon", horizontalalignment="right", verticalalignment="bottom")
plt.savefig("/steemdata/dailyposts.png")


###################################################
# Posts per app and day, all but steemit
###################################################
plt.figure(figsize=(12, 6))
plt.grid()
for app in sorted(pltvals, key=lambda k: max(pltvals[k]), reverse=True):
    maxval = max(pltvals[app])
    if maxval <= 100 or 'steemit' in app:
        continue
    plt.plot_date(pltdates[app], pltvals[app], label=app, linestyle="-", marker="None")

plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)
plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_formatter(xFmt)
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
box = plt.gca().get_position()
plt.gca().set_position([box.x0, box.y0, box.width * 0.9, box.height])
plt.figtext(0.99, 0.01, "@crokkon", horizontalalignment="right", verticalalignment="bottom")
plt.xlabel("Date")
plt.ylabel("Posts per day")
plt.title("Number of posts per day and app (%s - %s)" % (from_date_str, to_date_str))
plt.savefig("/steemdata/apps_3rdparty.png")


###################################################
# Posts per app and day, gainers
###################################################
plt.figure(figsize=(12, 6))
plt.grid()
apps = ['steemjs', 'steemjs-test!', 'dtube', 'steepshot', 'busy', 'zappl', 'chainbb', 'utopian-io']
for app in sorted(pltvals, key=lambda k: max(pltvals[k]), reverse=True):
    if not app in apps:
        continue
    plt.plot_date(pltdates[app], pltvals[app], label=app, linestyle="-", marker="None")

plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)
plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_formatter(xFmt)
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
box = plt.gca().get_position()
plt.gca().set_position([box.x0, box.y0, box.width * 0.9, box.height])
plt.figtext(0.99, 0.01, "@crokkon", horizontalalignment="right", verticalalignment="bottom")
plt.title("Number of post per 3rd-party app per day, gainers (%s - %s)" % (from_date_str, to_date_str))
plt.xlabel("Date")
plt.ylabel("Posts per day")
plt.savefig("/steemdata/apps_gainers.png")
    
###################################################
# App categories
###################################################
apps = ['steemit', 'steemjs', 'busy', 'steepshot', 'chainbb', 'zappl', 'esteem', 'dtube']

fig, axarr = plt.subplots(4, 2, figsize=(6, 12))
plt.suptitle("Categories for posts from various apps (%s - %s)" % (from_date_str, to_date_str))
idx = 0
for app in apps:
    if not app in appcategories:
        continue
    catlist = appcategories[app]
    catsum = sum([catlist[x] for x in catlist])
    values = [x[1] for x in sort_by_value(catlist, reverse=True)]
    if len(values) > 10:
        values_cut = [x for x in values if x/catsum >= 0.01]
        others = sum(values[len(values_cut):])
        labels = [x[0] for x in sort_by_value(catlist, reverse=True)[:len(values_cut)]]
        values_cut.append(others)
        labels.append("others")
    else:
        values_cut = values
        labels = [x[0] for x in sort_by_value(catlist, reverse=True)]

    col = (idx & 1)
    row = (idx >> 1)
    axarr[row, col].pie(values_cut, labels=labels, autopct="%d%%", startangle=90, rotatelabels=False, pctdistance=0.9)
    axarr[row, col].set_title(app)
    idx += 1


fig.subplots_adjust(hspace=0.3)
plt.figtext(0.99, 0.01, "@crokkon", horizontalalignment="right", verticalalignment="bottom")
plt.savefig("piechart.png")
[root@iri13 bca_apps]# v analyze.py 
[root@iri13 bca_apps]# cat analyze.py 
#!/usr/bin/python

import datetime as dt
import shelve
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

shelf = shelve.open("/steemdata/steem-apps.shelf")
posts = shelf['posts']
#comments = shelf['comments']
shelf.close()

def sort_by_value(dict, reverse=False):
    return sorted(dict.items(), key=lambda k: (k[1], k[0]), reverse=reverse)

def increment_kv(dict, key, increment=1):
    if not key in dict:
        dict[key] = 0
    dict[key] += increment

postdates = sorted(posts)
pltvals = {}
pltdates = {}
dailypostdates = []
dailytotalposts = []
dailysteemitposts = []
dailyotherposts = []
appcategories = {}

for date in postdates:
    appcounts = {}
    totalposts = len(posts[date])
    totalsteemitposts = 0
    totalotherposts = 0
    for post in posts[date]:
        app = "unknown"
        if 'json_metadata' in post and 'app' in post['json_metadata']:
            app = post['json_metadata']['app']
            if type(app) == list:
                app = app[0]            
            if "/" in app:
                app = app.split("/")[0]
            if app == "":
                app = "unknown"
        increment_kv(appcounts, app)
        if "steemit" in app:
            totalsteemitposts += 1
        else:
            totalotherposts += 1

        category = post['category']
        if not app in appcategories:
            appcategories[app] = {}
        increment_kv(appcategories[app], category)

    for app in appcounts:
        if not app in pltvals:
            pltvals[app] = []
            pltdates[app] = []
        pltvals[app].append(appcounts[app])
        pltdates[app].append(date)
        
    dailypostdates.append(date)
    dailytotalposts.append(totalposts)
    dailysteemitposts.append(totalsteemitposts)
    dailyotherposts.append(totalotherposts)

from_date_str = dt.datetime.strftime(min(dailypostdates), "%b/%d %Y")
to_date_str = dt.datetime.strftime(max(dailypostdates), "%b/%d %Y")
xFmt = mdates.DateFormatter('%m/%d')


###################################################
# Total posts per app
###################################################
total_app_posts = []
total_app_posts_labels = []
for app in sorted(pltvals, key=lambda k: sum(pltvals[k]), reverse=True):
    total = sum(pltvals[app])
    if total > 20:
        total_app_posts.append(total)
        total_app_posts_labels.append(app)

xticks = range(0, len(total_app_posts))
plt.figure(figsize=(12, 6))
plt.grid()
plt.bar(xticks, total_app_posts, label="Total posts per app", log=True)
plt.text(len(total_app_posts)/3*2, max(total_app_posts)/10, \
         "Total number of unique apps: %d" % len(pltvals), \
         fontsize=12, bbox={'facecolor':'white'})
plt.gca().xaxis.set_ticks(xticks)
plt.gca().set_xticklabels(total_app_posts_labels)
plt.gcf().autofmt_xdate(rotation=30)
plt.ylim([1e1, 2*total_app_posts[0]])
plt.legend()
plt.ylabel("Number of posts")
plt.title("Number of posts per app (%s - %s)" % (from_date_str, to_date_str))
plt.figtext(0.99, 0.01, "@crokkon", horizontalalignment="right", verticalalignment="bottom")
plt.savefig("/steemdata/total_posts_per_app.png")


###################################################
# Post per day
###################################################
plt.figure(figsize=(12, 6))
plt.grid()
plt.plot_date(dailypostdates, dailytotalposts, linestyle='-', marker="None", label="Total posts per day")
plt.plot_date(dailypostdates, dailysteemitposts, linestyle='-', marker="None", label="Posts per day from steemit")
plt.plot_date(dailypostdates, dailyotherposts, linestyle='-', marker="None", label="Posts per day from other apps")
plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_formatter(xFmt)
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
plt.ylim([0, 1.2*max(dailytotalposts)])
plt.legend()
plt.xlabel("Date")
plt.ylabel("Number of posts")
plt.title("Total number of posts per day from steemit and other apps (%s - %s)" % (from_date_str, to_date_str))
plt.figtext(0.99, 0.01, "@crokkon", horizontalalignment="right", verticalalignment="bottom")
plt.savefig("/steemdata/dailyposts.png")


###################################################
# Posts per app and day, all but steemit
###################################################
plt.figure(figsize=(12, 6))
plt.grid()
for app in sorted(pltvals, key=lambda k: max(pltvals[k]), reverse=True):
    maxval = max(pltvals[app])
    if maxval <= 100 or 'steemit' in app:
        continue
    plt.plot_date(pltdates[app], pltvals[app], label=app, linestyle="-", marker="None")

plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)
plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_formatter(xFmt)
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
box = plt.gca().get_position()
plt.gca().set_position([box.x0, box.y0, box.width * 0.9, box.height])
plt.figtext(0.99, 0.01, "@crokkon", horizontalalignment="right", verticalalignment="bottom")
plt.xlabel("Date")
plt.ylabel("Posts per day")
plt.title("Number of posts per day and app (%s - %s)" % (from_date_str, to_date_str))
plt.savefig("/steemdata/apps_3rdparty.png")


###################################################
# Posts per app and day, gainers
###################################################
plt.figure(figsize=(12, 6))
plt.grid()
apps = ['steemjs', 'steemjs-test!', 'dtube', 'steepshot', 'busy', 'zappl', 'chainbb', 'utopian-io']
for app in sorted(pltvals, key=lambda k: max(pltvals[k]), reverse=True):
    if not app in apps:
        continue
    plt.plot_date(pltdates[app], pltvals[app], label=app, linestyle="-", marker="None")

plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)
plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_formatter(xFmt)
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
box = plt.gca().get_position()
plt.gca().set_position([box.x0, box.y0, box.width * 0.9, box.height])
plt.figtext(0.99, 0.01, "@crokkon", horizontalalignment="right", verticalalignment="bottom")
plt.title("Number of post per 3rd-party app per day, gainers (%s - %s)" % (from_date_str, to_date_str))
plt.xlabel("Date")
plt.ylabel("Posts per day")
plt.savefig("/steemdata/apps_gainers.png")
    
###################################################
# App categories
###################################################
apps = ['steemit', 'steemjs', 'busy', 'steepshot', 'chainbb', 'zappl', 'esteem', 'dtube']

fig, axarr = plt.subplots(4, 2, figsize=(6, 12))
plt.suptitle("Categories for posts from various apps (%s - %s)" % (from_date_str, to_date_str))
idx = 0
for app in apps:
    if not app in appcategories:
        continue
    catlist = appcategories[app]
    catsum = sum([catlist[x] for x in catlist])
    values = [x[1] for x in sort_by_value(catlist, reverse=True)]
    if len(values) > 10:
        values_cut = [x for x in values if x/catsum >= 0.01]
        others = sum(values[len(values_cut):])
        labels = [x[0] for x in sort_by_value(catlist, reverse=True)[:len(values_cut)]]
        values_cut.append(others)
        labels.append("others")
    else:
        values_cut = values
        labels = [x[0] for x in sort_by_value(catlist, reverse=True)]

    col = (idx & 1)
    row = (idx >> 1)
    axarr[row, col].pie(values_cut, labels=labels, autopct="%d%%", startangle=90, rotatelabels=False, pctdistance=0.9)
    axarr[row, col].set_title(app)
    idx += 1


fig.subplots_adjust(hspace=0.3)
plt.figtext(0.99, 0.01, "@crokkon", horizontalalignment="right", verticalalignment="bottom")
plt.savefig("/steemdata/piechart.png")
