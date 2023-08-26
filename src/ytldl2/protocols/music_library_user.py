from typing import Protocol

from ytldl2.models.download_result import DownloadResult
from ytldl2.protocols.music_download_tracker import MusicDownloadTracker


class MusicLibraryUser(Protocol):
    """User for music library."""

    def on_download_result(self, result: DownloadResult):
        """Called by library to display download result."""
        ...

    def music_download_tracker(self) -> MusicDownloadTracker:
        """Should return class used to track music download progress."""
        ...
