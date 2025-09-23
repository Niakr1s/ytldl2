import pathlib

import pytest

from ytldl2.music_downloader import MusicDownloader
from ytldl2.music_library import (
    MusicLibrary,
)
from ytldl2.music_library_config import MusicLibraryConfig
from ytldl2.sqlite_cache import SqliteCache


class TestMusicLibrary:
    @pytest.fixture
    def library(
        self, tmp_path: pathlib.Path, auth: str, monkeypatch: pytest.MonkeyPatch
    ) -> MusicLibrary:
        home_dir = tmp_path

        config = MusicLibraryConfig(config_path=tmp_path / "config.json")
        cache = SqliteCache()

        downloader = MusicDownloader(home_dir)

        return MusicLibrary(
            config=config, cache=cache, downloader=downloader, auth=auth
        )

    def test_init(self, library: MusicLibrary):
        assert library is not None
