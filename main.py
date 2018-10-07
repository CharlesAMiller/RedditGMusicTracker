import praw
from gmusicapi import Mobileclient
from utils import is_match
import config
from config import logger

"""
    This script uses PRAW to parse posts from subreddits for songs.
    These songs are then searched for and added to a Google Play Music
    playlist using the gmusic api.

    Todo:
        * Actually have the script fallback to the defaults specified in config_options in config.py
        * Perform query in a separate function from the function that handles matching.
        * Change the spelling of delimiter, I guess.

    date: 10/06/2018
    username: porthog
    name: Charlie Miller
"""

# Reddit instance.
reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     password=config.reddit_password,
                     user_agent=config.user_agent,
                     username=config.reddit_username)

# Google Play Music instance.
gmusic = Mobileclient()

# Login with GM client.
logged_in = gmusic.login(config.email, config.password, Mobileclient.FROM_MAC_ADDRESS)


def validate_configuration(configured_options):
    """
        Reads user specified configurations, and determines if they've
        configured all fields that are required. Otherwise the program will
        throw an exception.

    :param configured_options:  The options that should be configured
        for a particular playlist and subreddit.
    :return:
    """
    required_options = [option for option, optionValue in config.config_options.iteritems()
                        if optionValue["required"]]

    if not all(rO in configured_options for rO in required_options):
        Exception("Required options are not configured")


def find_posts_in_subreddit(subRedditName, subRedditParseConfig):
    # type: (string, dictionary) -> List of praw.Submission
    """
        Reads submissions from the given subreddit according to the
        user configured settings.
    :param subRedditName:           A configured name of the subreddit to be searched for posts.
    :param subRedditParseConfig:    Configurable options for how posts/submissions should be parsed.
    :return:                        An array of
    """

    # Get a PRAW instance of the subreddit.
    subreddit = reddit.subreddit(subRedditName)

    # Retrieve various configured settings.
    sort_by = subRedditParseConfig["sort_by"]
    sort_by_range = subRedditParseConfig["sort_by_range"]
    search_terms = subRedditParseConfig["search"]

    # Elligible submissions found in the subreddit.
    submissions = []

    # Search submissions by our configured settings for all of our various
    # search terms.
    for searchTerm in search_terms:
        searchResults = subreddit.search(searchTerm, sort=sort_by,
                                         time_filter=sort_by_range)

        # The search term must appear in the submission's title, if it's to be parsed.
        # Right now it's strict matching. This is important for things like distinguishing
        # posts with '[FRESH]' from '[FRESH VIDEO]' in /r/hiphopheads.
        for result in searchResults:
            if searchTerm in result.title:
                submissions.append(result)

    return submissions


def match_song(artist, track):
    """
        Performs a Google Music search for the given artist and track.
        It then returns the first song search result that exceeds
        a certain threshold for fuzzy string matching on the artist and track.

    :param artist:  A string representing the name of the artist that should
                    be searched for and matched against.
    :param track:   A string representing the track name that should be searched
                    for and matched against.
    :return:    Either the Google Music store listing id for the first eligible search result.
                or None in the instance that no appropriate tracks could be found.
    """
    query = track + " " + artist

    search_results = gmusic.search(query)

    song_hits = [song_hit['track'] for song_hit in search_results['song_hits']]

    for hit in song_hits:
        if(is_match(hit['title'], track) and is_match(hit['artist'], artist)):
            return hit['storeId']

    return None

def plain_search_match(search):
    """
           Performs a Google Music search for the given plaintext query.
       :return:    Either the Google Music store listing id for the first eligible search result.
                   or None in the instance that no appropriate tracks could be found.
       """
    search_results = gmusic.search(search)

    song_hits = [song_hit['track'] for song_hit in search_results['song_hits']]

    for hit in song_hits:
        if(is_match(hit['title'], search)):
            return hit['storeId']

    return None

def create_or_update_playlist(playlist_config):
    """
        Function that either creates a new playlist, or clears the contents
        of an already existing playlist.
    :param playlist_config:     The user defined configuration for a playlist/subreddit entry.
    :return:                    The Google Music id for the created or matching playlist.
    """

    playlist_id = None

    # Check to see if the playlist exists.
    all_content = gmusic.get_all_user_playlist_contents()
    playlist = [x for x in all_content if x["name"] == playlist_config["playlist_name"]]

    # If it does, we'll remove the entries from it.
    if len(playlist) > 0:
        playlist = playlist[0]
        playlist_id = playlist["id"]
        entry_ids = [x["id"] for x in playlist["tracks"]]
        removed_entries = gmusic.remove_entries_from_playlist(entry_ids=entry_ids)
    else:
        # Otherwise, create the playlist if it couldn't be found.
        playlist_id = gmusic.create_playlist(playlist_config["playlist_name"],
                               playlist_config["playlist_description"],
                               True)
        logger.info("Playlist created " + playlist_id)

    return playlist_id


def find_songs_from_submissions(reddit_submissions, subreddit_config):
    """
        This function attempts to delineate the artist and track
        name from a reddit submission. It then does a search on Google Music
        to determine likely related songs.

    :param reddit_submissions:      An array of Submission objects.
    :param subreddit_config:                  The
    :return:                        A collection of Google Music track objects.
    """

    # Google Music song listings.
    songs = []

    # Configured settings.
    delimeter = subreddit_config["post_artist_track_delimeter"]
    track_artist_order = subreddit_config["post_artist_track_order"]
    stripTerms = subreddit_config["strip_from_search_results"]

    # An array of tuples in (Artist, Track Name) format
    artist_tracks = []

    # An array of plain text searches to be performed.
    plain_search = []

    # A list of search queries that returned no matching songs.
    no_matches = []

    # Parse submissions and split the text according to the configured delimiting character.
    for submission in reddit_submissions:
        title = submission.title
        for term in stripTerms:
            title = title.replace(term, "")

        split_title = title.split(delimeter)

        artist_track = ()

        # "TA" informs us that the order of the delimited text is Track then Artist.
        # Any other option defaults to Artist then Track.
        # TODO Add a valid_options field in the config
        if len(split_title) > 1:
            if track_artist_order == "TA":
                artist_track = (split_title[1].strip(), split_title[0].strip())
            else:
                artist_track = (split_title[0].strip(), split_title[1].strip())

            artist_tracks.append(artist_track)
        else:
            # If the delimiter couldn't be found, add the
            plain_search.append(title)

    # Search for potential matching songs.
    for artist, track in artist_tracks:
        match = match_song(artist, track)
        if match is None:
            no_matches.append((track, artist))
        else:
            if match not in songs:
                songs.append(match)

    # Try to find matches for the listings we couldn't delineate
    # an artist/track pair from.
    for search in plain_search:
        match = plain_search_match(search)
        if match is None:
            no_matches.append((search, search))
        else:
            if match not in songs:
                songs.append(match)

    return songs, no_matches


if logged_in:

    logger.info("Logged in")

    for subReddit, subRedditConfig in config.subreddits.iteritems():

        logger.info("Generating songs for " + subReddit)

        validate_configuration(subRedditConfig)
        posts = find_posts_in_subreddit(subReddit, subRedditConfig)
        songs, no_matches = find_songs_from_submissions(posts, subRedditConfig)
        playlist_id = create_or_update_playlist(subRedditConfig)

        logger.info("Number of songs matched: {}".format(len(songs)))
        logger.info("No matches for: {}".format(no_matches))

        gmusic.add_songs_to_playlist(playlist_id, songs)
