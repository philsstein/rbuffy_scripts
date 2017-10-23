#!/usr/bin/env python

import praw
from argparse import ArgumentParser

if __name__ == "__main__":
    ap = ArgumentParser()
    ap.add_argument('-s', '--subreddit', help='Read flair from this subreddit.')
    ap.add_argument('-w', '--wikisubreddit', help='Which subreddit\'s wiki to publish the list on.')
    args = ap.parse_args()

    # connect to reddit
    r = praw.Reddit(site_name='buffy_scripts', user_agent='Publish existing flair to wiki by /u/phil_s_stien')
    sub = 'buffy' if not args.subreddit else args.subreddit
    wiki_sub = 'buffytester' if not args.wikisubreddit else args.wikisubreddit

    flairs = []
    for f in r.subreddit(sub).flair(limit=None):
        # sample flair:
        # {'flair_css_class': None, 'user': Redditor(name='Adido_net'), 'flair_text': 'Ominous in yummy sushi PJs'}
        flairs.append({'user': f['user'].name, 'flair_text': f['flair_text']}) 
    
    sorted_flair = sorted(flairs, key=lambda f: f['user'])

    wiki_markup = 'Name|Flair Text\n'
    wiki_markup += ':-|:-\n'
    for f in sorted_flair:
        wiki_markup += '{}|{}\n'.format(f['user'], f['flair_text'])

    page = r.subreddit(wiki_sub).wiki['flairs/{}'.format(sub)]
    page.edit(wiki_markup)
