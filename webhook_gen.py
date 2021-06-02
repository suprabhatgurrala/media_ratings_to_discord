import logging
import os
import time
from datetime import datetime, timedelta

import feedparser
import requests

import letterboxd
import trakt
import json

with open("config.json", 'r') as f:
    config = json.load(f)

POST_FREQUENCY_HRS = config.get('post_freq_hrs', 1)

DISCORD_WEBHOOK_URL_LETTERBOXD = config['letterboxd'].get('discord_url')
LETTERBOXD_USERNAMES = config['letterboxd'].get('usernames')

DISCORD_WEBHOOK_URL_TRAKT = config['trakt'].get('discord_url')
TRAKT_CLIENT_ID = config['trakt'].get('trakt_api_key')
TRAKT_API_URL = "https://api.trakt.tv"

TMDB_API_KEY = config['trakt'].get('movie_db_api_key')

LOG_PATH = os.path.abspath(config.get("log_path"))


def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(LOG_PATH, "a+")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("{asctime} - {name} - {levelname} - {message}", style="{")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # Handle Letterboxd

    for username in LETTERBOXD_USERNAMES:
        d = feedparser.parse(f"https://letterboxd.com/{username}/rss/")

        for entry in d["entries"]:
            published_time = datetime.fromtimestamp(time.mktime(entry['published_parsed']))
            if (datetime.now() - published_time) < timedelta(hours=POST_FREQUENCY_HRS):
                webhook_obj = letterboxd.letterboxd_to_webhook(entry) # TODO: Pass all entries together at once
                r = requests.post(DISCORD_WEBHOOK_URL_LETTERBOXD, json=webhook_obj)
                logger.info(f"Post found for {username}, webhook status: {r.status_code}: {r.reason}")
    logger.info(f"Finished running script for {len(LETTERBOXD_USERNAMES)} feeds.")


if __name__ == "__main__":
    main()
