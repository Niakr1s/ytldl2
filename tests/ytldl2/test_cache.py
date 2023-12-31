from ytldl2.models.info import SongInfo
from ytldl2.models.types import VideoId
from ytldl2.sqlite_cache import SqliteCache


class TestCache:
    SONG_INFO = SongInfo(
        id=VideoId("id"),
        title="title",
        duration=3,
        channel="channel",
        artist="artist",
    )

    def test_get_infos(self):
        cache = SqliteCache()
        another_info = self.SONG_INFO.copy()
        another_info.id = VideoId("another info")
        ids = [self.SONG_INFO.id, another_info.id]
        cache.set_info(self.SONG_INFO)
        cache.set_info(another_info)

        for expected in [ids, [*ids, "third id"]]:
            assert set(expected) == set((got_infos := cache.get_infos(expected)).keys())
            assert self.SONG_INFO.id in got_infos
            assert another_info.id in got_infos
