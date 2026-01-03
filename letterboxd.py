import time

import bs4
import pandas as pd
from html_to_markdown import convert


def letterboxd_to_webhook(entries: list):
    """
    Display an entry of a Letterboxd RSS feed using a Discord webhook

    Parameters
    ----------
    entries: list
        list of entries from parsed RSS feed

    Returns
    -------
    JSON payload to send via Discord webhook
    """
    embeds = []
    num_lists = 0
    num_films = 0
    for entry in entries:
        id_str = entry.get("id", "")

        if "letterboxd-watch" in id_str or "letterboxd-review" in id_str:
            embeds.append(film_to_embed(entry))
            num_films += 1
        elif "letterboxd-list" in id_str:
            embeds.append(list_to_embed(entry))
            num_lists += 1

    author = entries[0]["author"]
    verb = ""

    if num_films == 1:
        movie_plural = "movie"
    else:
        movie_plural = "movies"

    if num_lists == 1:
        list_plural = "list"
    else:
        list_plural = "lists"

    if num_lists > 0 and num_films > 0:
        verb = (
            f"logged {num_films} {movie_plural} and created {num_lists} {list_plural}"
        )
    elif num_films > 0:
        verb = f"logged {num_films} {movie_plural}"
    elif num_lists > 0:
        verb = f"created {num_lists} {list_plural}"

    webhook_obj = {"content": f"{author} {verb} on Letterboxd:", "embeds": embeds}

    return webhook_obj


def film_to_embed(entry):
    """
    Convert a film entry into an embed to be used in a webhook
    """
    if entry.get("letterboxd_rewatch") == "Yes":
        watched_verbs = "Rewatched"
    else:
        watched_verbs = "Watched"

    stars = ""
    if entry.get("letterboxd_memberrating") is not None:
        stars = entry.get("title").split("-")[-1].strip().split(" ")[0]

    soup = bs4.BeautifulSoup(entry["summary"], "html.parser")

    date_or_review = soup.find_all("p")[-1].text

    if "Watched on" not in date_or_review:
        review = date_or_review
        if "spoiler" in review:
            review = f"|| {review} ||"
    else:
        review = ""

    date_str = ""

    if entry.get("letterboxd_watcheddate"):
        watched_date = time.strptime(entry["letterboxd_watcheddate"], "%Y-%m-%d")

        day_of_week = time.strftime("%A", watched_date)
        month = time.strftime("%B", watched_date)
        day_of_month = int(time.strftime("%d", watched_date))
        year = int(time.strftime("%Y", watched_date))

        date_str = f"{day_of_week} {month} {day_of_month}, {year}"

    image_url = soup.img["src"]

    description = f"{watched_verbs} {entry['letterboxd_filmtitle']} ({entry['letterboxd_filmyear']}) on {date_str}"

    embed_entry = {
        "title": entry["title"],
        "description": description,
        "url": entry["link"],
        "image": {"url": image_url},
        "timestamp": pd.to_datetime(entry["published"])
        .tz_convert("UTC")
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    fields = []

    if stars:
        fields.append({"name": "Rating", "value": stars})
    if review:
        fields.append({"name": "Review", "value": f"> {review}"})

    embed_entry["fields"] = fields
    return embed_entry


def list_to_embed(list_entry):
    """
    Convert a list entry into an embed to be used in a webhook
    """

    embed_entry = {
        "title": list_entry["title"],
        "description": convert(list_entry["description"]),
        "url": list_entry["link"],
        "timestamp": pd.to_datetime(list_entry["published"])
        .tz_convert("UTC")
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    return embed_entry
