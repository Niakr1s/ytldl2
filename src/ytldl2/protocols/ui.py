from typing import Protocol

from ytldl2.models.download_hooks import DownloadProgress, PostprocessorProgress
from ytldl2.models.download_result import DownloadResult
from ytldl2.models.types import VideoId


class ProgressBar(Protocol):
    def new(self, video: VideoId) -> None:
        """Called when a new video is started."""

    def close(self, video: VideoId) -> None:
        """Called when a video is finished, after all postprocessors are done."""

    def on_download_progress(self, progress: DownloadProgress) -> None:
        """Called on download progress."""

    def on_postprocessor_progress(self, progress: PostprocessorProgress) -> None:
        """Called on postprocessor progress."""


class Ui(Protocol):
    """User for music library."""

    def on_download_result(self, result: DownloadResult):
        """Called by library to display download result."""
        ...

    def progress_bar(self) -> ProgressBar:
        """
        Should return class used to track single song download progress.
        """
        ...
