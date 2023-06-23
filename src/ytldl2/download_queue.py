import pathlib
from dataclasses import dataclass

from ytldl2.models import VideoId


@dataclass
class Downloaded:
    video_id: VideoId
    path: pathlib.Path


@dataclass
class Failed:
    video_id: VideoId
    error: Exception


@dataclass
class Skipped:
    video_id: VideoId
    reason: str


class ItemNotCompletedError(Exception):
    pass


class ItemAlreadyCompletedError(Exception):
    pass


class Item:
    def __init__(self, queue: "DownloadQueue", video_id: VideoId) -> None:
        self.queue = queue
        self.video_id = video_id
        self._completed = False

    def _complete(self):
        if self._completed:
            raise ItemAlreadyCompletedError
        self.queue._has_incompleted_item = False
        self._completed = True

    def mark_as_downloaded(self, path: pathlib.Path):
        self._complete()
        self.queue.downloaded.append(Downloaded(self.video_id, path))

    def mark_as_failed(self, error: Exception):
        self._complete()
        self.queue.failed.append(Failed(self.video_id, error))

    def mark_as_skipped(self, reason: str):
        self._complete()
        self.queue.skipped.append(Skipped(self.video_id, reason))


@dataclass
class DownloadResult:
    videos: list[VideoId]
    """Initial video list. Always remains unchanged."""
    remained: list[VideoId]
    """Queue of videos, waiting to be downloaded."""
    downloaded: list[Downloaded]
    failed: list[Failed]
    skipped: list[Skipped]


class DownloadQueueHasUncompleteItem(Exception):
    pass


class DownloadQueue:
    def __init__(self, videos: list[VideoId]) -> None:
        self.videos: list[VideoId] = videos[:]
        """Initial video list. Always remains unchanged."""
        self.remained: list[VideoId] = list(reversed(videos))
        """Queue of videos, waiting to be downloaded."""
        self.downloaded: list[Downloaded] = []
        self.failed: list[Failed] = []
        self.skipped: list[Skipped] = []

        self._has_incompleted_item = False

    def __len__(self) -> int:
        return len(self.remained)

    def __next__(self) -> Item:
        """Iterates over self.remained videos.
        User should use .mark_as method on each item to mark it as completed.
        Raises:
            ItemNotMarkedError: Raised when Item is not marked as completed.
        Returns:
            Item: Next item in queue.
        """
        if self._has_incompleted_item:
            raise ItemNotCompletedError

        try:
            next_video_id = self.remained.pop()
            self._has_incompleted_item = True
        except IndexError:
            raise StopIteration
        return Item(self, next_video_id)

    def to_result(self) -> DownloadResult:
        """Returns download reuslt. Makes copies of inner data.

        Raises:
            DownloadQueueHasUncompleteItem: Raises when some item retrieved
            from self.remained via __next__ method, but had not marked as completed.

        Returns:
            DownloadResult: _description_
        """
        if self._has_incompleted_item:
            raise DownloadQueueHasUncompleteItem

        return DownloadResult(
            self.videos[:],
            self.remained[:],
            self.downloaded[:],
            self.failed[:],
            self.skipped[:],
        )
