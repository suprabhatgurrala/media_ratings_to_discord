import tmdb


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

        image_url = tmdb.fetch_tmdb_poster(tmdb_id)

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
