import pathlib
import sqlite3
from importlib.abc import Traversable
from shutil import copy

import pytest

from tests import DATA
from ytldl2.cache import CachedSongInfo, SqliteCache, VideoId


def cp(file: Traversable, dir: pathlib.Path) -> pathlib.Path:
    to_path = dir / file.name
    with to_path.open("wb") as to:
        to.write(file.read_bytes())
    return to_path


@pytest.fixture
def non_exist_cache_path(tmp_path: pathlib.Path):
    return str(tmp_path / "non_exist_cache.db")


@pytest.fixture
def invalid_cache_path(tmp_path):
    return cp(DATA / "invalid_cache.db", tmp_path)


@pytest.fixture
def cache_path(tmp_path: pathlib.Path):
    return cp(DATA / "cache.db", tmp_path)


@pytest.fixture
def cache(cache_path):
    cache = SqliteCache(cache_path)
    cache.open()
    return cache


@pytest.fixture
def empty_valid_cache(non_exist_cache_path):
    cache = SqliteCache(non_exist_cache_path)
    cache.open()
    return cache


MOCK_SONG = CachedSongInfo(
    VideoId("test_video_id"),
    "test_title",
    "test_artist",
    "test_filtered_reason",
)


STORED_SONG = CachedSongInfo(
    VideoId("9khpyvTIBBc"),
    "Ray",
    "BUMP OF CHICKEN",
    "some meaningful reason",
)


def test_open_non_exist_cache(non_exist_cache_path):
    cache = SqliteCache(non_exist_cache_path)
    cache.open()
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


def test_valid_cache_has_stored_song(cache: SqliteCache):
    got = cache[STORED_SONG.video_id]
    assert got is not None
    assert STORED_SONG == got


def test_get_set_len(cache: SqliteCache):
    assert len(cache) == 1

    cache.set(MOCK_SONG)
    assert len(cache) == 2
    assert MOCK_SONG.video_id in cache
    assert cache[MOCK_SONG.video_id] == MOCK_SONG

    cache.set(MOCK_SONG)
    assert len(cache) == 2


def test_set_updates(cache: SqliteCache):
    song = cache[STORED_SONG.video_id]
    assert song is not None
    NEW_ARTIST = "new artist"
    song.artist = NEW_ARTIST
    cache.set(song)
    assert (song := cache[STORED_SONG.video_id]) and song.artist == NEW_ARTIST


def test_iter(cache: SqliteCache):
    song_to_set = MOCK_SONG
    assert len(list(cache)) == 1
    cache.set(song_to_set)
    video_ids: list[VideoId] = list(cache)
    assert len(video_ids) == 2
    assert STORED_SONG.video_id in video_ids
    assert song_to_set.video_id in video_ids
