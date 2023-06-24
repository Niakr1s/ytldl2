import pathlib

import pytest
from ytldl2.models import (
    BrowseId,
    Channel,
    HomeItems,
    Playlist,
    PlaylistId,
    Title,
    Video,
    VideoId,
)
from ytldl2.music_library import (
    MusicLibrary,
    MusicLibraryConfig,
    default_include_playlists,
)


class TestMusicLibraryConfig:
    @pytest.fixture
    def config_path(self, tmp_path: pathlib.Path) -> pathlib.Path:
        return tmp_path / "config.json"

    def test_save_load(self, config_path: pathlib.Path):
        config = MusicLibraryConfig.load(config_path=config_path)
        assert config.config_path == config_path
        assert config.include_playlists == default_include_playlists()
        assert config.include_channels is not None

        include_channels = [Title("1"), Title("2"), Title("3")]
        config.include_channels = include_channels
        config.save()

        same_config = MusicLibraryConfig.load(config_path=config_path)
        assert config == same_config


class TestMusicLibrary:
    @pytest.fixture
    def library(
        self, tmp_path: pathlib.Path, oauth: str, monkeypatch: pytest.MonkeyPatch
    ) -> MusicLibrary:
        monkeypatch.setattr("ytldl2.music_library.get_oauth", lambda *_: oauth)
        return MusicLibrary(tmp_path / "library", skip_download=True)

    def test_init(self, library: MusicLibrary):
        assert library.home_dir.exists()
        assert library.dot_dir.exists()
        assert (config_path := library.config.config_path).exists()
        assert config_path.read_text()

    VIDEO_TITLES = ["video1", "video2"]
    PLAYLIST_TITLES = ["playlist1", "playlist2"]
    CHANNEL_TITLES = ["channel1", "channel2"]

    @pytest.fixture
    def home_items(self) -> HomeItems:
        return HomeItems(
            videos=[
                Video(videoId=VideoId(str(id)), title=Title(title))
                for id, title in enumerate(self.VIDEO_TITLES)
            ],
            playlists=[
                Playlist(playlistId=PlaylistId(str(id)), title=Title(title))
                for id, title in enumerate(self.PLAYLIST_TITLES)
            ],
            channels=[
                Channel(browseId=BrowseId(str(id)), title=Title(title))
                for id, title in enumerate(self.CHANNEL_TITLES)
            ],
        )

    def test_filter_home_items__empty(self, home_items: HomeItems):
        assert MusicLibrary.filter_home_items(home_items).is_empty()

    def test_filter_home_items__unknown_titles(self, home_items: HomeItems):
        home_items = MusicLibrary.filter_home_items(
            home_items,
            incl_videos=[Title("another video")],
            incl_playlists=[Title("unknown playlist")],
            incl_channels=[Title("unknown channel")],
        )
        assert not home_items.videos
        assert not home_items.playlists
        assert not home_items.channels

    def test_filter_home_items__videos(self, home_items: HomeItems):
        incl = Title(self.VIDEO_TITLES[0])
        filtered = MusicLibrary.filter_home_items(home_items, incl_videos=[incl])
        assert len(filtered.videos) == 1
        assert len(filtered.playlists) == 0
        assert len(filtered.channels) == 0
        assert incl == filtered.videos[0].title

    def test_filter_home_items__playlists(self, home_items: HomeItems):
        incl = Title(self.PLAYLIST_TITLES[0])
        filtered = MusicLibrary.filter_home_items(home_items, incl_playlists=[incl])
        assert len(filtered.videos) == 0
        assert len(filtered.playlists) == 1
        assert len(filtered.channels) == 0
        assert incl == filtered.playlists[0].title

    def test_filter_home_items__channels(self, home_items: HomeItems):
        incl = Title(self.CHANNEL_TITLES[0])
        filtered = MusicLibrary.filter_home_items(home_items, incl_channels=[incl])
        assert len(filtered.videos) == 0
        assert len(filtered.playlists) == 0
        assert len(filtered.channels) == 1
        assert incl == filtered.channels[0].title
