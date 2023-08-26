from typing import Protocol

from ytldl2.models.download_result import DownloadResult
from ytldl2.models.home_items import HomeItems, HomeItemsFilter
from ytldl2.models.song import Song
from ytldl2.protocols.music_download_tracker import MusicDownloadTracker


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

    def on_download_result(self, result: DownloadResult):
        """Called by library to display download result."""
        ...

    def music_download_tracker(self) -> MusicDownloadTracker:
        """Should return class used to track music download progress."""
        ...
