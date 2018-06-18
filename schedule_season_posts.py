#!/usr/bin/env python

import praw
import json
import argparse
from datetime import datetime, timedelta, time

epi_data_sr = 'buffytester'
epi_data_dir = 'epi_data'
post_days = [0, 2, 5]       # starting at day 0 (MOnday), when next to post in days. [0, 3] == Monday, Thrusday
post_time = 13           # in UTC from 0 15 == 3PM

# Given a day and hour, return the datetime of that hour and day next week. day starts with Monday at 0.
def next_week_at_hour(now, day, hour):
    next_hour = time(hour=hour)
    now += timedelta(days=day)
    if now.time() < next_hour:
        now = now.combine(now.date(), next_hour)
    else:
        now = now.combine(now.date(), next_hour) + timedelta(days=1)

    return now + timedelta((day - now.weekday()) % 7)

parser = argparse.ArgumentParser(description='Schedule episode of rhe week posts on /r/buffy and /r/ANGEL.')
parser.add_argument('-s', '--season', type=int, dest='season', help='Which season to schedule. Can be given '
                    'multiple times', required=True, action='append')
parser.add_argument('--show', type=str, dest='show', help='Which show to schedule.',
                    choices=['buffy', 'angel'], required=True)
parser.add_argument('-d', dest='debug', help='If true, do not write to wiki, just print to stdout.',
                    action='store_true')
parser.add_argument('-p', '--publishto', dest='publishto', help='If given publish to the subreddit listed'
                    ' instead of the one given in the "show" argument.')
parser.add_argument('--day', type=int, dest='start_day', help='Which days of the week to start the posts on. Mon=0, Tue=1, etc')
args = parser.parse_args()

publishto = args.publishto if args.publishto else args.show

# connect to reddit
r = praw.Reddit(site_name='buffy_scripts', user_agent='buffybot_scraper by /u/phil_s_stien')

schedule = ('###### If you edit this page, you must [click this link, then click "send"]'
            '(http://www.reddit.com/message/compose/?to=AutoModerator&subject={}&message=schedule)'
            'to have AutoModerator re-load the schedule from here'.format(publishto))

start_day = 0 if not args.start_day else args.start_day
start_time = next_week_at_hour(datetime.now() - timedelta(days=1), start_day, post_time)
for season in args.season:
    wiki_path = '{}/{}/season_{}'.format(epi_data_dir, args.show, season) # e.g. "epi_data/buffy/season_1"
    page = r.subreddit(epi_data_sr).wiki[wiki_path]
    ep_nums = json.loads(page.content_md)

    for i, ep_num in enumerate(ep_nums):
        page = r.subreddit(epi_data_sr).wiki['{}/{}'.format(wiki_path, ep_num)]
        print('Loading wiki page {}'.format(page))
        ep = json.loads(page.content_md)

        days = (int(i/len(post_days))*7) + post_days[i%len(post_days)]
        first = start_time + timedelta(days=days)
        ep_data = ('\n---\n'
                '    first: "{}"\n'
                '    title: "{}"\n'
                '    sticky: true\n'
                '    distinguish: true\n'
                '    text: |\n'.format(first.strftime("%Y-%m-%d %H:%M:%S"), ep['title']))
        for line in ep['selftext'].split('\n'):
            ep_data += '        {}\n'.format(line)

        schedule += ep_data

if not args.debug:
    r.subreddit(publishto).wiki['automoderator-schedule'].edit(
        content=schedule, reason='scheduled weekly posts for season {}'.format(args.season))
    print('scheduled weekly posts for {} season {}.'.format(args.show, args.season))
    print('Now go to https://www.reddit.com/r/{}/wiki/automoderator-schedule and click the link to notify'
        'automoderator about the update.'.format(args.show))
else:
    print(schedule)

exit(0)
