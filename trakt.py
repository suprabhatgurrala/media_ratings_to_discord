import requests
import pandas as pd

import webhook_gen

TMDB_API_KEY = webhook_gen.TMDB_API_KEY
TMDB_BASE_IMG_URL = "https://www.themoviedb.org/t/p/original"


def rating_to_webhook(user_slug, entries):
    """
    Display a Trakt.tv rating using a Discord webhook

    Parameters
    ----------
    entries : list
    """
    # TODO: Message should include the number of shows/seasons/episodes that were rated
    webhook_obj = {"content": f"{user_slug} on Trakt.tv:"}
    embeds = []

    for entry in entries[0:3]:
        show_title_year = f"{entry['show']['title']} ({entry['show']['year']})"
        rating = entry['rating']

        description = f"{user_slug} rated {show_title_year} {rating}/10 on Trakt.tv"

        tmdb_id = entry["show"]["ids"]["tmdb"]

        image_url = fetch_tmdb_poster(tmdb_id)

        embeds.append({
            "title": show_title_year,
            "description": description,
            "url": f"https://trakt.tv/users/{user_slug}/ratings",
            "image": {"url": image_url},
            "fields": [{
                "name": "Rating",
                "value": f"{rating}/10"}]
        })

    webhook_obj["embeds"] = embeds

    return webhook_obj


def fetch_tmdb_poster(tmdb_id):
    """
    Get URL for poster image from TheMovieDatabase
    """
    tv_image_url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/images"

    headers = {
        'Content-Type': 'application/json',
    }

    params = {
        "api_key": TMDB_API_KEY
    }

    r2 = requests.get(tv_image_url, headers=headers, params=params)

    tmdb_images = r2.json()

    image_df = pd.DataFrame(tmdb_images["posters"])

    image_path = image_df.loc[image_df["vote_count"].idxmax()].file_path

    poster_url = f"{TMDB_BASE_IMG_URL}{image_path}"

    return poster_url
