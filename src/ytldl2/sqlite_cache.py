import pathlib
import sqlite3
from datetime import datetime
from typing import Iterator, Literal

from ytldl2.models.info import SongInfo
from ytldl2.models.types import VideoId
from ytldl2.protocols.cache import Cache, CachedVideo
from ytldl2.sqlite_cache_migrations import migrations


class MigrationError(Exception):
    pass


class SqliteCache(Cache):
    def __init__(
        self, db_path: pathlib.Path | Literal[":memory:"] = ":memory:"
    ) -> None:
        """
        :param db_path: Can be also ":memory:" for RAM usage.
        """
        self.db_path: pathlib.Path | Literal[":memory:"] = db_path
        self.conn = self._init_connection(self.db_path)
        self._apply_migrations_if_needed()
        len(self)  # calling to ensure that db is valid

    @staticmethod
    def _init_connection(
        db_path: pathlib.Path | Literal[":memory:"],
    ) -> sqlite3.Connection:
        db_path_str: str

        match db_path:
            case pathlib.Path():
                if not db_path.exists():
                    db_path.touch()
                db_path_str = str(db_path)
            case ":memory:":
                db_path_str = db_path
            case _:
                raise ValueError(f"db path {db_path} is nor file path, nor ':memory:'")

        conn = sqlite3.connect(db_path_str)
        return conn

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()

    def set(self, video: CachedVideo) -> None:
        sql = r"""
INSERT INTO cache (
                      video_id,
                      filtered_reason,
                      last_modified
                  )
                  VALUES (
                      ?,
                      ?,
                      ?
                  )
        """
        self.conn.cursor().execute(
            sql,
            (
                video.video_id,
                video.filtered_reason,
                str(datetime.now()),
            ),
        )
        self.conn.commit()

    def __getitem__(self, video_id: VideoId) -> CachedVideo | None:
        sql = r"""
SELECT video_id,
       filtered_reason
  FROM cache
 WHERE video_id = ?;
        """
        cur = self.conn.cursor().execute(sql, (video_id,))
        if not (video := cur.fetchone()):
            return None
        return CachedVideo(video_id=VideoId(video[0]), filtered_reason=video[1])

    def __len__(self) -> int:
        return len(list(self.__iter__()))

    def __iter__(self) -> Iterator[VideoId]:
        sql = r"""select video_id from cache"""
        fetched = self.conn.cursor().execute(sql).fetchall()
        video_ids = [item[0] for item in fetched]
        return video_ids.__iter__()

    def last_modified(self, video_id: VideoId) -> datetime:
        fetched = (
            self.conn.cursor()
            .execute("SELECT last_modified FROM cache WHERE video_id = ?;", (video_id,))
            .fetchone()
        )
        if not fetched:
            raise LookupError()
        return datetime.fromisoformat(fetched[0])

    def set_info(self, song_info: SongInfo):
        sql = r"""
INSERT INTO song_info (
                          id,
                          title,
                          duration,
                          channel,
                          artist
                      )
                      VALUES (?, ?, ?, ?, ?);
            """
        self.conn.execute(
            sql,
            [
                song_info.id,
                song_info.title,
                song_info.duration,
                song_info.channel,
                song_info.artist,
            ],
        )
        self.conn.commit()

    def get_info(self, video_id: VideoId) -> SongInfo | None:
        sql = r"""
SELECT id,
       title,
       duration,
       channel,
       artist
  FROM song_info
  WHERE id = ?
        """
        if not (info := self.conn.execute(sql, [video_id]).fetchone()):
            return None
        return SongInfo(
            id=info[0],
            title=info[1],
            duration=info[2],
            channel=info[3],
            artist=info[4],
        )

    def _apply_migrations_if_needed(self):
        if (db_version := self.db_version) < 0:
            raise MigrationError("db version is < 0")
        elif db_version < len(migrations):
            # actual work here
            for migration in migrations[db_version:]:
                for sql in migration:
                    self.conn.cursor().execute(sql)
            self._set_db_version(len(migrations))
            self.conn.commit()
            # migrations ended
        elif db_version == len(migrations):
            return
        else:
            raise MigrationError("db version exeeds available migrations")

    def _set_db_version(self, v: int):
        self.conn.cursor().execute(f"PRAGMA user_version = {v}")
        self.conn.commit()

    @property
    def db_version(self) -> int:
        return self.conn.cursor().execute("PRAGMA user_version;").fetchone()[0]
