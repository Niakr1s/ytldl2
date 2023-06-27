from typing import Protocol

from tqdm import tqdm
from ytldl2.download_queue import DownloadQueue
from ytldl2.models.download_hooks import (
    PostprocessorProgress,
    is_postprocessor_finished,
    is_postprocessor_started,
)
from ytldl2.models.home_items import HomeItems, HomeItemsFilter
from ytldl2.models.song import Song
from ytldl2.models.types import VideoId
from ytldl2.protocols.music_download_tracker import MusicDownloadTracker
from ytldl2.protocols.music_library_user import MusicLibraryUser


class DownlodProgressBar(Protocol):
    def update(self, filename: str, total: int, downloaded: int) -> None:
        ...


class TqdmDownloadProgressBar(DownlodProgressBar):
    def __init__(self) -> None:
        self._pbars: dict[str, tqdm] = {}

    def update(self, filename: str, total: int, downloaded: int) -> None:
        if filename not in self._pbars:
            self._start(filename, total)
        self._pbars[filename].update(downloaded - self._pbars[filename].n)
        if total == downloaded:
            self._close(filename)

    def _start(self, filename: str, total: int) -> None:
        self._pbars[filename] = tqdm(
            total=total,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        )
        self._pbars[filename].set_description(filename)
        self._last_file = filename

    def _close(self, filename: str) -> None:
        self._pbars[filename].close()
        del self._pbars[filename]


class PostprocessorProgressBar(Protocol):
    def start(self, name: str) -> None:
        ...

    def close(self, name: str) -> None:
        ...


class TqdmPostprocessorProgressBar(PostprocessorProgressBar):
    def __init__(self) -> None:
        self._bars = {}

    def start(self, name: str) -> None:
        self._bars[name] = tqdm(leave=False, desc=name)

    def close(self, name: str) -> None:
        self._bars[name].close()
        del self._bars[name]


class TerminalMusicDownloadTracker(MusicDownloadTracker):
    def __init__(
        self,
        download_pbar: DownlodProgressBar | None = None,
        pp_pbar: PostprocessorProgressBar | None = None,
    ) -> None:
        self._download_pbar = (
            download_pbar if download_pbar is not None else TqdmDownloadProgressBar()
        )
        self._pp_pbar = (
            pp_pbar if pp_pbar is not None else TqdmPostprocessorProgressBar()
        )
        self._current_video: VideoId | None = None
        self._end_str = ""

    def new(self, video: VideoId) -> None:
        print(f"Starting download {video}...")
        self._end_str = ""

    def close(self, video: VideoId) -> None:
        """Called when a video is finished, after all postprocessors are done."""
        print(self._end_str + "\n")
        self._current_video = None
        self._end_str = ""

    def on_video_skipped(self, video: VideoId, reason: str) -> None:
        """Called when a video is skipped."""
        self._end_str = f"Skipped download {video}: {reason}."

    def on_video_filtered(self, video: VideoId, filtered_reason: str) -> None:
        """Called when a video is filtered."""
        self._end_str = f"Filtered download {video}: {filtered_reason}."

    def on_download_progress(
        self,
        video: VideoId,
        filename: str,
        *,
        total_bytes: int,
        downloaded_bytes: int,
    ) -> None:
        """Called on download progress."""
        self._download_pbar.update(filename, total_bytes, downloaded_bytes)
        self._end_str = f"Finished download {video}."

    def on_postprocessor_progress(self, progress: PostprocessorProgress) -> None:
        if is_postprocessor_started(progress):
            self._pp_pbar.start(progress["postprocessor"])
        if is_postprocessor_finished(progress):
            self._pp_pbar.close(progress["postprocessor"])


class TerminalMusicLibraryUser(MusicLibraryUser):
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
