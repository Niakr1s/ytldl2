from dataclasses import dataclass
from typing import Iterator, Protocol

from ytldl2.models import VideoId


@dataclass
class CachedSongInfo:
    video_id: VideoId
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
