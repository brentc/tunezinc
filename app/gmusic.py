import logging
from datetime import datetime, time
import os

import pytz
from cached_property import cached_property
from gmusicapi import Mobileclient, Musicmanager

logger = logging.getLogger(__name__)


class Gmusic(object):

    def __init__(self, playlists_to_sync, credentials_storage_location, debug):
        self.playlists_to_sync = playlists_to_sync
        self.credentials_storage_location = credentials_storage_location
        self._client = Mobileclient(debug_logging=debug)
        self._manager = Musicmanager(debug_logging=debug)


    def client_login(self):
        credentials = self.credentials_storage_location

        if not os.path.isfile(credentials):
            credentials = self._client.perform_oauth(
                storage_filepath=self.credentials_storage_location,
                open_browser=True
            )

        if not self._client.oauth_login(
            device_id=Mobileclient.FROM_MAC_ADDRESS,
            oauth_credentials=credentials,
        ):
            logger.error("Gmusic mobile client authentication failed")
            return False

        logger.info("Gmusic mobile client authentication succeeded.")
        return True

    def manager_login(self):
        credentials = self.credentials_storage_location

        if not os.path.isfile(credentials):
            credentials = self._manager.perform_oauth(
                storage_filepath=self.credentials_storage_location,
                open_browser=True
            )

        if not self._manager.login(
                oauth_credentials=credentials,
        ):
            logger.error("Gmusic music manager authentication failed")
            return False

        logger.info("Gmusic music manager authentication succeeded.")
        return True

    @property
    def client(self):
        if not self._client.is_authenticated():
            self.client_login()
        return self._client

    @property
    def manager(self):
        if not self._manager.is_authenticated():
            self.manager_login()
        return self._manager

    @cached_property
    def uploaded_songs(self):
        return {song['id']: song for song in self.manager.get_uploaded_songs()}

    @property
    def _playlists(self):
        playlists = self.client.get_all_user_playlist_contents()
        logger.debug("Loaded {} playlists".format(len(playlists)))
        return playlists

    @cached_property
    def playlists(self):
        playlists_to_sync = []
        for playlist in self._playlists:
            if playlist['name'] in self.playlists_to_sync:
                playlists_to_sync.append(playlist)
        return playlists_to_sync

    def get_latest_addition_date(self, playlist):
        lastModified = playlist.get('lastModifiedTimestamp')
        if lastModified:
            return datetime.fromtimestamp(int(lastModified) / 10 ** 6).replace(tzinfo=pytz.utc)

        return None
