import pathlib
from typing import Protocol, TypeGuard

from tqdm import tqdm

from ytldl2.download_queue import DownloadQueue
from ytldl2.models.download_hooks import (
    DownloadProgress,
    PostprocessorProgress,
    is_postprocessor_finished,
    is_postprocessor_started,
    is_progress_downloading,
    is_progress_error,
    is_progress_finished,
)
from ytldl2.models.home_items import HomeItems, HomeItemsFilter
from ytldl2.models.song import Song
from ytldl2.models.types import VideoId
from ytldl2.music_download_tracker import MusicDownloadTracker


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

    @property
    def music_download_tracker(self) -> MusicDownloadTracker:
        ...


class DownloadProgressBar:
    def __init__(self) -> None:
        self._pbar: tqdm | None = None
        self._last_file: str | None = None

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

    def on_download(self, filename: str, total: int, downloaded: int) -> None:
        if self._last_file != filename:
            self._on_download_start(filename, total, downloaded)
        else:
            if self._pbar is None:
                raise RuntimeError("no progress bar to update")
            self._pbar.update(downloaded - self._pbar.n)
            # print(f"on download: {self._last_file} ({downloaded} bytes)")

    def on_download_finish(self) -> None:
        self._on_finish()

    def on_download_error(self) -> None:
        self._on_finish()

    def close(self) -> None:
        self._on_finish()

    def _on_finish(self) -> None:
        # print("on download finish")
        if self._pbar is not None:
            self._pbar.close()
        self._pbar = None
        self._last_file = None


class PostprocessorProgressBar:
    def __init__(self) -> None:
        self._pbar = tqdm(leave=False)

    def on_postprocessor_start(self, name: str) -> None:
        self._set_description(name)

    def on_postprocessor_finish(self, name: str) -> None:
        self._pbar.update()

    def close(self):
        self._pbar.close()

    def _set_description(self, name: str) -> None:
        self._pbar.set_description("Postprocessor: " + name)


class TerminalMusicDownloadTracker(MusicDownloadTracker):
    def __init__(self) -> None:
        self._download_pbar = DownloadProgressBar()
        self._postprocessor_pbar: PostprocessorProgressBar | None = None
        self._current_video: VideoId | None = None
        self._end_str = ""

    def on_download_start(self, video: VideoId) -> None:
        print(f"Starting download {video}...")
        self._postprocessor_pbar = PostprocessorProgressBar()

    def on_download_finish(self, video: VideoId) -> None:
        """Called when a video is finished, after all postprocessors are done."""
        self._download_pbar.close()
        if self._is_postprocessor_bar_not_none(self._postprocessor_pbar):
            self._postprocessor_pbar.close()
        print(self._end_str)
        self._end_str = ""
        print()

    def on_video_skipped(self, video: VideoId, reason: str) -> None:
        """Called when a video is skipped."""
        self._end_str = f"Skipped download {video}: {reason}."

    def on_video_filtered(self, video: VideoId, filtered_reason: str) -> None:
        """Called when a video is filtered."""
        self._end_str = f"Filtered download {video}: {filtered_reason}."

    def on_download_progress(self, video: VideoId, progress: DownloadProgress) -> None:
        """Called on download progress."""
        filename = pathlib.Path(progress["filename"]).name

        if is_progress_downloading(progress):
            downloaded_bytes = progress["downloaded_bytes"]
            total_bytes = progress["total_bytes"]
            self._download_pbar.on_download(filename, total_bytes, downloaded_bytes)
        if is_progress_finished(progress):
            self._download_pbar.on_download_finish()
            self._end_str = f"Finished download {video}."

            # print(f"Finished: {filename}: {progress['total_bytes']} bytes")
        if is_progress_error(progress):
            self._download_pbar.on_download_error()
            self._end_str = f"Error: {filename}: {progress}"
            # print(f"Error: {filename}: {progress}")

    @staticmethod
    def _is_postprocessor_bar_not_none(
        bar: PostprocessorProgressBar | None,
    ) -> TypeGuard[PostprocessorProgressBar]:
        if bar is None:
            raise RuntimeError("no postprocessor bar")
        return True

    def on_postprocessor_progress(self, progress: PostprocessorProgress) -> None:
        if self._is_postprocessor_bar_not_none(pbar := self._postprocessor_pbar):
            if is_postprocessor_started(progress):
                pbar.on_postprocessor_start(progress["postprocessor"])
            if is_postprocessor_finished(progress):
                pbar.on_postprocessor_finish(progress["postprocessor"])


class TerminalMusicLibraryUser(MusicLibraryUser):
    def __init__(self) -> None:
        self._pbar = DownloadProgressBar()

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

    @property
    def music_download_tracker(self) -> MusicDownloadTracker:
        return TerminalMusicDownloadTracker()