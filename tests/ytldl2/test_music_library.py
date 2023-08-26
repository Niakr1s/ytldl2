import pathlib

import pytest
from ytldl2.models.types import (
    Title,
)
from ytldl2.music_downloader import MusicDownloader
from ytldl2.music_library import (
    MusicLibrary,
    MusicLibraryConfig,
)
from ytldl2.sqlite_cache import SqliteCache


class TestMusicLibraryConfig:
    @pytest.fixture
    def config_path(self, tmp_path: pathlib.Path) -> pathlib.Path:
        return tmp_path / "config.json"

    def test_save_load(self, config_path: pathlib.Path):
        config = MusicLibraryConfig.load(config_path=config_path)
        assert config.config_path == config_path
        assert (
            isinstance(pf := config.home_items_filter.playlists, list) and len(pf) > 0
        )
        assert config.home_items_filter.videos == "retain_all"
        assert config.home_items_filter.channels == "retain_all"

        include_channels = [Title("1"), Title("2"), Title("3")]
        config.home_items_filter.channels = include_channels
        config.save()

        same_config = MusicLibraryConfig.load(config_path=config_path)
        assert config == same_config


class TestMusicLibrary:
    @pytest.fixture
    def library(
        self, tmp_path: pathlib.Path, oauth: str, monkeypatch: pytest.MonkeyPatch
    ) -> MusicLibrary:
        home_dir = tmp_path

        config = MusicLibraryConfig(config_path=tmp_path / "config.json")
        cache = SqliteCache()

        downloader = MusicDownloader(home_dir)

        return MusicLibrary(
            config=config, cache=cache, downloader=downloader, oauth=oauth
        )

    def test_init(self, library: MusicLibrary):
        assert library is not None
