import logging
import re

from .gmusic import Gmusic
from .spotify import Spotify

logger = logging.getLogger(__name__)


class Track(object):
    spotify_uri = None
    FEATURING_PATTERN = re.compile(r"""
        ^(?P<title>.*?)         # Some title
        \s+                     # Required whitespace break
        (?:[(-])?\s*            # Optional opening parens or - and more space
        feat(?:\.|uring)\s+(?P<featuring>.*?)
        (?:
            \)                  # Optional closing parens
            (?:                 # Optional following content
                \s+
                (?P<suffix>.+)?
            )?
        )?
        $
        """, re.VERBOSE | re.IGNORECASE)

    VERSION_PATTERN = re.compile(r"""
        ^(?P<title>.*?)         # Some title
        \s+                     # Required whitespace break
        \(\s*                   # Open parens and (optional) whitespace
            (?P<version>        # The word "version" somewhere inside
                [^)]*?
                version
                [^)]*?
            )
        \s*\)                   # Closing (optional) whitespace and parens
        $                       # End of title
        """, re.VERBOSE | re.IGNORECASE)

    EDITION_PATTERN = re.compile(r"""
        ^(?P<title>.*?)         # Title
        \s*                     # Required whitespace break
        [(\[]\s*                # Opening parens or bracket & whitespace
        (?P<edition>
            (?:
                Standard|Deluxe|Web-Only|Exclusive|EP|Explicit|International|Single|US|UK
                (?:\s+(?:Edition|Version))? # Optional secondary term
            )|
            (?:.*?Remix.*?)     # Remix Edition
        )
        \s*
        [)\]]                   # Closing parens or bracket
        $
    """, re.VERBOSE | re.IGNORECASE)

    def __init__(self, title=u'', artist=u'', album=u''):
        self.title = title
        self.artist = artist
        self.album = album

    @classmethod
    def from_gmusic_track_info(cls, track_info):
        return cls(**{key: track_info.get(key, '') for key in ('title', 'artist', 'album')})

    def matches_spotify_track_info(self, track_info):
        return (
            self._title_matches(track_info) and
            self._artist_matches(track_info) and
            self._album_matches(track_info)
        )

    def _artist_matches(self, track_info):
        local_artist = self._clean_term(self.artist)
        if not local_artist:
            return True

        return (local_artist.lower() in self._track_info_artist_names(track_info))

    @property
    def search_title(self):
        title = self.title

        featuring_match = self.FEATURING_PATTERN.search(title)
        if featuring_match:
            title = featuring_match.group('title')

        edition_match = self.EDITION_PATTERN.search(title)
        if edition_match:
            title = "{title} {edition}".format(**edition_match.groupdict())

        version_match = self.VERSION_PATTERN.search(title)
        if version_match:
            title = "{title} {version}".format(**version_match.groupdict())

        return title

    @property
    def search_album(self):
        album = self.album
        album_edition_match = self.EDITION_PATTERN.search(album)
        if album_edition_match:
            if re.search(r"Standard|Explicit|UK|US|International", album_edition_match.group('edition'), re.IGNORECASE):
                album = album_edition_match.group('title')
            else:
                album = "{title} {edition}".format(**album_edition_match.groupdict())

        album_version_match = self.VERSION_PATTERN.search(album)
        if album_version_match:
            if re.search(r"Single Version",
                         album_version_match.group('version'), re.IGNORECASE):
                album = album_version_match.group('title')
            else:
                album = "{title} {version}".format(**album_version_match.groupdict())

        return album

    def _clean_term(self, term):
        return term.replace("&", "and").strip().lower()

    def _album_matches(self, track_info):
        local_album = self._clean_term(self.album)
        track_info_album = self._clean_term(track_info.get('album', {}).get('name'))

        if not local_album:
            return True

        if local_album == track_info_album:
            return True

        local_album_edition_match = self.EDITION_PATTERN.search(local_album)
        track_info_album_edition_match = self.EDITION_PATTERN.search(track_info_album)

        if not local_album_edition_match and not track_info_album_edition_match:
            return False

        if local_album_edition_match:
            if "{title} - {edition}".format(
                    **local_album_edition_match.groupdict()) == track_info_album:
                return True

            if "{title} {edition}".format(
                    **local_album_edition_match.groupdict()) == track_info_album:
                return True

            if not track_info_album_edition_match:
                if local_album_edition_match.group('title') == track_info_album:
                    return True

        if track_info_album_edition_match:
            if "{title} - {edition}".format(
                    **track_info_album_edition_match.groupdict()) == local_album:
                return True

        if local_album_edition_match:
            local_album = local_album_edition_match.group('title')
        else:
            local_album = local_album

        if track_info_album_edition_match:
            track_info_album = track_info_album_edition_match.group('title')

        return local_album == track_info_album

    def _track_info_artist_names(self, track_info):
        return [self._clean_term(artist.get('name')) for artist in track_info['artists']]

    def _title_matches(self, track_info):
        track_info_title = self._clean_term(track_info['name'])
        local_title = self._clean_term(self.title)

        if local_title == track_info_title:
            return True

        featuring_match = self.FEATURING_PATTERN.search(local_title)
        if featuring_match:
            track_artist_names = u' and '.join(self._track_info_artist_names(track_info)).lower()
            for featuring_artist in re.split(r",| and ", featuring_match.group('featuring').lower()):
                featuring_artist = self._clean_term(featuring_artist)
                missing = featuring_artist and featuring_artist not in track_artist_names
                if missing:
                    break

            if missing:
                # Check for non-parens versions
                if "{title} - feat. {featuring}".format(
                        **featuring_match.groupdict()
                ) == track_info_title:
                    return True

                return False

            feature_title = featuring_match.group('title')
            feature_suffix = featuring_match.group('suffix')
            local_title = "{}{}".format(
                feature_title.strip(),
                " {}".format(feature_suffix.strip()) if feature_suffix else ''
            )

            if local_title == track_info_title:
                return True

        version_match = self.VERSION_PATTERN.search(local_title)
        if version_match:
            # Check for non-parens versions
            if "{title} - {version}".format(
                    **version_match.groupdict()
            ) == track_info_title:
                return True

            if "{title} {version}".format(
                    **version_match.groupdict()
            ) == track_info_title:
                return True

        edition_match = self.EDITION_PATTERN.search(local_title)
        if edition_match:
            # Check for non-parens versions
            if "{title} - {edition}".format(
                    **edition_match.groupdict()
            ) == track_info_title:
                return True

            if "{title} {edition}".format(
                    **edition_match.groupdict()
            ) == track_info_title:
                return True

        return False

    def __str__(self):
        return "'{}' by {} from the album {}{}".format(
            self.title,
            self.artist,
            self.album,
            " uri:{}".format(self.spotify_uri) if self.spotify_uri else "",
        )

    def __nonzero__(self):
        return bool(self.title)


