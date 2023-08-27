from typing import Protocol

from ytldl2.models.download_result import DownloadResult
from ytldl2.protocols.ui.progress_bar import ProgressBar


class User(Protocol):
    """User for music library."""

    def on_download_result(self, result: DownloadResult):
        """Called by library to display download result."""
        ...

    def progress_bar(self) -> ProgressBar:
        """
        Should return class used to track single song download progress.
        """
        ...
