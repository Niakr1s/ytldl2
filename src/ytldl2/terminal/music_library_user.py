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

    def on_download(self, filename: str, total: int, downloaded: int) -> None:
        if self._last_file != filename:
            self._on_download_start(filename, total, downloaded)
        else:
            if self._pbar is None:
                raise RuntimeError("no progress bar to update")
            self._pbar.update(downloaded - self._pbar.n)

    def close(self) -> None:
        if self._pbar is not None:
            self._pbar.close()
        self._pbar = None
        self._last_file = None


class PostprocessorProgressBar(tqdm):
    def __init__(self, name: str) -> None:
        super().__init__(leave=False, desc=name)


class TerminalMusicDownloadTracker(MusicDownloadTracker):
    def __init__(self) -> None:
        self._download_pbar = DownloadProgressBar()
        self._postprocessor_pbar: PostprocessorProgressBar | None = None
        self._current_video: VideoId | None = None
        self._end_str = ""

    def new(self, video: VideoId) -> None:
        print(f"Starting download {video}...")
        self._end_str = ""

    def close(self, video: VideoId) -> None:
        """Called when a video is finished, after all postprocessors are done."""
        self._download_pbar.close()
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
        self._download_pbar.on_download(filename, total_bytes, downloaded_bytes)
        self._end_str = f"Finished download {video}."

    def _close_postprocessor_bar(self) -> None:
        if self._postprocessor_pbar is not None:
            self._postprocessor_pbar.close()
            self._postprocessor_pbar = None

    def on_postprocessor_progress(self, progress: PostprocessorProgress) -> None:
        if is_postprocessor_started(progress):
            self._close_postprocessor_bar()
            self._postprocessor_pbar = PostprocessorProgressBar(
                progress["postprocessor"]
            )
        if is_postprocessor_finished(progress):
            self._close_postprocessor_bar()


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
