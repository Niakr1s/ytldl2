migrations: list[list[str]] = []
"""
(Index+1) of each migration corresponds to migration version.
Warning: DON'T EVER REMOVE MIGRATIONS, JUST ADD NEW BELOW.
"""

migrations.append(
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
        """
    ]
)

migrations.append(
    r"""
PRAGMA foreign_keys = 0;
CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM songs;
DROP TABLE songs;
CREATE TABLE songs (
    video_id        TEXT PRIMARY KEY ON CONFLICT REPLACE
                         NOT NULL,
    filtered_reason TEXT,
    last_modified   TEXT NOT NULL
);
INSERT INTO songs (
                      video_id,
                      filtered_reason,
                      last_modified
                  )
                  SELECT video_id,
                         filtered_reason,
                         last_modified
                    FROM sqlitestudio_temp_table;
DROP TABLE sqlitestudio_temp_table;
PRAGMA foreign_keys = 1;
        """.split(
        ";"
    )
)
migrations.append(
    r"""
PRAGMA foreign_keys = 0;
CREATE TABLE cache (
    video_id        TEXT PRIMARY KEY ON CONFLICT REPLACE
                         NOT NULL,
    filtered_reason TEXT,
    last_modified   TEXT NOT NULL
);
INSERT INTO cache (
                      video_id,
                      filtered_reason,
                      last_modified
                  )
                  SELECT video_id,
                         filtered_reason,
                         last_modified
                    FROM songs;
DROP TABLE songs;
PRAGMA foreign_keys = 1;
        """.split(
        ";"
    )
)
migrations.append(
    [
        r"""
CREATE TABLE song_info (
    id       TEXT    PRIMARY KEY ON CONFLICT REPLACE
                     NOT NULL,
    title    TEXT    NOT NULL,
    duration INTEGER NOT NULL,
    channel  TEXT,
    artist   TEXT    NOT NULL,
    lyrics   TEXT
);
        """
    ]
)
migrations.append(
    r"""
PRAGMA foreign_keys = 0;
CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM song_info;
DROP TABLE song_info;
CREATE TABLE song_info (
    id       TEXT    PRIMARY KEY ON CONFLICT REPLACE
                     NOT NULL,
    title    TEXT    NOT NULL,
    duration INTEGER NOT NULL,
    channel  TEXT,
    artist   TEXT    NOT NULL
);
INSERT INTO song_info (
                          id,
                          title,
                          duration,
                          channel,
                          artist
                      )
                      SELECT id,
                             title,
                             duration,
                             channel,
                             artist
                        FROM sqlitestudio_temp_table;
DROP TABLE sqlitestudio_temp_table;
PRAGMA foreign_keys = 1;
        """.split(
        ";"
    )
)
