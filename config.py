import json
import os

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

with open(config_path, "r") as f:
    config = json.load(f)

POST_FREQUENCY_HRS = config.get("post_freq_hrs", 1)

DISCORD_WEBHOOK_URL_LETTERBOXD = config["letterboxd"].get("discord_url")
LETTERBOXD_USERNAMES = config["letterboxd"].get("usernames")

DISCORD_WEBHOOK_URL_TRAKT = config["trakt"].get("discord_url")
TRAKT_CLIENT_ID = config["trakt"].get("trakt_api_key")
TRAKT_API_URL = "https://api.trakt.tv"
TRAKT_USERNAMES = config["trakt"].get("usernames")

TMDB_API_KEY = config["trakt"].get("movie_db_api_key")

LOG_PATH = config.get("log_path")
if LOG_PATH:
    LOG_PATH = os.path.abspath(LOG_PATH)