class TuneZinc(object):
    SPOTIFY_PLAYLIST_NAME_FORMAT = '{name}'

    def __init__(self, config):
        self.config = config
        self.gmusic = Gmusic(
            config.GMUSIC_PLAYLISTS, 
            config.GMUSIC_CREDENTIALS_STORAGE_LOCATION,
            config.DEBUG
        )
        self.spotify = Spotify(
            config.SPOTIFY_USERNAME,
            config.SPOTIFY_CLIENT_ID,
            config.SPOTIFY_CLIENT_SECRET,
            config.SPOTIFY_CREATE_PUBLIC,
        )

    def sync(self):
        logger.info("Found {}/{} gmusic playlists to sync".format(len(self.gmusic.playlists),
                                                                   len(
                                                                       self.config.GMUSIC_PLAYLISTS)))

        for gmusic_playlist in self.gmusic.playlists:
            logger.info("Gmusic Playlist: {name} ({id})".format(**gmusic_playlist))

            spotify_playlist = self.spotify.get_or_create_playlist(
                self._format_spotify_playlist_name(gmusic_playlist['name'])
            )
            logger.info("Spotify Playlist: {name} ({id})".format(**spotify_playlist))
            self.sync_playlists(gmusic_playlist, spotify_playlist)

    def _format_spotify_playlist_name(self, name):
        return self.SPOTIFY_PLAYLIST_NAME_FORMAT.format(name=name)

    def spotify_playlist_has_track(self, playlist, track):
        items = playlist.get('items')
        if not items:
            return False

        for item in items:
            track_info = item.get('track')
            if track_info and track.matches_spotify_track_info(track_info):
                return True
        return False

    def sync_playlists(self, gmusic_playlist, spotify_playlist):
        logger.debug("Synchronizing playlist...")

        if not gmusic_playlist['tracks']:
            logger.info("No tracks found in gmusic playlist '{}'".format(gmusic_playlist['name']))
            return

        spotify_playlist_tracks = self.spotify.get_playlist_tracks(spotify_playlist['uri'])

        spotify_max_date = self.spotify.get_latest_addition_date(spotify_playlist_tracks)
        spotify_tracks_count = len(spotify_playlist_tracks.get('items', []))

        gmusic_max_date = self.gmusic.get_latest_addition_date(gmusic_playlist)
        gmusic_tracks_count = len(
            [track for track in gmusic_playlist['tracks'] if track.get('track')])

        if (spotify_max_date and gmusic_max_date and
                (spotify_max_date >= gmusic_max_date) and
                    spotify_tracks_count == gmusic_tracks_count):
            logger.info(
                "Spotify playlist last modified after gmusic & track counts match. Skipping ({}).".format(
                    gmusic_playlist['name']
                )
            )
            return

        missing_tracks = []
        for track_numner, track_value in enumerate(gmusic_playlist['tracks'], start=1):
            track = Track.from_gmusic_track_info(track_value.get('track', {}))
            if not track:
                uploaded_track = self.gmusic.uploaded_songs.get(track_value['trackId'])
                if uploaded_track:
                    track = Track.from_gmusic_track_info(uploaded_track)

            if not track:
                logger.error("Track {} from '{}' playlist has no track info associated with it!, {}".format(
                    track_numner,
                    gmusic_playlist['name'],
                    track_value
                ))
                continue

            if not self.spotify_playlist_has_track(spotify_playlist_tracks, track):
                missing_tracks.append(track)

        if not missing_tracks:
            logger.info("No missing tracks!")
            return

        logger.debug("Identified {} missing track(s)".format(len(missing_tracks)))

        found_tracks = []
        for missing_track in missing_tracks:
            track = self.spotify.find_track(missing_track)
            if track:
                found_tracks.append(track)

        logger.debug("Found {}/{} missing track(s)".format(len(found_tracks), len(missing_tracks)))

        if found_tracks:
            self.spotify.add_tracks_to_playlist(spotify_playlist, found_tracks)
            logger.info(
                "Added {}/{} missing track(s)!".format(len(found_tracks), len(missing_tracks)))
