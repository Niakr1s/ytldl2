import json

import pytest

from tests.ytldl2 import DATA
from ytldl2.extractor import ExtractError, Extractor
from ytldl2.models import Channel, Playlist, Video


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

    # parse_home

    def test_parse_home_throws(self, extractor: Extractor):
        with pytest.raises(ExtractError):
            extractor.parse_home([{"contents": "wrong"}])

    def test_parse_home(self, extractor: Extractor, home):
        items = extractor.parse_home(home)
        assert 1 == len(items.videos)
        assert 2 == len(items.channels)
        assert 3 == len(items.playlists)

        assert all((isinstance(video, Video) for video in items.videos))
        assert all((isinstance(channel, Channel) for channel in items.channels))
        assert all((isinstance(playlist, Playlist) for playlist in items.playlists))

        assert all((video.is_valid() for video in items.videos))
        assert all((channel.is_valid() for channel in items.channels))
        assert all((playlist.is_valid() for playlist in items.playlists))

    # extract_video_ids_from_playlist

    def test_extract_video_ids_from_playlist_throws(self, extractor: Extractor):
        with pytest.raises(ExtractError):
            extractor.extract_video_ids_from_playlist({})

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

    # extract_songs_browse_id_from_artist

    def test_extract_songs_browse_id_from_artist_throws(self, extractor: Extractor):
        with pytest.raises(ExtractError):
            extractor.extract_songs_browse_id_from_artist({})

    def test_extract_songs_browse_id_from_artist(self, extractor: Extractor, artist):
        res = extractor.extract_songs_browse_id_from_artist(artist)
        assert "VLOLAK5uy_k3MhpJYfxJH099ZbTqgGF9fpPCE_QXSVQ" == res
