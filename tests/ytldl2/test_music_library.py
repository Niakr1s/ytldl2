import pathlib

import pytest
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

        include_channels = ["1", "2", "3"]
        config.include_channels = include_channels
        config.save()

        same_config = MusicLibraryConfig.load(config_path=config_path)
        assert config == same_config


class TestMusicLibrary:
    @pytest.fixture
    def library(self, tmp_path: pathlib.Path) -> MusicLibrary:
        return MusicLibrary(tmp_path / "library", skip_download=True)

    def test_init(self, library: MusicLibrary):
        assert library.home_dir.exists()
        assert library.dot_dir.exists()
        assert (config_path := library.config.config_path).exists()
        assert config_path.read_text()
