import time

import bs4
import html2text
import pandas as pd
import requests

import tmdb


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
        # elif "letterboxd-list" in id_str:
        #     embeds.append(list_to_embed(entry))
        #     num_lists += 1

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
    soup = bs4.BeautifulSoup(list_entry["summary"], "html.parser")

    list_description_p = soup.find_all("p", recursive=False)
    list_description = ""
    list_overflow = ""
    if len(list_description_p) == 1:
        if "...plus" in list_description_p[0].text:
            list_overflow = list_description_p[0].text
        else:
            list_description = list_description_p[0].text
    elif len(list_description_p) == 2:
        list_description = list_description_p[0].text
        list_overflow = list_description_p[1].text

    if list_overflow:
        overflow = int(
            list_overflow.replace("...plus ", "").replace(
                " more. View the full list on Letterboxd.", ""
            )
        )
    else:
        overflow = 0

    ol_tags = soup.find_all("ol", recursive=False)
    ul_tags = soup.find_all("ul", recursive=False)

    fields = []

    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True

    ordered = False
    list_tags = None

    if len(ol_tags) > 0:
        list_tags = soup.ol.find_all("li")
        ordered = True

    elif len(ul_tags) > 0:
        list_tags = soup.ul.find_all("li")

    for i, item in enumerate(list_tags):
        item_description = ""
        for para in item.find_all("p"):
            item_description += para.prettify()

        item_desc_text = text_maker.handle(item_description)

        if len(item_desc_text) > 1024:
            item_desc_text = item_desc_text[0:1021] + "..."

        if len(item_desc_text.strip()) == 0:
            # value cannot be empty
            tmdb_id = get_tmdb_from_letterboxd(item.a["href"])
            item_desc_text = tmdb.fetch_director(tmdb_id)

        if ordered:
            number = f"{i + 1}. "
        else:
            number = ""

        fields.append(
            {
                "name": f"{number}{item.a.text}",
                "value": item_desc_text,
            }
        )

    if overflow > 0:
        fields.append(
            {
                "name": f"{list_overflow.replace('View the full list on Letterboxd.', '')}",
                "value": f"[View the full list on Letterboxd.]({list_entry['link']})",
            }
        )
        # Subtract 1 from overflow since we've added an extra field
        overflow -= 1

    list_description = (
        f"List of {len(fields) + overflow} movies:\n\n{list_description}".strip()
    )

    embed_entry = {
        "title": list_entry["title"],
        "description": list_description,
        "url": list_entry["link"],
        "fields": fields,
        "timestamp": pd.to_datetime(list_entry["published"])
        .tz_convert("UTC")
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    return embed_entry


def get_tmdb_from_letterboxd(letterboxd_url):
    """
    Scrape a Letterboxd movie page to get it's TMDb link
    Parameters
    ----------
    letterboxd_url: URL to a film page on Letterboxd

    Returns
    -------
    URL to the film on TheMovieDB
    """
    raw_html = requests.get(letterboxd_url).text
    parsed_html = bs4.BeautifulSoup(raw_html, "html.parser")
    tmdb_url = parsed_html.find("a", attrs={"data-track-action": "TMDB"})
    tmdb_id = tmdb_url["href"].split("/")[-2]
    return tmdb_id
