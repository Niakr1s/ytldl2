import pathlib
import sqlite3
from datetime import datetime
from os import PathLike
from typing import Iterator

from ytldl2 import VideoId
from ytldl2.cache import Cache, CachedSongInfo

SqlCommands = list[str]

_migrations: list[SqlCommands] = [
    [
        r"""
CREATE TABLE songs (
    video_id        TEXT PRIMARY KEY ON CONFLICT REPLACE
                         NOT NULL,
    title           TEXT NOT NULL,
    artist          TEXT NOT NULL,
    filtered_reason TEXT,
    last_modified   TEXT NOT NULL
);
        """,
    ],
]
"""
(Index+1) of each migration corresponds to migration version.
Warning: DON'T EVER REMOVE MIGRATIONS, JUST ADD NEW.
"""


class MigrationError(Exception):
    pass


class SqliteCache(Cache):
    def __init__(self, db_path: PathLike) -> None:
        self.db_path = pathlib.Path(db_path)
        self.conn: sqlite3.Connection

    def open(self) -> None:
        if not self.db_path.exists():
            self.db_path.touch()

        self.conn = sqlite3.connect(self.db_path)
        self._apply_migrations_if_needed()

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

    def last_modified(self, video_id: VideoId) -> datetime:
        fetched = (
            self.conn.cursor()
            .execute("SELECT last_modified FROM songs WHERE video_id = ?;", (video_id,))
            .fetchone()
        )
        if not fetched:
            raise LookupError()
        return datetime.fromisoformat(fetched[0])

    def _apply_migrations_if_needed(self):
        if (db_version := self.db_version) < 0:
            raise MigrationError(f"db version is < 0")
        elif db_version < len(_migrations):
            # actual work here
            cur = self.conn.cursor()
            for migration in _migrations[db_version:]:
                for sql in migration:
                    cur.execute(sql)
            self._set_db_version(len(_migrations))
            self.conn.commit()
            # migrations ended
        elif db_version == len(_migrations):
            return
        else:
            raise MigrationError(f"db version exeeds available migrations")

    def _set_db_version(self, v: int):
        self.conn.cursor().execute(f"PRAGMA user_version = {v}")

    @property
    def db_version(self) -> int:
        return self.conn.cursor().execute("PRAGMA user_version;").fetchone()[0]
