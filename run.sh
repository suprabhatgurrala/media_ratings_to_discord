cd /home/campbell/devtree/media_ratings_to_discord
uv run webhook_gen.py 2>&1 | systemd-cat -t media_ratings_to_discord
