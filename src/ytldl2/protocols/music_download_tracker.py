from typing import Protocol

from ytldl2.models.download_hooks import DownloadProgress, PostprocessorProgress
from ytldl2.models.types import VideoId


class MusicDownloadTracker(Protocol):
    def new(self, video: VideoId) -> None:
        """Called when a new video is started."""

    def close(self, video: VideoId) -> None:
        """Called when a video is finished, after all postprocessors are done."""

    def on_download_progress(self, progress: DownloadProgress) -> None:
        """Called on download progress."""

    def on_postprocessor_progress(self, progress: PostprocessorProgress) -> None:
        """Called on postprocessor progress."""
