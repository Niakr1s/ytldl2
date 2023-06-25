import pathlib
from typing import Protocol

from tqdm import tqdm

from ytldl2.download_queue import DownloadQueue
from ytldl2.models.download_hooks import (
    DownloadProgress,
    is_progress_downloading,
    is_progress_error,
    is_progress_finished,
)
from ytldl2.models.home_items import HomeItems, HomeItemsFilter
from ytldl2.models.song import Song


class MusicLibraryUser(Protocol):
    """User for music library."""

    def review_filter(
        self,
        home_items: HomeItems,
        filter: HomeItemsFilter,
    ) -> HomeItemsFilter:
        """
        Called by library to ask user to review filter.
        :return: Reviewed filter, that is intended to be stored in library config.
        """
        ...

    def review_songs(self, songs: list[Song]) -> list[Song]:
        """
        Called by library to ask user to review songs.
        :return: Reviewed songs, that is intended to be downloaded.
        """
        ...

    def display_result(self, queue: DownloadQueue):
        """Called by library after download to display download result."""
        ...

    def on_progress(self, progress: DownloadProgress) -> None:
        ...


class TerminalMusicLibraryUser(MusicLibraryUser):
    def __init__(self) -> None:
        self._pbar: tqdm | None = None
        self._last_file: str | None = None

    def review_filter(
        self,
        home_items: HomeItems,
        filter: HomeItemsFilter,
    ) -> HomeItemsFilter:
        """
        Called by library to ask user to review filter.
        :return: Reviewed filter, that is intended to be stored in library config.
        """
        return filter

    def review_songs(self, songs: list[Song]) -> list[Song]:
        """
        Called by library to ask user to review songs.
        :return: Reviewed songs, that is intended to be downloaded.
        """
        print(f"{len(songs)} songs will be downloaded:")
        for song in songs:
            print(f"{song.artist} - {song.title}")
        print(f"Total: {len(songs)} songs.")
        print()
        return songs

    def display_result(self, queue: DownloadQueue):
        """Called by library after download to display download result."""
        self._on_finish()

        title = "====== Download result ======"

        print()
        print(title)
        print()
        print(f"Requested: {len(queue.videos)}.")
        print()
        print(f"Downloaded: {len(queue.downloaded)},")
        print(f"Skipped: {len(queue.skipped)},")
        print(f"Filtered: {len(queue.filtered)}.")
        print()
        print(f"Remained in queue: {len(queue)}.")
        print()
        print("=" * len(title))

    def on_progress(self, progress: DownloadProgress) -> None:
        filename = pathlib.Path(progress["filename"]).name

        if is_progress_downloading(progress):
            downloaded_bytes = progress["downloaded_bytes"]
            total_bytes = progress["total_bytes"]
            if self._last_file != filename:
                self._on_download_start(filename, total_bytes, downloaded_bytes)
            else:
                self._on_download(downloaded_bytes)
        if is_progress_finished(progress):
            self._on_download_finish()
            # print(f"Finished: {filename}: {progress['total_bytes']} bytes")
        if is_progress_error(progress):
            self._on_download_error()
            # print(f"Error: {filename}: {progress}")

    def _on_download_start(self, filename: str, total: int, downloaded: int) -> None:
        self._pbar = tqdm(
            total=total,
            initial=downloaded,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        )
        self._pbar.set_description(filename)
        self._last_file = filename
        # print(f"on download start: {self._last_file} ({total} bytes)")

    def _on_download(self, downloaded: int) -> None:
        if not self._pbar:
            raise RuntimeError("no progress bar to update")
        self._pbar.update(downloaded - self._pbar.n)
        # print(f"on download: {self._last_file} ({downloaded} bytes)")

    def _on_download_finish(self) -> None:
        self._on_finish()

    def _on_download_error(self) -> None:
        self._on_finish()

    def _on_finish(self) -> None:
        # print("on download finish")
        if self._pbar:
            self._pbar.close()
        self._pbar = None
        self._last_file = None
