import pathlib
from dataclasses import dataclass
from typing import Iterator

from ytldl2.models.types import VideoId, WithVideoId


@dataclass
class Downloaded(WithVideoId):
    path: pathlib.Path


@dataclass
class Filtered(WithVideoId):
    filtered_reason: str


@dataclass
class Skipped(WithVideoId):
    reason: str


class QueueError(Exception):
    @staticmethod
    def no_pending() -> "QueueError":
        return QueueError("no item, pending mark")

    @staticmethod
    def has_pending() -> "QueueError":
        return QueueError("has item, pending mark")


class DownloadQueue:
    """
    Download queue of videos. User can get next item via next() method. For full
    description of it usage, see .next() doc.
    """

    def __init__(self, videos: list[VideoId]) -> None:
        self.videos: list[VideoId] = videos[:]
        """Initial video list. Always remains unchanged."""

        self.downloaded: list[Downloaded] = []
        """List of downloaded items. Should be cached."""
        self.filtered: list[Filtered] = []
        """List of filtered items. These items are intendend to be cached too."""
        self.skipped: list[Skipped] = []
        """List of items, skipped due to various reasons."""

        self._pending_mark: VideoId | None = None
        self._current_index = 0

    @property
    def pending_mark(self) -> VideoId | None:
        return self._pending_mark

    def revert(self) -> None:
        """Simply returns pending mark back to queue."""
        if self._pending_mark is None:
            raise QueueError.no_pending()
        self._pending_mark = None
        self._current_index -= 1

    def mark_downloaded(self, path: pathlib.Path) -> None:
        if self._pending_mark is None:
            raise QueueError.no_pending()
        self.downloaded.append(Downloaded(self._pending_mark, path))
        self._pending_mark = None

    def mark_filtered(self, reason: str) -> None:
        if self._pending_mark is None:
            raise QueueError.no_pending()
        self.filtered.append(Filtered(self._pending_mark, reason))
        self._pending_mark = None

    def mark_skipped(self, reason: str) -> None:
        if self._pending_mark is None:
            raise QueueError.no_pending()
        self.skipped.append(Skipped(self._pending_mark, reason))
        self._pending_mark = None

    def __len__(self) -> int:
        return (
            len(self.videos)
            - len(self.downloaded)
            - len(self.filtered)
            - len(self.skipped)
            - (0 if self._pending_mark is None else 1)
        )

    def __next__(self) -> VideoId:
        if self._current_index >= len(self.videos):
            raise StopIteration

        if self._pending_mark is not None:
            raise QueueError.has_pending()

        self._pending_mark = self.videos[self._current_index]
        self._current_index += 1
        return self._pending_mark

    def __iter__(self) -> Iterator[VideoId]:
        return self
