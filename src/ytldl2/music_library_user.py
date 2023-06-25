import pathlib
from typing import Protocol

from ytldl2.download_queue import DownloadResult
from ytldl2.models.download_hooks import (
    DownloadProgress,
    DownloadProgressDownloading,
    DownloadProgressError,
    DownloadProgressFinished,
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

    def review_songs(self, videos: list[Song]) -> list[Song]:
        """
        Called by library to ask user to review songs.
        :return: Reviewed songs, that is intended to be downloaded.
        """
        return videos

    def display_result(self, result: DownloadResult):
        """Called by library after download to display download result."""
        print("=== Download result ===")
        print()
        print(f"Requested: {len(result.videos)}.")
        print(f"\tDownloaded: {len(result.downloaded)},")
        print(f"\tSkipped: {len(result.skipped)},")
        print(f"\tFailed: {len(result.failed)},")
        print(f"\tFiltered: {len(result.filtered)}")
        print()
        print(f"Remained in queue: {len(result.queue)}")

    def on_progress(self, progress: DownloadProgress) -> None:
        filename = pathlib.Path(progress["filename"]).name
        match progress:
            case DownloadProgressDownloading():
                print(
                    f"Downloading: {filename}: {progress['downloaded_bytes']} of \
                        {progress['total_bytes_estimate']} bytes"
                )
            case DownloadProgressFinished():
                print(f"Finished: {filename}: {progress['total_bytes']} bytes")
            case DownloadProgressError():
                print(f"Error: {filename}: {progress}")


class NoLibraryUser(MusicLibraryUser):
    pass
