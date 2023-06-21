import json

import pytest
from ytmusicapi import YTMusic

from tests.ytldl2 import DATA, OAUTH_PATH
from ytldl2 import VideoId
from ytldl2.api import Extractor, HomeItems, YtMusicApi


class TestExtractor:
    @pytest.fixture
    def extractor(self) -> Extractor:
        return Extractor()

    @pytest.fixture(scope="session")
    def home(self):
        with (DATA / "home.json").open(encoding="utf-8") as file:
            return json.load(file)

    @pytest.fixture(scope="session")
    def get_playlist(self):
        with (DATA / "get_playlist.json").open(encoding="utf-8") as file:
            return json.load(file)

    @pytest.fixture(scope="session")
    def get_watch_playlist(self):
        with (DATA / "get_watch_playlist.json").open(encoding="utf-8") as file:
            return json.load(file)

    @pytest.fixture(scope="session")
    def artist(self):
        with (DATA / "artist.json").open(encoding="utf-8") as file:
            return json.load(file)

    def test_parse_home(self, extractor: Extractor, home):
        items = extractor.parse_home(home)
        assert 3 == len(items)
        assert 1 == len(items["videos"])
        assert 2 == len(items["channels"])
        assert 3 == len(items["playlists"])

    def test_parse_home__exclude_home_titles(self, extractor: Extractor, home):
        """Here we exclude all titles of home."""
        items = extractor.parse_home(
            home, exclude_titles=["Mixed for you", "Listen again"]
        )
        for item in items.values():
            assert not item

    def test_parse_home__exclude_playlists(self, extractor: Extractor, home):
        """Here we exclude all titles of playlists."""
        items = extractor.parse_home(
            home,
            exclude_titles=[
                "My Supermix",
                "Your Likes",
                "Suzume no Tojimari Car Playlist",
            ],
        )
        assert items["videos"]
        assert items["channels"]
        assert not items["playlists"]

    def test_extract_video_ids_from_playlist__get_playlist(
        self, extractor: Extractor, get_playlist
    ):
        res = extractor.extract_video_ids_from_playlist(get_playlist)
        assert ["9amPGYrVxFA", "OHcFfF3w0Ok"] == res

    def test_extract_video_ids_from_playlist__get_watch_playlist(
        self, extractor: Extractor, get_watch_playlist
    ):
        res = extractor.extract_video_ids_from_playlist(get_watch_playlist)
        assert ["6xZWW8ZQvVs", "mrGYm1djl3A", "T_iLqam_f4E"] == res

    def test_extract_songs_browse_id_from_artist(self, extractor: Extractor, artist):
        res = extractor.extract_songs_browse_id_from_artist(artist)
        assert "VLOLAK5uy_k3MhpJYfxJH099ZbTqgGF9fpPCE_QXSVQ" == res


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
