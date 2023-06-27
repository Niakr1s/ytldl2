from rich.progress import Progress, TaskID
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
from ytldl2.util.console import clear_last_line


class TerminalMusicDownloadTracker(MusicDownloadTracker):
    def __init__(
        self,
    ) -> None:
        self._progress = Progress(expand=True)
        self._dl: TaskID | None = None
        self._pp: dict[str, TaskID] = {}
        self._close_str = ""

    def new(self, video: VideoId) -> None:
        self._clean()
        print(f"Starting download {video}...", end="\r")

        self._progress.start()
        self._dl = self._progress.add_task(video, total=None)

    def close(self, video: VideoId) -> None:
        """Called when a video is finished, after all postprocessors are done."""
        self._clean()
        self._progress.stop()

        clear_last_line(1)
        print(self._close_str)

    def _clean(self) -> None:
        if self._dl is not None:
            self._progress.remove_task(self._dl)
            self._dl = None
        if self._pp:
            for pp in self._pp.values():
                self._progress.remove_task(pp)
            self._pp = {}

    def on_video_skipped(self, video: VideoId, reason: str) -> None:
        """Called when a video is skipped."""
        self._close_str = f"Skipped download {video}: {reason}."

    def on_video_filtered(self, video: VideoId, filtered_reason: str) -> None:
        """Called when a video is filtered."""
        self._close_str = f"Filtered download {video}: {filtered_reason}."

    def on_download_progress(
        self,
        video: VideoId,
        filename: str,
        *,
        total_bytes: int,
        downloaded_bytes: int,
    ) -> None:
        """Called on download progress."""
        self._progress.update(
            self._dl,  # type: ignore
            description=filename,
            total=total_bytes,
            completed=downloaded_bytes,
        )
        if downloaded_bytes >= total_bytes:
            self._on_download_finished(video, filename)

    def _on_download_finished(self, video: VideoId, filename: str) -> None:
        self._close_str = f"Finished download {video} as {filename}."

    def on_postprocessor_progress(self, progress: PostprocessorProgress) -> None:
        pp = progress["postprocessor"]
        if is_postprocessor_started(progress):
            self._pp[pp] = self._progress.add_task(f"\t{pp}", total=None)
        if is_postprocessor_finished(progress):
            self._progress.remove_task(self._pp[pp])
            del self._pp[pp]


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
