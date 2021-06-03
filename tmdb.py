from datetime import datetime

import requests

import config

TMDB_API_KEY = config.TMDB_API_KEY
TMDB_BASE_IMG_URL = "https://www.themoviedb.org/t/p/original"


def fetch_poster(tmdb_id):
    """
    Get URL for poster image from TheMovieDatabase
    """
    tv_image_url = f"https://api.themoviedb.org/3/tv/{tmdb_id}"

    headers = {
        'Content-Type': 'application/json',
    }

    params = {
        "api_key": TMDB_API_KEY
    }

    r2 = requests.get(tv_image_url, headers=headers, params=params)

    tmdb_info = r2.json()

    image_path = tmdb_info['poster_path']

    poster_url = f"{TMDB_BASE_IMG_URL}{image_path}"

    return poster_url


def fetch_movie_description(tmdb_id):
    movie_info_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"

    headers = {
        'Content-Type': 'application/json',
    }

    params = {
        "api_key": TMDB_API_KEY
    }

    r = requests.get(movie_info_url, headers=headers, params=params)

    tmdb_info = r.json()

    release_date = datetime.strptime(tmdb_info['release_date'], "%Y-%m-%d")

    return f"{tmdb_info['overview']}\n\nReleased on {release_date.strftime('%b %d, %Y')}"
