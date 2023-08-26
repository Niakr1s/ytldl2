from typing import Iterable, Iterator, Protocol

import pydantic
from ytldl2.models.types import VideoId


class CachedVideo(pydantic.BaseModel):
    video_id: VideoId

    filtered_reason: str | None


class SongInfo(pydantic.BaseModel):
    id: VideoId
    title: str
    duration: int
    channel: str | None
    """I'm pretty sure it won't have None, but made optional just in case"""
    artist: str


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

    def get_infos(self, video_ids: list[VideoId]) -> dict[VideoId, SongInfo | None]:
        return {id: self.get_info(id) for id in video_ids}

    def filter_cached(self, videos: Iterable[VideoId]) -> Iterable[VideoId]:
        """Filters out cached videos"""
        return (video for video in videos if video not in self)
