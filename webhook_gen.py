import json
import logging
from datetime import datetime, timedelta, timezone

import feedparser
import pandas as pd
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
DISCORD_WEBHOOK_URL_TRAKT = config.DISCORD_WEBHOOK_URL_TRAKT

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_PATH, "a+")
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("{asctime} - {name} - {levelname} - {message}", style="{")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def main():
    # Poll Letterboxd RSS feeds

    for username in LETTERBOXD_USERNAMES:
        d = feedparser.parse(f"https://letterboxd.com/{username}/rss/")
        entries_to_post = []
        for entry in d["entries"]:
            published_time = pd.to_datetime(entry["published"]).to_pydatetime()

            if (datetime.now(tz=timezone.utc) - published_time) < timedelta(
                hours=POST_FREQUENCY_HRS
            ):
                entries_to_post.append(entry)
        if len(entries_to_post) > 0:
            webhook_obj = letterboxd.letterboxd_to_webhook(entries_to_post)
            logger.debug(f"Webhook payload: {json.dumps(webhook_obj, indent=4)}")
            r = requests.post(DISCORD_WEBHOOK_URL_LETTERBOXD, json=webhook_obj)
            logger.info(
                f"Letterboxd posts found for {username}, webhook status: {r.status_code}: {r.reason}"
            )

    # Poll Trakt.tv Ratings
    for user_slug in TRAKT_USERNAMES:
        entries_to_post = []
        headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": TRAKT_CLIENT_ID,
        }
        ratings_url = f"{TRAKT_API_URL}/users/{user_slug}/ratings/all/"

        r = requests.get(ratings_url, headers=headers)

        for entry in r.json():
            published_time = pd.to_datetime(entry["rated_at"]).to_pydatetime()
            if (datetime.now(tz=timezone.utc) - published_time) < timedelta(
                hours=POST_FREQUENCY_HRS
            ):
                entries_to_post.append(entry)
        if len(entries_to_post) > 0:
            webhook_obj = trakt.rating_to_webhook(user_slug, entries_to_post)
            logger.debug(f"Webhook payload: {json.dumps(webhook_obj, indent=4)}")
            r = requests.post(DISCORD_WEBHOOK_URL_TRAKT, json=webhook_obj)
            logger.info(
                f"Trakt.tv posts found for {user_slug}, webhook status: {r.status_code}: {r.reason}"
            )

    logger.info(
        f"Polled {len(LETTERBOXD_USERNAMES)} Letterboxd feeds and {len(TRAKT_USERNAMES)} Trakt.tv users."
    )


if __name__ == "__main__":
    try:
        main()
    except:
        logger.exception("Exception while running main()")
        raise
