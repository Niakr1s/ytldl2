import pathlib
from typing import Protocol

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

    def on_progress(self, progress: DownloadProgress) -> None:
        filename = pathlib.Path(progress["filename"]).name
        if is_progress_downloading(progress):
            print(
                f"Downloading: {filename}: {progress['downloaded_bytes']} of \
                    {progress['total_bytes']} bytes"
            )
        if is_progress_finished(progress):
            print(f"Finished: {filename}: {progress['total_bytes']} bytes")
        if is_progress_error(progress):
            print(f"Error: {filename}: {progress}")


class TerminalMusicLibraryUser(MusicLibraryUser):
    pass
