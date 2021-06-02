import bs4
import time


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
    author = ''
    embeds = []
    for entry in entries:
        author = entry['author']

        link = entry.get('links', [{'href': ''}])[0]['href']

        if "/film/" in link:
            embeds.append(film_to_embed(entry))
        elif "/list/" in link:
            embeds.append(list_to_embed(entry))

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


def list_to_embed(entry):
    """
    Convert a list entry into an embed to be used in a webhook
    """
    pass
