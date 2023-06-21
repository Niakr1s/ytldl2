import pytest

from tests.ytldl2 import OAUTH_PATH
from ytldl2.api import YtMusicApi


class TestYtMusicApi:
    __test__ = False  # it tooks very much time, so i disabled it for a while

    @pytest.fixture(scope="session")
    def oauth(self) -> str:
        if OAUTH_PATH.exists():
            return OAUTH_PATH.read_text()
        raise FileNotFoundError(
            f"oauth path {OAUTH_PATH} not found, please run command 'python -m tests.ytldl2' to init it"
        )

    @pytest.fixture()
    def yt_music_api(self, oauth) -> YtMusicApi:
        return YtMusicApi(oauth=oauth)

    def test_get_songs(self, yt_music_api: YtMusicApi):
        extracted = yt_music_api.get_songs(home_limit=2, each_playlist_limit=1)
        assert extracted
