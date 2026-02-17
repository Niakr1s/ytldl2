from __future__ import annotations

import logging
from pathlib import Path

from ytmusicapi import YTMusic

from ytldl2.api import YtMusicApi
from ytldl2.cancellation_tokens import CancellationToken
from ytldl2.models import download_result
from ytldl2.models.home_items import HomeItems
from ytldl2.models.song import Song
from ytldl2.models.types import VideoId
from ytldl2.music_downloader import MusicDownloader
from ytldl2.music_library_config import MusicLibraryConfig
from ytldl2.protocols.cache import Cache, CachedVideo
from ytldl2.protocols.ui import Ui
from ytldl2.proxies import to_proxies
from ytldl2.terminal.ui import TerminalUi
from ytldl2.youtube_dl_builder import YoutubeDlBuilder

logger = logging.getLogger(__name__)


def ytmusic_build(auth, proxy: str | None) -> YTMusic:
    return YTMusic(auth=auth, proxies=to_proxies(proxy=proxy))


class MusicLibrary:
    def __init__(
        self,
        home_dir: Path,
        tmp_dir: Path,
        config: MusicLibraryConfig,
        cache: Cache,
        auth: str,
        cancellation_token: CancellationToken,
        proxy: str | None,
        ui: Ui | None = None,
    ):
        self._config = config
        self._cache = cache
        self._cancellation_token = cancellation_token
        self._ui = ui if ui else TerminalUi()

        ytm = ytmusic_build(auth, proxy)
        ytlb = YoutubeDlBuilder(home_dir=home_dir, tmp_dir=tmp_dir, proxy=proxy)
        self._downloader = MusicDownloader(ytlb=ytlb)
        self._api = YtMusicApi(ytm=ytm)

    def update(self, each_playlist_limit: int = 200):
        """
        Updates library
        """
        self._ui.library_update_started()
        home_items = self._get_home_items()

        if self._cancellation_token.kill_requested:
            self._log_cancel_requested()
            return

        self._review_home_items(home_items)
        songs = self._extract_songs(home_items, each_playlist_limit=each_playlist_limit)

        if self._cancellation_token.kill_requested:
            self._log_cancel_requested()
            return

        self.batch_download([s.video_id for s in songs])

    def _get_home_items(self) -> HomeItems:
        """Gets home items from api. Filters out cached videos."""
        logger.info("Starting to get home items")
        home_items = self._api.get_home_items()
        home_items.videos = self._cache.filter_cached(home_items.videos)
        logger.debug(f"Got home items: {home_items}")
        return home_items

    def _review_home_items(self, home_items: HomeItems) -> HomeItems:
        """Suggests user to review home items filter and filters home items with it."""
        logger.debug(
            f"Home items filter before review: {self._config.home_items_filter}"
        )
        self._ui.home_items_reviewer().review_home_items(
            home_items, self._config.home_items_filter
        )
        self._config.save()
        logger.debug(
            f"Home items filter after review: {self._config.home_items_filter}"
        )
        home_items.filter(self._config.home_items_filter.to_re())
        logger.info(f"Home items after being filtered: {home_items}")
        print(f"Home items after being filtered: {home_items}")
        return home_items

    def _extract_songs(
        self, home_items: HomeItems, each_playlist_limit: int
    ) -> list[Song]:
        """Extract songs from home items via api. Returns uncached songs list."""
        videos = set(
            self._api.get_videos(
                home_items=home_items, each_playlist_limit=each_playlist_limit
            )
        )
        logger.debug(f"Got {len(videos)} videos: {videos}")
        songs = [
            Song(video_id=v.video_id, title=v.title, artist=v.artist)
            for v in videos
            if v.artist is not None
        ]
        logger.info(f"Got {len(songs)} unfiltered songs")

        songs = self._cache.filter_cached(songs)
        logger.info(f"Got {len(songs)} filtered songs")
        return songs

    def batch_download(
        self,
        songs: list[VideoId],
    ):
        batch_download_tracker = self._ui.batch_download_tracker()
        batch_download_tracker.start(songs)

        logger.info(f"Starting batch download of {len(songs)} songs")
        downloaded = 0
        with self._downloader:
            for result in self._downloader.download(
                videos=songs,
                tracker=self._ui.progress_bar(),
            ):
                logger.info(f"Got download result: {result}")
                match result:
                    case download_result.Downloaded():
                        downloaded += 1
                        self._cache.set_info(result.info)
                        self._cache.set(
                            CachedVideo(video_id=result.video_id, filtered_reason=None)
                        )
                    case download_result.Filtered():
                        self._cache.set(
                            CachedVideo(
                                video_id=result.video_id, filtered_reason=result.reason
                            )
                        )
                    case download_result.Error():
                        # TODO: I need to fix postprocessors
                        # seems Lyrics postprocessor can't retrieve empty lyrics
                        # so I need to signal it somehow, or simply delete got file
                        pass

                batch_download_tracker.on_download_result(result)

                if self._cancellation_token.kill_requested:
                    self._log_cancel_requested()
                    break

        batch_download_tracker.end()
        logger.info(f"Batch download ended, downloaded {downloaded} songs")

    def _log_cancel_requested(self):
        logger.info("Stopping download: cancel was requested")
