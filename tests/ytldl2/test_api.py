import pytest

from tests.ytldl2 import OAUTH_PATH
from ytldl2.api import YtMusicApi
from ytldl2.models import HomeItems


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

    @pytest.fixture()
    def home_items(self, yt_music_api: YtMusicApi) -> HomeItems:
        return yt_music_api.get_home_items(home_limit=2)

    def test_get_videos(self, yt_music_api: YtMusicApi, home_items: HomeItems):
        extracted = yt_music_api.get_videos(home_items, each_playlist_limit=1)
        assert extracted

    def test_get_home_items(self, home_items):
        assert not home_items.is_empty()
