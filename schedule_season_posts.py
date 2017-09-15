#!/usr/bin/env python

import praw
import json
import argparse
from datetime import datetime, timedelta
from time import time

epi_data_sr = 'buffytester'
epi_data_dir = 'epi_data'

parser = argparse.ArgumentParser(description='Schedule episode of rhe week posts on /r/buffy and /r/ANGEL.')
parser.add_argument('--season', type=int, dest='season', help='Which season to schedule.', required=True)
parser.add_argument('--show', type=str, dest='show', help='Which show to schedule.',
                    choices=['buffy', 'angel'], required=True)
args = parser.parse_args()

# connect to reddit
r = praw.Reddit(site_name='buffy_scripts', user_agent='buffybot_scraper by /u/phil_s_stien')

wiki_path = '{}/{}/season_{}'.format(epi_data_dir, args.show, args.season) # e.g. "epi_data/buffy/season_1"
page = r.subreddit(epi_data_sr).wiki[wiki_path]
ep_nums = json.loads(page.content_md)

schedule = ('###### If you edit this page, you must [click this link, then click "send"]'
            '(http://www.reddit.com/message/compose/?to=AutoModerator&subject={}&message=schedule)'
            'to have AutoModerator re-load the schedule from here'.format('buffytester'))

start_time = datetime.utcnow() + timedelta(minutes=10)
for i, ep_num in enumerate(ep_nums):
    page = r.subreddit(epi_data_sr).wiki['{}/{}'.format(wiki_path, ep_num)]
    ep = json.loads(page.content_md)
    first = start_time + timedelta(weeks=i)
    ep_data = '\n---\n    first: "{}"\n    title: "{}"\n    distinguish: true\n    text: |\n'.format(
        first.strftime("%Y-%m-%d %H:%M:%S"),
        ep['title']
    )
    for line in ep['selftext'].split('\n'):
        ep_data += '        {}\n'.format(line)

    schedule += ep_data

r.subreddit('buffytester').wiki['automoderator-schedule'].edit(
    content=schedule, reason='scheduled weekly posts for season {}'.format(args.season))

print('scheduled weekly posts for {} season {}.'.format(args.show, args.season))
print('Now go to https://www.reddit.com/r/{}/wiki/automoderator-schedule and click the link to notify'
      'automoderator about the update.'.format(args.show))

exit(0)
