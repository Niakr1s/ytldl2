from __future__ import annotations

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
    def no_pending() -> QueueError:
        return QueueError("no item, pending mark")

    @staticmethod
    def has_pending() -> QueueError:
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

        self._current: VideoId | None = None
        self._current_index = 0

    @property
    def current(self) -> VideoId | None:
        return self._current

    def revert(self) -> None:
        """Simply returns pending mark back to queue."""
        if self._current is None:
            raise QueueError.no_pending()
        self._current = None
        self._current_index -= 1

    def mark_downloaded(self, path: pathlib.Path) -> None:
        if self._current is None:
            raise QueueError.no_pending()
        self.downloaded.append(Downloaded(self._current, path))
        self._current = None

    def mark_filtered(self, reason: str) -> None:
        if self._current is None:
            raise QueueError.no_pending()
        self.filtered.append(Filtered(self._current, reason))
        self._current = None

    def mark_skipped(self, reason: str) -> None:
        if self._current is None:
            raise QueueError.no_pending()
        self.skipped.append(Skipped(self._current, reason))
        self._current = None

    def __len__(self) -> int:
        return (
            len(self.videos)
            - len(self.downloaded)
            - len(self.filtered)
            - len(self.skipped)
            - (0 if self._current is None else 1)
        )

    def __next__(self) -> VideoId:
        if self._current_index >= len(self.videos):
            raise StopIteration

        if self._current is not None:
            raise QueueError.has_pending()

        self._current = self.videos[self._current_index]
        self._current_index += 1
        return self._current

    def __iter__(self) -> Iterator[VideoId]:
        return self
