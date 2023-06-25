import json

import pytest
from ytldl2.extractor import ExtractError, Extractor
from ytldl2.models.channel import Channel
from ytldl2.models.playlist import Playlist
from ytldl2.models.video import Video

from tests.ytldl2 import DATA


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

    def test_extract_videos_from_playlist_throws(self, extractor: Extractor):
        with pytest.raises(ExtractError):
            extractor.extract_videos_from_playlist({})

    def test_extract_videos_from_playlist__get_playlist(
        self, extractor: Extractor, get_playlist
    ):
        videos = extractor.extract_videos_from_playlist(get_playlist)
        assert all([video.is_valid() for video in videos])
        assert ["9amPGYrVxFA", "OHcFfF3w0Ok"] == [video.videoId for video in videos]

    def test_extract_videos_from_playlist__get_watch_playlist(
        self, extractor: Extractor, get_watch_playlist
    ):
        videos = extractor.extract_videos_from_playlist(get_watch_playlist)
        assert all([video.is_valid() for video in videos])
        assert ["6xZWW8ZQvVs", "mrGYm1djl3A", "T_iLqam_f4E"] == [
            video.videoId for video in videos
        ]

    # extract_playlist_id_from_artist

    def test_extract_playlist_id_from_artist_throws(self, extractor: Extractor):
        with pytest.raises(ExtractError):
            extractor.extract_playlist_id_from_artist({})

    def test_extract_playlist_id_from_artist(self, extractor: Extractor, artist):
        res = extractor.extract_playlist_id_from_artist(artist)
        assert "VLOLAK5uy_k3MhpJYfxJH099ZbTqgGF9fpPCE_QXSVQ" == res
