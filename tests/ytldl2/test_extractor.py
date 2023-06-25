import pytest
from ytldl2.extractor import Extractor
from ytldl2.models.raw_artist import RawArtist
from ytldl2.models.raw_home import Home
from ytldl2.models.raw_playlist import RawPlaylist, RawWatchPlaylist

from tests.ytldl2 import DATA


class TestExtractor:
    @pytest.fixture
    def extractor(self) -> Extractor:
        return Extractor()

    @pytest.fixture(scope="session")
    def home(self) -> Home:
        return Home.parse_raw((DATA / "home.json").read_bytes())

    @pytest.fixture(scope="session")
    def get_playlist(self) -> RawPlaylist:
        return RawPlaylist.parse_raw((DATA / "playlist.json").read_bytes())

    @pytest.fixture(scope="session")
    def get_watch_playlist(self) -> RawWatchPlaylist:
        return RawWatchPlaylist.parse_raw((DATA / "watch_playlist.json").read_bytes())

    @pytest.fixture(scope="session")
    def artist(self) -> RawArtist:
        return RawArtist.parse_raw((DATA / "artist.json").read_bytes())

    # parse_home

    def test_parse_home(self, extractor: Extractor, home):
        items = extractor.parse_home(home)
        assert items.videos
        assert items.channels
        assert items.playlists

    # extract_video_ids_from_playlist

    def test_extract_videos_from_playlist__get_playlist(
        self, extractor: Extractor, get_playlist
    ):
        videos = extractor.extract_videos_from_playlist(get_playlist)
        assert videos

    def test_extract_videos_from_playlist__get_watch_playlist(
        self, extractor: Extractor, get_watch_playlist
    ):
        videos = extractor.extract_videos_from_playlist(get_watch_playlist)
        assert videos

    # extract_playlist_id_from_artist

    def test_extract_playlist_id_from_artist(self, extractor: Extractor, artist):
        res = extractor.extract_playlist_id_from_artist(artist)
        assert "VLOLAK5uy_k3MhpJYfxJH099ZbTqgGF9fpPCE_QXSVQ" == res
