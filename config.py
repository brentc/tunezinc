import os
import logging
import re
from logging import config as logging_config

BASE_PATH = os.path.realpath(os.path.dirname(__file__))

DEBUG = os.environ.get('TUNEZINC_DEBUG', False)
GMUSIC_USERNAME = os.environ.get('GMUSIC_USERNAME', '')
GMUSIC_PASSWORD = os.environ.get('GMUSIC_PASSWORD', '')
GMUSIC_PLAYLISTS = re.split('\s*;\s*', os.environ.get('GMUSIC_PLAYLISTS', '').strip())  # TODO: Need a better way to manage this

GMUSIC_CREDENTIALS_STORAGE_LOCATION = os.path.join(BASE_PATH, '.gmusic.credentials')

SPOTIFY_USERNAME = os.environ.get('SPOTIFY_USERNAME', '')
SPOTIFY_CREATE_PUBLIC = os.environ.get('SPOTIFY_CREATE_PUBLIC', False)
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID', '')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET', '')

log_output_level = logging.DEBUG if DEBUG else logging.INFO

logging_config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': log_output_level
        }
    },
    'loggers': {
        'app': {
            'handlers': ['console'],
            'level': log_output_level
        },
        'gmusicapi': {
            'handlers': ['console'] if DEBUG else [],
            'level': log_output_level
        }
    }
})
