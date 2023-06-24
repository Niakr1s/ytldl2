from typing import Iterator, Protocol

import pydantic

from ytldl2.models import VideoId


class CachedVideo(pydantic.BaseModel):
    video_id: VideoId
    filtered_reason: str | None

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"


class SongInfo(pydantic.BaseModel):
    id: VideoId
    title: str
    duration: int
    channel: str | None
    """I'm pretty sure it won't have None, but made optional just in case"""
    artist: str
    lyrics: str | None


class Cache(Protocol):
    def close(self) -> None:
        """
        Should force dump data and close resources.
        """

    def set(self, video: CachedVideo) -> None:
        ...

    def __getitem__(self, video_id: VideoId) -> CachedVideo | None:
        ...

    def __len__(self) -> int:
        ...

    def __iter__(self) -> Iterator[VideoId]:
        ...

    def set_info(self, video_info: SongInfo):
        ...

    def get_info(self, video_id: VideoId) -> SongInfo | None:
        ...
