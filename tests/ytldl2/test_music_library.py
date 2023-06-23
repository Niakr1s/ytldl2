import pathlib

import pytest
from ytldl2.music_library import MusicLibraryConfig, default_include_playlists


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
