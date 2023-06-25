import pathlib
from typing import TypeVar

import pytest
from yt_dlp.postprocessor.ffmpeg import FFmpegExtractAudioPP
from ytldl2.cache import CachedVideo
from ytldl2.cancellation_tokens import CancellationToken
from ytldl2.models.types import VideoId, WithVideoId
from ytldl2.music_downloader import (
    MusicDownloader,
    MusicDownloadError,
    MusicYoutubeDlBuilder,
    YoutubeDlParams,
)
from ytldl2.postprocessors import FilterSongPP, LyricsPP, MetadataPP, RetainMainArtistPP
from ytldl2.sqlite_cache import SqliteCache

from tests.ytldl2.marks import slow_test


class TestMusicYoutubeDlBuilder:
    @slow_test
    def test_build(self):
        params = YoutubeDlParams(
            home_dir=pathlib.Path("~"),
            tmp_dir=pathlib.Path("f:/"),
        )

        builder = MusicYoutubeDlBuilder(params)

        ydl = builder.build()

        ydl_params = ydl.params
        assert str(params.home_dir) == ydl_params["paths"]["home"]
        assert str(params.tmp_dir) == ydl_params["paths"]["tmp"]

        pre_processes = ydl._pps["pre_process"]
        assert len(pre_processes) == 2
        assert isinstance(pre_processes[0], FilterSongPP)
        assert isinstance(pre_processes[1], RetainMainArtistPP)

        post_processes = ydl._pps["post_process"]
        assert len(post_processes) == 3
        assert isinstance(post_processes[0], FFmpegExtractAudioPP)
        assert isinstance(post_processes[1], LyricsPP)
        assert isinstance(post_processes[2], MetadataPP)


class TestMusicDownloader:
    INVALID_VIDEO = VideoId("NOT_VALID")
    SONG_WITH_LYRICS = VideoId("OCYdICRobEo")
    SONG_WITHOUT_LYRICS = VideoId("rVryEboMof8")
    VIDEO = VideoId("F7NOovxx3lg")
    VIDEOS = [
        # INVALID_VIDEO,
        VIDEO,
        SONG_WITH_LYRICS,
        SONG_WITHOUT_LYRICS,
    ]

    @pytest.fixture
    def ydl_params(self, tmp_path: pathlib.Path) -> YoutubeDlParams:
        music_tmp_dir = tmp_path / "tmp"
        music_home_dir = tmp_path / "home"
        return YoutubeDlParams(home_dir=music_home_dir, tmp_dir=music_tmp_dir)

    @slow_test
    def test_download(self, ydl_params: YoutubeDlParams):
        cache = SqliteCache()

        expected_downloaded = [
            self.SONG_WITH_LYRICS,
            self.SONG_WITHOUT_LYRICS,
        ]
        expected_filtered = [self.VIDEO]
        expected_skipped = []

        self._test_download(
            MusicDownloader(cache, ydl_params),
            self.VIDEOS[:],
            expected_downloaded,
            expected_filtered,
            expected_skipped,
            skip_download=False,
        )
        assert set(expected_downloaded) == set(
            cache.get_infos(expected_downloaded).keys()
        )
        assert set(expected_filtered) == set(cache.get_infos(expected_filtered).keys())

    @slow_test
    def test_download__respects_cache(self, ydl_params: YoutubeDlParams):
        cache = SqliteCache()

        for video_id in self.VIDEOS:
            cache.set(CachedVideo(video_id=video_id, filtered_reason=None))
        expected_downloaded = []
        expected_filtered = []
        expected_skipped = self.VIDEOS[:]

        self._test_download(
            MusicDownloader(cache, ydl_params),
            self.VIDEOS[:],
            expected_downloaded,
            expected_filtered,
            expected_skipped,
            skip_download=True,
        )

    @slow_test
    def test_download_with_skip_download(self, ydl_params: YoutubeDlParams):
        expected_downloaded = []
        expected_filtered = [self.VIDEO]
        expected_skipped = [
            self.SONG_WITH_LYRICS,
            self.SONG_WITHOUT_LYRICS,
        ]

        cache = SqliteCache()
        self._test_download(
            MusicDownloader(cache, ydl_params),
            self.VIDEOS[:],
            expected_downloaded,
            expected_filtered,
            expected_skipped,
            skip_download=True,
        )
        assert set(expected_skipped) == set(cache.get_infos(expected_skipped).keys())

    @slow_test
    def test_download_with_err(self, ydl_params: YoutubeDlParams):
        expected_downloaded = []
        expected_filtered = [self.VIDEO]
        expected_skipped = [
            self.SONG_WITH_LYRICS,
            self.SONG_WITHOUT_LYRICS,
        ]
        with pytest.raises(MusicDownloadError) as err:
            self._test_download(
                MusicDownloader(SqliteCache(), ydl_params),
                [*self.VIDEOS, self.INVALID_VIDEO],
                expected_downloaded,
                expected_filtered,
                expected_skipped,
                skip_download=True,
            )
        queue = err.value.queue
        assert len(queue) == 1
        assert expected_downloaded == self.to_video_ids(queue.downloaded)
        assert expected_filtered == self.to_video_ids(queue.filtered)
        assert expected_skipped == self.to_video_ids(queue.skipped)

    def test_download__cancellation_token(self, ydl_params: YoutubeDlParams):
        token = CancellationToken()
        token.request_kill()

        self._test_download(
            MusicDownloader(SqliteCache(), ydl_params),
            self.VIDEOS,
            [],
            [],
            self.VIDEOS[:],
            token=token,
            skip_download=True,
        )

    def _test_download(
        self,
        downloader: MusicDownloader,
        videos: list[VideoId],
        expected_downloaded: list[VideoId],
        expected_filtered: list[VideoId],
        expected_skipped: list[VideoId],
        skip_download: bool,
        token: CancellationToken = CancellationToken(),
    ):
        cache_items_before = {x for x in downloader._cache}
        res = downloader.download(
            videos, cancellation_token=token, skip_download=skip_download
        )

        assert videos == res.videos
        assert len(res) == 0

        got_downloaded = self.to_video_ids(res.downloaded)
        got_filtered = self.to_video_ids(res.filtered)
        got_skipped = self.to_video_ids(res.skipped)

        assert expected_downloaded == got_downloaded
        assert expected_filtered == got_filtered
        assert expected_skipped == got_skipped

        expected_cache = {*cache_items_before, *expected_downloaded, *expected_filtered}
        assert expected_cache == {x for x in downloader._cache}

    WithVideoIdT = TypeVar("WithVideoIdT", bound=WithVideoId)

    @staticmethod
    def to_video_ids(lst: list[WithVideoIdT]):
        return [x.video_id for x in lst]
