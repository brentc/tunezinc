import logging
import urllib
from datetime import datetime

import dateutil
import spotipy
from spotipy import util as spotipy_util

logger = logging.getLogger(__name__)


class Spotify(object):
    _client = None
    _playlists = None
    SCOPES = ' '.join([
        'playlist-read-private',
        'playlist-modify-public',
        'playlist-modify-private',
        'user-read-private'
    ])

    def __init__(self, username, client_id, client_secret, create_public=False):
        self.username = username
        self.client_id = client_id
        self.client_secret = client_secret
        self.create_public = create_public

    def _get_auth(self):
        return spotipy_util.prompt_for_user_token(
            username=self.username,
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri='http://example.com/tunezinc/',
            scope=self.SCOPES,
        )

    @property
    def client(self):
        if not self._client:
            self._client = spotipy.Spotify(auth=self._get_auth())
        return self._client

    def search(self, q, market=None, limit=10, offset=0, type='track'):
        """
        Spotipy 2.0 doesn't support the market parameter for search results, but
        we can add it ourselves
        """
        if not market:
            return self.client.search(q, limit, offset, type)

        return self.client._get('search', q=q, market=market, limit=limit, offset=offset, type=type)

    def _fetch_playlists(self):
        playlists = {}
        for playlist in self.client.user_playlists(self.username)['items']:
            if playlist['owner']['id'] != self.username:
                logger.debug(u"Skipping playlist owned by a different user, {} ".format(playlist['name']))
                continue

            name = playlist['name']
            if playlists.get(name):
                raise Exception("Duplicate playlist named '{}' found.".format(playlist['name']))
            playlists[name] = playlist

        logger.debug(u"Loaded {} playlists".format(len(playlists)))
        return playlists

    @property
    def playlists(self):
        if not self._playlists:
            self._playlists = self._fetch_playlists()
        return self._playlists

    def _create_playlist(self, name):
        playlist = self.client.user_playlist_create(self.username, name)
        logger.info(u"Playlist named '{}' created.".format(name))
        self._playlists[name] = playlist
        return playlist

    def get_playlist(self, name):
        return self.playlists[name]

    def get_playlist_tracks(self, playlist_uri):
        return self.client.user_playlist_tracks(self.username, playlist_uri)

    def get_latest_addition_date(self, playlist_tracks):
        max_added_at = None
        items = playlist_tracks.get('items')
        if not items:
            return None

        for item in items:
            added_at = item.get('added_at')
            if not added_at:
                continue
            if max_added_at < added_at:
                max_added_at = added_at

        if max_added_at:
            return dateutil.parser.parse(max_added_at)
        return None

    def get_or_create_playlist(self, name):
        try:
            return self.get_playlist(name)
        except KeyError:
            logger.info(u"Playlist named '{}' doesn't exist".format(name))
            return self._create_playlist(name)

    def find_track(self, track):
        logger.debug(u"Searching for spotify track matching: {}".format(track))
        parts = [
            u'track:"{}"'.format(track.search_title),
            u'artist:"{}"'.format(track.artist),
            u'album:"{}"'.format(track.search_album),
        ]

        results = self.search(
            q=u' '.join(parts),
            type='track',
            market='from_token'
        )

        items = results.get('tracks', {}).get('items')
        if not items:
            logger.info(u"No match found for {}".format(track))
            return None

        for track_info in items:
            if track.matches_spotify_track_info(track_info):
                track.spotify_uri = track_info.get('uri')
                logger.debug(u"Match found: {}, {}".format(track, track_info))
                return track

    def add_tracks_to_playlist(self, playlist, tracks):
        if not tracks:
            return 0

        result = self.client.user_playlist_add_tracks(
            self.username,
            playlist['uri'],
            [track.spotify_uri for track in tracks],
        )
