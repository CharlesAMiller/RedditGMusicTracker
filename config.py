import logging
import os

"""
    This file should be adjusted by the user to configure the behavior of
    the main script.

    By default, private fields are loaded from the user's
    environment variable.
"""

# Google Play Music configuration
# You can find information about App passwords here:
#   https://support.google.com/accounts/answer/185833?hl=en
email = os.environ.get("GMUSIC_EMAIL")
password = os.environ.get("GMUSIC_APP_PASS")

# Reddit script configuration
# You can find useful info here: https://github.com/reddit-archive/reddit/wiki/OAuth2
client_id = os.environ.get('REDDIT_CLIENT_ID')
client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
user_agent = os.environ.get("REDDIT_USER_AGENT")

# Reddit account configuration
reddit_username = os.environ.get("REDDIT_USER")
reddit_password = os.environ.get("REDDIT_PASS")

# This configuration handles the subreddits that should be parsed by the script,
# defines parsing behavior, and the configuration for the playlist(s).
#
# Note: Each key should be the name of a subreddit.
#       Each key should have an array as its value. This array is comprised of Dicts that contain the below:

# playlist_name (required) - The name of the Google Music playlist that should be created/overwritten.
# playlist_description - The desired description text for the playlist.
# sort_by (required) - the method by which reddit posts should be searched.
# sort_by_range - the time range that reddit posts should be searched across.
# search (list) - search terms for which posts will be compared against.
# post_artist_track_delimiter -
#   A character that will help the script determine where the name of the artist is separated from the track's name.
# post_artist_track_order - Determines whether the artist or track should appear first in the post title.
# strip_from_search_results (list) - When a post is found according to the search criteria,
#   this list determines what parts of the post title should be removed prior to performing a song search.
subreddits = {
    'hiphopheads': [
        {
            "playlist_name": "HipHopHeads Top Weekly",
            "playlist_description": "[FRESH] weekly posts from reddit.com/r/hiphopheads",
            "sort_by": "top",
            "sort_by_range": "week",
            "search": ["[FRESH]"],
            "post_artist_track_delimiter": '-',
            "post_artist_track_order": 'AT',
            "strip_from_search_results": ["[FRESH]"]
        },
        {
            "playlist_name": "HipHopHeads Top Monthly",
            "playlist_description": "[FRESH] monthly posts from reddit.com/r/hiphopheads",
            "sort_by": "top",
            "sort_by_range": "month",
            "search": ["[FRESH]"],
            "post_artist_track_delimiter": '-',
            "post_artist_track_order": 'AT',
            "strip_from_search_results": ["[FRESH]"]
        }
    ],
    'indieheads': [
        {
            "playlist_name": "IndieHeads Top Weekly",
            "playlist_description": "Top [FRESH] posts from reddit.com/r/indieheads for the week.",
            "sort_by": "top",
            "sort_by_range": "week",
            "search": ["[FRESH]"],
            "post_artist_track_order": 'AT',
            "post_artist_track_delimiter": '-',
            "strip_from_search_results": ["[FRESH]"]
        },
        {
            "playlist_name": "IndieHeads Top Monthly",
            "playlist_description": "Top [FRESH] posts from reddit.com/r/indieheads for the month.",
            "sort_by": "top",
            "sort_by_range": "month",
            "search": ["[FRESH]"],
            "post_artist_track_order": 'AT',
            "post_artist_track_delimiter": '-',
            "strip_from_search_results": ["[FRESH]"]
        },
    ]
}


"""
    YOU SHOULDN'T HAVE TO ALTER SETTINGS BELOW
"""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reddit-gmusic-tracker")

config_options = {
    'playlist_name': {"required": True},
    'playlist_description': {"required": False, "default": "Auto generated playlist by RedditGMusicTracker."},
    'sort_by': {"required": True, "default": "top", "valid_options": ['top', 'hot', 'new', 'gilded']},
    'sort_by_range': {"required": False, "default": "week"},
    'linked_sites': {"required": False, "default": ["youtube", "spotify", "google", "tidal", "soundcloud"]},
    'search': {"required": False, "default": ["[FRESH]"]}
}