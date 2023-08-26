from __future__ import annotations

import json
import logging
import pathlib
import random
import tempfile

import pydantic

from ytldl2.api import YtMusicApi
from ytldl2.cancellation_tokens import CancellationToken
from ytldl2.models.home_items import HomeItemsFilter
from ytldl2.models.song import Song
from ytldl2.models.types import Title
from ytldl2.music_downloader import MusicDownloader, YoutubeDlParams
from ytldl2.oauth import _get_oauth, _get_oauth_crypto
from ytldl2.protocols.cache import Cache
from ytldl2.protocols.music_library_user import MusicLibraryUser
from ytldl2.sqlite_cache import SqliteCache
from ytldl2.terminal.music_library_user import TerminalMusicLibraryUser
from ytldl2.util.fs import init_dirs

logger = logging.getLogger(__name__)


class MusicLibraryConfig(pydantic.BaseModel):
    @staticmethod
    def default_home_items_filter() -> HomeItemsFilter:
        my_mixes = (f"My Mix {i}" for i in range(1, 7))
        return HomeItemsFilter(playlists=[Title(x) for x in ["My Supermix", *my_mixes]])

    config_path: pathlib.Path
    home_items_filter: HomeItemsFilter = pydantic.Field(
        default_factory=default_home_items_filter
    )

    def save(self):
        """Saves config to config_path."""
        with self.config_path.open("w", encoding="utf-8") as file:
            file.write(self.model_dump_json(exclude={"config_path"}, indent=4))

    @staticmethod
    def load(config_path: pathlib.Path) -> MusicLibraryConfig:
        try:
            jsn = json.loads(config_path.read_bytes())
            return MusicLibraryConfig(config_path=config_path, **jsn)
        except FileNotFoundError:
            logger.debug(f"file {config_path} not found, creating new config")
            config = MusicLibraryConfig(config_path=config_path)
            config.save()
            logger.debug(f"created new config at {config_path}")
            return config


class MusicLibrary:
    def __init__(
        self,
        home_dir: pathlib.Path,
        password: str | None = None,
        user: MusicLibraryUser | None = None,
    ):
        self._user = user if user else TerminalMusicLibraryUser()
        self._home_dir = home_dir
        self._dot_dir = home_dir / ".ytldl2"
        self._db_path = self._dot_dir / "cache.db"
        init_dirs([self._home_dir, self._dot_dir])

        self._config = MusicLibraryConfig.load(self._dot_dir / "config.json")
        self._cache = SqliteCache(self._db_path)
        self._downloader = self._init_downloader(home_dir=home_dir, cache=self._cache)

        self.oauth_path = self._dot_dir / "oauth"
        oauth = (
            _get_oauth(self.oauth_path)
            if password is None
            else _get_oauth_crypto(
                self.oauth_path, self._dot_dir / "salt", password.encode()
            )
        )
        self._api = YtMusicApi(oauth)

    @staticmethod
    def _init_downloader(
        home_dir: pathlib.Path,
        cache: Cache,
    ) -> MusicDownloader:
        tmp_dir = pathlib.Path(tempfile.mkdtemp(suffix=".ytldl2_"))
        ydl_params = YoutubeDlParams(
            home_dir=home_dir,
            tmp_dir=tmp_dir,
        )

        return MusicDownloader(cache=cache, ydl_params=ydl_params)

    def update(
        self,
        limit: int = 100,
        cancellation_token: CancellationToken = CancellationToken(),
        skip_download: bool = False,
    ):
        """
        Updates library
        """
        home_items = self._api.get_home_items()

        self._config.home_items_filter = self._user.review_filter(
            home_items, self._config.home_items_filter
        )
        self._config.save()
        home_items = home_items.filtered(self._config.home_items_filter)

        videos = self._api.get_videos(home_items=home_items)
        songs = [
            Song(v.video_id, v.title, v.artist) for v in videos if v.artist is not None
        ]

        songs = self._cache.filter_cached(songs)
        songs = self._user.review_songs(songs)
        random.shuffle(songs)

        result = self._downloader.download(
            videos=[v.video_id for v in songs],
            limit=limit,
            cancellation_token=cancellation_token,
            skip_download=skip_download,
            tracker=self._user.music_download_tracker(),
        )
        self._user.display_result(result)

    def _clean_home_dir(self):
        """Cleans home directory: removes *.part files."""
        for path in self._home_dir.glob("*.part"):
            try:
                path.unlink()
            except Exception:
                pass

    def __enter__(self):
        self._clean_home_dir()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._clean_home_dir()
        return False
