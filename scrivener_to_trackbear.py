#!/usr/bin/env python3.12
"""
Automagically uploads yesterday's Scrivener progress to TrackBear.

Set this as a launchd or crontab item to run some time in the morning.

Reads from `config.toml` with the keys:

- scrivener_path: The path to the .scriv file.
- trackbear_key: Your TrackBear API key. Get it from https://trackbear.app/account/api-keys
- project_id: The TrackBear project ID. Find it in the URL, eg https://trackbear.app/projects/12345
- tags: Optionally a list of strings as tags
"""

import tomllib
from datetime import date as Date, timedelta as Timedelta

from scrivener import WritingHistory
from trackbear import TrackBearAPI


if __name__ == '__main__':
    with open('config.toml', 'rb') as f:
        CONFIG = tomllib.load(f)

    tb = TrackBearAPI(CONFIG['trackbear_key'])

    yesterday = Date.today() - Timedelta(days=1)

    wh = WritingHistory.from_scriv(CONFIG['scrivener_path']).get(yesterday)
    if wh is None:
        print("No writing history found for yesterday!")
        exit(0)

    tally = tb.create_tally(
        project=CONFIG['project_id'],
        count=wh.draft_words_total,
        date=yesterday,
        set_total=True,
        note="Automatically sent by scrivener_to_trackbear.py",
        tags=CONFIG.get('tags', []),
    )
    print("Tally sent!")
    print(tally)
