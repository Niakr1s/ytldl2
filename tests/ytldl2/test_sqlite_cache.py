import pathlib
import sqlite3
from copy import copy
from datetime import datetime
from time import sleep

import pytest

from tests.ytldl2 import DATA
from ytldl2 import VideoId
from ytldl2.cache import CachedSongInfo
from ytldl2.sqlite_cache import SqliteCache


@pytest.fixture
def invalid_cache_path():
    return DATA / "invalid_cache.db"


@pytest.fixture
def cache(tmp_path: pathlib.Path):
    cache = SqliteCache(tmp_path / "cache.db")
    cache.open()
    return cache


MOCK_SONG = CachedSongInfo(
    VideoId("test_video_id"),
    "test_title",
    "test_artist",
    "test_filtered_reason",
)


def test_empty_cache(cache):
    assert cache.db_version > 0
    assert len(cache) == 0


def test_open_invalid_cache(invalid_cache_path):
    with pytest.raises((sqlite3.DatabaseError)):
        SqliteCache(invalid_cache_path).open()


def test_close(cache: SqliteCache):
    cache.set(MOCK_SONG)
    video_ids = list(cache)
    cache.close()

    new_cache = SqliteCache(cache.db_path)
    new_cache.open()

    new_video_ids = list(new_cache)
    assert set(video_ids) == set(new_video_ids)


def test_set_with_none_attribute(cache: SqliteCache):
    MOCK_SONG.filtered_reason = None
    cache.set(MOCK_SONG)
    assert MOCK_SONG == cache[MOCK_SONG.video_id]


def test_set_with_empty_attribute(cache: SqliteCache):
    MOCK_SONG.filtered_reason = ""
    cache.set(MOCK_SONG)
    assert MOCK_SONG == cache[MOCK_SONG.video_id]


def test_get_set_len(cache: SqliteCache):
    assert len(cache) == 0

    cache.set(MOCK_SONG)
    assert len(cache) == 1
    assert MOCK_SONG.video_id in cache
    assert cache[MOCK_SONG.video_id] == MOCK_SONG

    cache.set(MOCK_SONG)
    assert len(cache) == 1


def test_set_updates(cache: SqliteCache):
    cache.set(MOCK_SONG)

    updated = copy(MOCK_SONG)
    updated.artist = "new artist"
    cache.set(updated)
    assert (updated := cache[MOCK_SONG.video_id]) and updated.artist == updated.artist


def test_iter(cache: SqliteCache):
    cache.set(MOCK_SONG)
    video_ids: list[VideoId] = list(cache)
    assert len(video_ids) == 1
    assert MOCK_SONG.video_id in video_ids


def test_last_modified(cache: SqliteCache):
    cache.set(song=MOCK_SONG)
    last_modified_old = cache.last_modified(MOCK_SONG.video_id)
    assert last_modified_old

    SLEEP_SECS = 0.1
    sleep(SLEEP_SECS)
    cache.set(MOCK_SONG)
    diff = cache.last_modified(video_id=MOCK_SONG.video_id) - last_modified_old
    assert diff.total_seconds() >= SLEEP_SECS
