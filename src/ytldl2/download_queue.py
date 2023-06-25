import pathlib
from dataclasses import dataclass

from ytldl2.models.types import VideoId, WithVideoId


@dataclass
class Downloaded(WithVideoId):
    path: pathlib.Path


@dataclass
class Filtered(WithVideoId):
    filtered_reason: str


@dataclass
class Failed(WithVideoId):
    error: Exception


@dataclass
class Skipped(WithVideoId):
    reason: str


class ItemNotCompletedError(Exception):
    pass


class ItemModifyNotAllowed(Exception):
    pass


class Item:
    def __init__(self, queue: "DownloadQueue", video_id: VideoId) -> None:
        self.queue = queue
        self.video_id = video_id
        self._modify_allowed = True

    def _complete(self):
        if not self._modify_allowed:
            raise ItemModifyNotAllowed
        self.queue._has_incompleted_item = False
        self._modify_allowed = False

    def complete_as_downloaded(self, path: pathlib.Path):
        self._complete()
        self.queue._downloaded.append(Downloaded(self.video_id, path))

    def complete_as_filtered(self, filtered_reason: str):
        self._complete()
        self.queue._filtered.append(
            Filtered(self.video_id, filtered_reason=filtered_reason)
        )

    def complete_as_failed(self, error: Exception):
        self._complete()
        self.queue._failed.append(Failed(self.video_id, error))

    def complete_as_skipped(self, reason: str):
        self._complete()
        self.queue._skipped.append(Skipped(self.video_id, reason))

    def return_to_queue(self):
        self._complete()
        self.queue._queue.append(self.video_id)

    def __repr__(self) -> str:
        return f"Item({self.video_id}, modify_allowed={self._modify_allowed})"


@dataclass
class DownloadResult:
    """
    Result of download.
    Attributes, that are intended to be cached are: downloaded and filtered.
    """

    videos: list[VideoId]
    """Initial video list. Always remains unchanged."""
    queue: list[VideoId]
    """Queue of videos, waiting to be downloaded."""

    downloaded: list[Downloaded]
    """List of downloaded items. Should be cached by caller."""

    filtered: list[Filtered]
    """List of filtered items. Should be cached by caller."""

    skipped: list[Skipped]
    """Just skipped. Should not be cached by caller."""

    failed: list[Failed]
    """Failed due to external reasons, e.g network problems etc."""


class DownloadQueueHasUncompleteItem(Exception):
    pass


class DownloadQueue:
    """
    Download queue of videos. User can get next item via next() method. For full
    description of it usage, see .next() doc.
    """

    def __init__(self, videos: list[VideoId]) -> None:
        self._videos: list[VideoId] = videos[:]
        """Initial video list. Always remains unchanged."""
        self._queue: list[VideoId] = list(reversed(videos))
        """Queue of videos, waiting to be downloaded."""

        self._downloaded: list[Downloaded] = []
        """List of downloaded items. Should be cached."""
        self._filtered: list[Filtered] = []
        """List of filtered items. These items are intendend to be cached too."""
        self._failed: list[Failed] = []
        """List of items, that failed to download."""
        self._skipped: list[Skipped] = []
        """List of items, skipped due to various reasons."""

        self._has_incompleted_item = False

    def __len__(self) -> int:
        return len(self._queue)

    def next(self) -> Item | None:
        """Iterates over self.remained videos. Doesn't throw StopIteration - instead,
        returns None if no items remained.
        User should use .complete_as method on each item to mark it as completed.
        User can also return item to queue using .return_to_queue method.
        If user don't mark or return item, next call to this method will raise
        ItemNotCompletedError.

        Raises:
            ItemNotCompletedError: Raised when previously retrieved item
            is not marked as completed.
        Returns:
            Item: Next item in queue.
        """
        if self._has_incompleted_item:
            raise ItemNotCompletedError

        try:
            next_video_id = self._queue.pop()
            self._has_incompleted_item = True
        except IndexError:
            return None
        return Item(self, next_video_id)

    def to_result(self) -> DownloadResult:
        """Returns download reuslt. Makes copies of inner data.

        Raises:
            DownloadQueueHasUncompleteItem: Raises when some item retrieved
            from self.remained via next method, but had not marked as completed.

        Returns:
            DownloadResult: _description_
        """
        if self._has_incompleted_item:
            raise DownloadQueueHasUncompleteItem

        return DownloadResult(
            self._videos[:],
            self._queue[:],
            self._downloaded[:],
            self._filtered[:],
            self._skipped[:],
            self._failed[:],
        )
