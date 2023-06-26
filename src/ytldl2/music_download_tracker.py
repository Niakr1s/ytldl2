from typing import Protocol

from ytldl2.models.download_hooks import DownloadProgress
from ytldl2.models.types import VideoId


class MusicDownloadTracker(Protocol):
    def on_download_start(self, video: VideoId) -> None:
        """Called when a new video is started."""

    def on_download_finish(self, video: VideoId) -> None:
        """Called when a video is finished, after all postprocessors are done."""

    def on_video_skipped(self, video: VideoId, reason: str) -> None:
        """Called when a video is skipped."""

    def on_video_filtered(self, video: VideoId, filtered_reason: str) -> None:
        """Called when a video is filtered."""

    def on_download_progress(self, video: VideoId, progress: DownloadProgress) -> None:
        """Called on download progress."""
