#!/usr/bin/env python

import praw
import json
import argparse
from sys import stderr
from datetime import datetime, timedelta
from time import time

epi_data_sr = 'buffytester'
epi_data_dir = 'epi_data'

# connect to reddit
r = praw.Reddit(site_name='buffy_scripts', user_agent='buffybot_scraper by /u/phil_s_stien')

# grab the episode data from previous posts. 
subs = {}
for submission in r.redditor('buffy_bot').submissions.new(limit=None):
    if 'episode' in submission.title.lower():
        sub_name = submission.subreddit.display_name
        if sub_name not in subs:
            subs[sub_name] = []
      
        # episode removed by someone - do not include.
        if submission.banned_by:
            continue

        subs[sub_name].append(submission)

# Some eps were not posted by buffy_bot. These need to be added "by hand".
eps_missing = {
    'buffy': [
        '3h7axj',   # b20
        '3i3572',   # b21
        '3juuxg',   # b22
        '3ks9tg',   # b25
        '3l68hr',   # b26
        '3za3wm',   # b46
    ]
}

for sub_name, sids in eps_missing.items():
    for sid in sids:
        subs[sub_name].append(praw.models.Submission(r, sid))

ep_data = {}
for sr, sb in subs.items():
    ep_data[sr] = []
    for i, s in enumerate(sorted(sb, key=lambda x: x.created_utc)):
        season_str = s.title[s.title.find('(')+1:s.title.find(')')]
        if 'x' in season_str:
            season = str(int(season_str.split('x')[0]))
        else:
            season = str(int(season_str.split(' ')[0].split('S')[1]))

        ep_data[sr].append({
            'created_utc': s.created_utc,
            'title': s.title,
            'selftext': s.selftext,
            'subreddit': sr,
            'episode_number': format(i+1, '03d'),
            'season': season
        })

        if str(i+1) not in s.title:
            print('ERROR in episode sequence at: {} ep {}, {}'.format(sr, i+1, s.title), file=stderr)

for sr, eps in ep_data.items():
    # keep track of ep num to season map so we can add them to the wiki for later iteration.
    ep_nums = {}
    for ep in eps:
        page = r.subreddit(epi_data_sr).wiki['{}/{}/season_{}/{}'.format(
            epi_data_dir, sr, ep['season'], ep['episode_number'])]
        page.edit(content=json.dumps(ep, indent=4, sort_keys=True))

        if ep['season'] not in ep_nums:
            ep_nums[ep['season']] = []

        ep_nums[ep['season']].append(ep['episode_number'])

    for s_num, s_eps in ep_nums.items():
        page = r.subreddit(epi_data_sr).wiki['{}/{}/season_{}/'.format(
            epi_data_dir, sr, s_num)]
        page.edit(content=json.dumps(s_eps))

exit(0)
