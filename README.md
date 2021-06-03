# Media Ratings to Discord
Use Python to post your Letterboxd and Trakt.tv ratings/activity to your Discord server via webhooks.

## Setup
Install the Python dependencies listed in `requirements.txt`

Input your config options in `config.json`.

## Data
- Letterboxd data is pulled from RSS feeds available for each user
- Trakt.tv data is pulled using their API
- TMDb data is pulled using their API for supplemental information

## Running
The entrypoint script is `webhook_gen.py`:
```bash
python webhook_gen.py
```
The script will poll the various services and determine if there were recent posts, and post a message via webhook if so.
The length of time to be considered recent can be set using `POST_FREQUENCY_HRS ` in `config.json`.

Running the script at regular intervals using `cron` or other schedulers can monitor your posts and automatically send them to Discord

## Future Updates
- Handle more Trakt.tv activity such as marking as watched or lists
- Add more services (video games?)
