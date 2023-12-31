from typing import Protocol

from ytldl2.models.download_hooks import DownloadProgress, PostprocessorProgress
from ytldl2.models.download_result import DownloadResult
from ytldl2.models.home_items import HomeItems, HomeItemsFilter
from ytldl2.models.song import Song
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


class HomeItemsReviewer(Protocol):
    def review_home_items(
        self, home_items: HomeItems, home_items_filter: HomeItemsFilter
    ):
        """
        Should review home items. Param home_items should be left unchangeable,
        but home_items_filter can be changed. Every change in home_items_filter
        will be persisted.
        """


class BatchDownloadTracker(Protocol):
    def start(self, songs: list[Song], limit: int | None):
        """Called by library before batch starts."""
        ...

    def on_download_result(self, result: DownloadResult):
        """Called by library on each download result."""
        ...

    def end(self):
        """Called by library after batch ends."""
        ...


class Ui(Protocol):
    """Ui for music library."""

    def library_update_started(self):
        """Should inform user that library update started."""
        ...

    def home_items_reviewer(self) -> HomeItemsReviewer:
        """
        Should return home items reviewer, that will be called after
        home items have been fetched.
        """
        ...

    def batch_download_tracker(self) -> BatchDownloadTracker:
        """Should return class used to track batch download progress."""
        ...

    def progress_bar(self) -> ProgressBar:
        """
        Should return class used to track single song download progress.
        """
        ...
