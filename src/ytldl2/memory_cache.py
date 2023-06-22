from typing import Iterator

from ytldl2.cache import Cache, CachedSongInfo
from ytldl2.models import VideoId


class MemoryCache(Cache):
    def __init__(self) -> None:
        self._cache: dict[VideoId, CachedSongInfo] = {}

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def set(self, song: CachedSongInfo) -> None:
        self._cache[song.video_id] = song

    def __getitem__(self, video_id: VideoId) -> CachedSongInfo | None:
        return self._cache.get(video_id)

    def __len__(self) -> int:
        return len(self._cache)

    def __iter__(self) -> Iterator[VideoId]:
        return self._cache.__iter__()
