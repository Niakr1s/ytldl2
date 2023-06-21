from ytmusicapi import setup_oauth

from tests.ytldl2 import OAUTH_PATH

setup_oauth(str(OAUTH_PATH), open_browser=True)
