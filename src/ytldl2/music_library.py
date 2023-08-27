from __future__ import annotations

import json
import logging
import pathlib

import pydantic

from ytldl2.api import YtMusicApi
from ytldl2.cancellation_tokens import CancellationToken
from ytldl2.models.download_result import Downloaded, Filtered
from ytldl2.models.home_items import HomeItemsFilter
from ytldl2.models.types import Title
from ytldl2.music_downloader import MusicDownloader
from ytldl2.protocols.cache import Cache, CachedVideo
from ytldl2.protocols.ui import Ui
from ytldl2.terminal.ui import TerminalUi

logger = logging.getLogger(__name__)


class MusicLibraryConfig(pydantic.BaseModel):
    @staticmethod
    def default_home_items_filter() -> HomeItemsFilter:
        my_mixes = (f"My Mix {i}" for i in range(1, 7))
        return HomeItemsFilter(
            playlists=[
                Title("Your Likes"),
                *[Title(x) for x in ["My Supermix", *my_mixes]],
            ],
            channels=[],
            videos=[],
        )

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
        config: MusicLibraryConfig,
        cache: Cache,
        downloader: MusicDownloader,
        oauth: str,
        ui: Ui | None = None,
    ):
        self._config = config
        self._cache = cache
        self._downloader = downloader
        self._api = YtMusicApi(oauth)
        self._ui = ui if ui else TerminalUi()

    def update(
        self,
        limit: int = 100,
        cancellation_token: CancellationToken = CancellationToken(),
    ):
        """
        Updates library
        """
        home_items = self._api.get_home_items()

        self._ui.home_items_reviewer().review_home_items(
            home_items, self._config.home_items_filter
        )

        home_items = home_items.filtered(self._config.home_items_filter)

        videos = self._api.get_videos(home_items=home_items)
        songs = {v.video_id for v in videos if v.artist is not None}

        songs = self._cache.filter_cached(songs)
        songs = list(songs)

        downloaded = 0
        with self._downloader:
            for result in self._downloader.download(
                videos=songs,
                tracker=self._ui.progress_bar(),
            ):
                match result:
                    case Downloaded():
                        downloaded += 1
                        self._cache.set_info(result.info)
                        self._cache.set(
                            CachedVideo(video_id=result.video_id, filtered_reason=None)
                        )
                    case Filtered():
                        self._cache.set(
                            CachedVideo(
                                video_id=result.video_id, filtered_reason=result.reason
                            )
                        )

                self._ui.on_download_result(result)

                if cancellation_token.kill_requested:
                    break

                if limit != 0 and downloaded == limit:
                    break
