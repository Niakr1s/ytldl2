from copy import copy

import pytest
from ytldl2.cache import CachedSongInfo
from ytldl2.memory_cache import MemoryCache
from ytldl2.models import VideoId

MOCK_SONG = CachedSongInfo(
    VideoId("test_video_id"),
    "test_filtered_reason",
)


class TestMemoryCache:
    @pytest.fixture
    def cache(self):
        return MemoryCache()

    def test_empty_cache(self, cache: MemoryCache):
        assert len(cache) == 0

    def test_get_set_len(self, cache: MemoryCache):
        assert len(cache) == 0

        cache.set(MOCK_SONG)
        assert len(cache) == 1
        assert MOCK_SONG.video_id in cache
        assert cache[MOCK_SONG.video_id] == MOCK_SONG

        cache.set(MOCK_SONG)
        assert len(cache) == 1

    def test_set_updates(self, cache: MemoryCache):
        cache.set(MOCK_SONG)

        updated = copy(MOCK_SONG)
        cache.set(updated)
        assert cache[MOCK_SONG.video_id]

    def test_iter(self, cache: MemoryCache):
        cache.set(MOCK_SONG)
        video_ids: list[VideoId] = list(cache)
        assert len(video_ids) == 1
        assert MOCK_SONG.video_id in video_ids
