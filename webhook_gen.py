import logging
import time
from datetime import datetime, timedelta

import feedparser
import requests

import config
import letterboxd
import trakt

LOG_PATH = config.LOG_PATH
LETTERBOXD_USERNAMES = config.LETTERBOXD_USERNAMES
DISCORD_WEBHOOK_URL_LETTERBOXD = config.DISCORD_WEBHOOK_URL_LETTERBOXD
POST_FREQUENCY_HRS = config.POST_FREQUENCY_HRS

TRAKT_CLIENT_ID = config.TRAKT_CLIENT_ID
TRAKT_API_URL = config.TRAKT_API_URL
TRAKT_USERNAMES = config.TRAKT_USERNAMES


def main():
    # Setup logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(LOG_PATH, "a+")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("{asctime} - {name} - {levelname} - {message}", style="{")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # Poll Letterboxd RSS feeds

    for username in LETTERBOXD_USERNAMES:
        d = feedparser.parse(f"https://letterboxd.com/{username}/rss/")
        entries_to_post = []
        for entry in d["entries"]:
            published_time = datetime.fromtimestamp(time.mktime(entry['published_parsed']))

            if (datetime.now() - published_time) < timedelta(hours=POST_FREQUENCY_HRS):
                entries_to_post.append(entry)
        if len(entries_to_post) > 0:
            webhook_obj = letterboxd.letterboxd_to_webhook(entries_to_post)
            print(webhook_obj)
            # r = requests.post(DISCORD_WEBHOOK_URL_LETTERBOXD, json=webhook_obj)
            logger.info(f"Letterboxd posts found for {username}, webhook status: {r.status_code}: {r.reason}")

    # Poll Trakt.tv Ratings
    for user_slug in TRAKT_USERNAMES:
        headers = {
            'Content-Type': 'application/json',
            'trakt-api-version': '2',
            'trakt-api-key': TRAKT_CLIENT_ID
        }
        ratings_url = f"{TRAKT_API_URL}/users/{user_slug}/ratings/all/"

        r = requests.get(ratings_url, headers=headers)

        for entry in r.json():
            published_time = datetime.strptime(entry['rated_at'], "%Y-%m-%dT%H:%M:%S.000Z")
            if (datetime.now() - published_time) < timedelta(hours=POST_FREQUENCY_HRS):
                entries_to_post.append(entry)
        if len(entries_to_post) > 0:
            webhook_obj = trakt.rating_to_webhook(entries_to_post)
            print(webhook_obj)
            # r = requests.post(DISCORD_WEBHOOK_URL_LETTERBOXD, json=webhook_obj)
            logger.info(f"Trakt.tv posts found for {username}, webhook status: {r.status_code}: {r.reason}")

    logger.info(f"Polled {len(LETTERBOXD_USERNAMES)} Letterboxd feeds and {len(TRAKT_USERNAMES)} Trakt.tv users.")


if __name__ == "__main__":
    main()
