import tmdb


def rating_to_webhook(user_slug, entries):
    """
    Display a Trakt.tv rating using a Discord webhook

    Parameters
    ----------
    entries : list
    """
    embeds = []

    num_shows = 0
    num_seasons = 0
    num_episodes = 0

    for i, entry in enumerate(entries):
        item_type = entry["type"]

        show_title = f"{entry['show']['title']}"

        fields = [
            {"name": "Show", "value": entry["show"]["title"]},
            {"name": "Year", "value": f"{entry['show']['year']}"},
        ]

        if item_type == "show":
            num_shows += 1
        elif item_type == "season":
            show_title = f"Season {entry['season']['number']} of {show_title}"
            fields.append({"name": "Season", "value": f"{entry['season']['number']}"})
            num_seasons += 1
        elif item_type == "episode":
            show_title = f"Season {entry['episode']['season']}, Ep. {entry['episode']['number']} of {show_title}"
            fields.append({"name": "Season", "value": f"{entry['episode']['season']}"})
            fields.append(
                {
                    "name": "Episode",
                    "value": f"{entry['episode']['number']} - '{entry['episode']['title']}'",
                }
            )
            num_episodes += 1

        if i > 5:
            # Don't include more than 5 embeds per webhook
            continue

        rating = entry["rating"]

        fields.append({"name": "Rating", "value": f"{rating}/10"})

        description = f"{user_slug} rated {show_title} **{rating}/10** on Trakt.tv"

        tmdb_id = entry["show"]["ids"]["tmdb"]

        image_url = tmdb.fetch_poster(tmdb_id)

        embeds.append(
            {
                "title": show_title,
                "description": description,
                # "url": f"https://trakt.tv/users/{user_slug}/ratings",
                "image": {"url": image_url},
                "fields": fields,
                "timestamp": entry["rated_at"],
            }
        )

    shows = ""
    if num_shows == 1:
        shows = "1 show"
    elif num_shows > 1:
        shows = f"{num_shows} shows"

    episodes = ""
    if num_episodes == 1:
        episodes = "1 episode"
    elif num_episodes > 1:
        episodes = f"{num_episodes} episodes"

    seasons = ""
    if num_seasons == 1:
        seasons = "1 season"
    elif num_seasons > 1:
        seasons = f"{num_seasons} seasons"

    if shows and seasons and episodes:
        item_str = f"{shows}, {seasons}, and {episodes}"
    elif shows and seasons:
        item_str = f"{shows} and {seasons}"
    elif shows and episodes:
        item_str = f"{shows} and {episodes}"
    elif seasons and episodes:
        item_str = f"{seasons} and {episodes}"
    else:
        item_str = f"{shows}{seasons}{episodes}"

    webhook_obj = {
        "content": f"{user_slug} rated {item_str} on Trakt.tv:",
        "embeds": embeds,
    }

    return webhook_obj
