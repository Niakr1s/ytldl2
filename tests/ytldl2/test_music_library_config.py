import pathlib

import pytest
from ytldl2.models.types import Title
from ytldl2.music_library_config import MusicLibraryConfig


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
        assert config.home_items_filter.videos == []
        assert config.home_items_filter.channels == []

        include_channels = [Title("1"), Title("2"), Title("3")]
        config.home_items_filter.channels = include_channels
        config.save()

        same_config = MusicLibraryConfig.load(config_path=config_path)
        assert config == same_config
