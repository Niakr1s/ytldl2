import pathlib
import sqlite3
from copy import copy
from time import sleep

import pytest
from ytldl2.cache import CachedVideo
from ytldl2.models import VideoId
from ytldl2.sqlite_cache import SqliteCache

from tests.ytldl2 import DATA

MOCK_VIDEO = CachedVideo(
    VideoId("test_video_id"),
    "test_filtered_reason",
)


class TestSqliteCache:
    @pytest.fixture
    def invalid_cache_path(
        self,
    ):
        return DATA / "invalid_cache.db"

    @pytest.fixture
    def cache(self, tmp_path: pathlib.Path):
        return SqliteCache(tmp_path / "cache.db")

    def test_empty_cache(self, cache):
        assert cache.db_version > 0
        assert len(cache) == 0

    def test_init_invalid_cache(self, invalid_cache_path):
        with pytest.raises((sqlite3.DatabaseError)):
            SqliteCache(invalid_cache_path)

    def test_close(self, cache: SqliteCache):
        cache.set(MOCK_VIDEO)
        video_ids = list(cache)
        cache.close()

        new_cache = SqliteCache(cache.db_path)

        new_video_ids = list(new_cache)
        assert set(video_ids) == set(new_video_ids)

    def test_set_with_none_attribute(self, cache: SqliteCache):
        MOCK_VIDEO.filtered_reason = None
        cache.set(MOCK_VIDEO)
        assert MOCK_VIDEO == cache[MOCK_VIDEO.video_id]

    def test_set_with_empty_attribute(self, cache: SqliteCache):
        MOCK_VIDEO.filtered_reason = ""
        cache.set(MOCK_VIDEO)
        assert MOCK_VIDEO == cache[MOCK_VIDEO.video_id]

    def test_get_set_len(self, cache: SqliteCache):
        assert len(cache) == 0

        cache.set(MOCK_VIDEO)
        assert len(cache) == 1
        assert MOCK_VIDEO.video_id in cache
        assert cache[MOCK_VIDEO.video_id] == MOCK_VIDEO

        cache.set(MOCK_VIDEO)
        assert len(cache) == 1

    def test_set_updates(self, cache: SqliteCache):
        cache.set(MOCK_VIDEO)

        updated = copy(MOCK_VIDEO)
        cache.set(updated)
        assert cache[MOCK_VIDEO.video_id]

    def test_iter(self, cache: SqliteCache):
        cache.set(MOCK_VIDEO)
        video_ids: list[VideoId] = list(cache)
        assert len(video_ids) == 1
        assert MOCK_VIDEO.video_id in video_ids

    def test_last_modified(self, cache: SqliteCache):
        cache.set(video=MOCK_VIDEO)
        last_modified_old = cache.last_modified(MOCK_VIDEO.video_id)
        assert last_modified_old

        SLEEP_SECS = 0.1
        sleep(SLEEP_SECS)
        cache.set(MOCK_VIDEO)
        diff = cache.last_modified(video_id=MOCK_VIDEO.video_id) - last_modified_old
        assert diff.total_seconds() >= SLEEP_SECS
