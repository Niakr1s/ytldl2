import json
import pathlib
import sqlite3
import typing
from dataclasses import dataclass
from datetime import datetime
from os import PathLike
from pathlib import Path
from typing import Any, Iterator, NewType, Protocol, Self, Tuple, TypeVar, TypeVarTuple

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


class SqliteCache(Cache):
    def __init__(self, db_path: PathLike) -> None:
        self.db_path = pathlib.Path(db_path)
        self.conn: sqlite3.Connection

    def open(self) -> None:
        if not (db_existed := self.db_path.exists()):
            self.db_path.touch()

        self.conn = sqlite3.connect(self.db_path)

        if not db_existed:
            self._init_db()

        len(self)  # calling to ensure that db is valid

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()

    def set(self, song: CachedSongInfo) -> None:
        sql = r"""
INSERT INTO songs (
                      video_id,
                      title,
                      artist,
                      filtered_reason,
                      last_modified
                  )
                  VALUES (
                      ?,
                      ?,
                      ?,
                      ?,
                      ?
                  )
        """
        self.conn.cursor().execute(
            sql,
            (
                song.video_id,
                song.title,
                song.artist,
                song.filtered_reason,
                str(datetime.now()),
            ),
        )

    def __getitem__(self, video_id: VideoId) -> CachedSongInfo | None:
        sql = r"""
SELECT video_id,
       title,
       artist,
       filtered_reason
  FROM songs
 WHERE video_id = ?;
        """
        cur = self.conn.cursor().execute(sql, (video_id,))
        if not (song := cur.fetchone()):
            return None
        return CachedSongInfo(VideoId(song[0]), song[1], song[2], song[3])

    def __len__(self) -> int:
        return len(list(self.__iter__()))

    def __iter__(self) -> Iterator[VideoId]:
        sql = r"""select video_id from songs"""
        fetched = self.conn.cursor().execute(sql).fetchall()
        video_ids = [item[0] for item in fetched]
        return video_ids.__iter__()

    def _init_db(self):
        self._init_songs_table()
        self._set_db_version(1)

    def _init_songs_table(self):
        sql = r"""
CREATE TABLE songs (
    video_id        TEXT PRIMARY KEY ON CONFLICT REPLACE
                         NOT NULL,
    title           TEXT NOT NULL,
    artist          TEXT NOT NULL,
    filtered_reason TEXT,
    last_modified   TEXT NOT NULL
);
        """
        self.conn.cursor().execute(sql)

    def _set_db_version(self, v: int):
        self.conn.cursor().execute(f"PRAGMA user_version = {v}")

    @property
    def db_version(self) -> int:
        return self.conn.cursor().execute("PRAGMA user_version;").fetchone()[0]
