import time

import bs4
import html2text
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
    for entry in entries:
        id_str = entry.get("id", '')

        if "letterboxd-watch" in id_str:
            embeds.append(film_to_embed(entry))
        elif "letterboxd-list" in id_str:
            embeds.append(list_to_embed(entry))

    author = entries[0]['author']
    webhook_obj = {"content": f"{author} on Letterboxd:"}
    webhook_obj["embeds"] = embeds

    return webhook_obj


def film_to_embed(entry):
    """
    Convert a film entry into an embed to be used in a webhook
    """
    if entry.get('letterboxd_rewatch') == "Yes":
        watched_verbs = "Rewatched"
    else:
        watched_verbs = "Watched"

    stars = ""
    if entry.get('letterboxd_memberrating') is not None:
        stars = entry.get('title').split("-")[-1].strip().split(" ")[0]

    soup = bs4.BeautifulSoup(entry['summary'], 'html.parser')

    date_or_review = soup.find_all('p')[-1].text

    if "Watched on" not in date_or_review:
        review = date_or_review
        if "spoiler" in review:
            review = f"|| {review} ||"
    else:
        review = ""

    date_str = ""

    if entry.get('letterboxd_watcheddate'):
        watched_date = time.strptime(entry['letterboxd_watcheddate'], "%Y-%m-%d")

        day_of_week = time.strftime('%A', watched_date)
        month = time.strftime('%B', watched_date)
        day_of_month = int(time.strftime('%d', watched_date))
        year = int(time.strftime('%Y', watched_date))

        date_str = f"{day_of_week} {month} {day_of_month}, {year}"

    image_url = soup.img["src"]

    description = f"{watched_verbs} {entry['letterboxd_filmtitle']} ({entry['letterboxd_filmyear']}) on {date_str}"

    embed_entry = {
        "title": entry['title'],
        "description": description,
        "url": entry["link"],
        "image": {"url": image_url},
    }

    fields = []

    if stars:
        fields.append({
            "name": "Rating",
            "value": stars
        })
    if review:
        fields.append({
            "name": "Review",
            "value": f"> {review}"
        })

    embed_entry["fields"] = fields
    return embed_entry


def list_to_embed(list_entry):
    """
    Convert a list entry into an embed to be used in a webhook
    """
    soup = bs4.BeautifulSoup(list_entry['summary'], 'html.parser')

    list_description_p = soup.find_all('p', recursive=False)
    list_description = ""
    list_overflow = ""
    if len(list_description_p) == 1:
        if "...plus" in list_description_p.text:
            list_overflow = list_description_p.text
        else:
            list_description = list_description_p.text
    elif len(list_description_p) == 2:
        list_description = list_description_p[0].text
        list_overflow = list_description_p[1].text

    ol_tags = soup.find_all('ol', recursive=False)
    ul_tags = soup.find_all('ul', recursive=False)

    fields = []

    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True

    ordered = False
    list_tags = None

    if len(ol_tags) > 0:
        list_tags = soup.ol.find_all('li')
        ordered = True

    elif len(ul_tags) > 0:
        list_tags = soup.ul.find_all('li')

    for i, item in enumerate(list_tags):
        item_description = ''
        for para in item.find_all('p'):
            item_description += para.prettify()

        item_desc_text = text_maker.handle(item_description)

        if len(item_desc_text) > 1024:
            item_desc_text = item_desc_text[0:1021] + "..."

        if len(item_desc_text.strip()) == 0:
            # value cannot be empty
            tmdb_id = get_tmdb_from_letterboxd(item.a['href'])
            item_desc_text = tmdb.fetch_movie_description(tmdb_id)

        if ordered:
            number = f"{i + 1}. "
        else:
            number = ""

        fields.append({
            "name": f"{number}{item.a.text}",
            "value": item_desc_text,
        })

    embed_entry = {
            "title": list_entry['title'],
            "description": list_description,
            "url": list_entry["link"],
            "fields": fields
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
    parsed_html = bs4.BeautifulSoup(raw_html)
    tmdb_url = parsed_html.find('a', attrs={'data-track-action': "TMDb"})['href']
    tmdb_id = tmdb_url.split("/")[-2]
    return tmdb_id
