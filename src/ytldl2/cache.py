import json
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, NewType, Protocol, TypeVarTuple

VideoId = NewType("VideoId", str)


@dataclass
class CachedSongInfo:
    video_id: VideoId
    title: str
    artist: str
    filtered_reason: str | None

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"


class Cache(Protocol):
    def open(self) -> None:
        """
        Should init cache.
        """

    def close(self) -> None:
        """
        Should force dump data and close resources.
        """

    def set(self, song: CachedSongInfo) -> None:
        ...

    def __getitem__(self, video_id: VideoId) -> CachedSongInfo | None:
        ...

    def __len__(self) -> int:
        ...

    def __iter__(self) -> Iterator[VideoId]:
        ...
