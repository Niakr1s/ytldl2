import logging
import pathlib

import pytest
from yt_dlp.postprocessor.ffmpeg import FFmpegExtractAudioPP

from tests.ytldl2.marks import slow_test
from ytldl2.models import VideoId
from ytldl2.music_downloader import (
    MusicDownloader,
    MusicYoutubeDlBuilder,
    YoutubeDlParams,
)
from ytldl2.postprocessors import FilterSongPP, LyricsPP, MetadataPP, RetainMainArtistPP


class TestMusicYoutubeDlBuilder:
    @slow_test
    def test_build(self):
        params = YoutubeDlParams(
            logger=logging.Logger("logger"),
            home_dir=pathlib.Path("~"),
            tmp_dir=pathlib.Path("f:/"),
            progress_hooks=["progress_hook"],
            postprocessor_hooks=["postprocessor_hook"],
            skip_download=True,
        )

        builder = MusicYoutubeDlBuilder(params)

        ydl = builder.build()

        ydl_params = ydl.params
        assert params.logger == ydl_params["logger"]
        assert str(params.home_dir) == ydl_params["paths"]["home"]
        assert str(params.tmp_dir) == ydl_params["paths"]["tmp"]
        assert params.progress_hooks == ydl_params["progress_hooks"]
        assert params.postprocessor_hooks == ydl_params["postprocessor_hooks"]
        assert params.skip_download == ydl_params["skip_download"]

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
        INVALID_VIDEO,
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
        ydl_params.skip_download = False

        expected_downloaded = [
            self.SONG_WITH_LYRICS,
            self.SONG_WITHOUT_LYRICS,
        ]
        expected_failed = [self.INVALID_VIDEO]
        expected_skipped = [self.VIDEO]
        self._test_download(
            ydl_params,
            self.VIDEOS[:],
            expected_downloaded,
            expected_failed,
            expected_skipped,
        )

    @slow_test
    def test_download_with_skip_download(self, ydl_params: YoutubeDlParams):
        ydl_params.skip_download = True
        expected_downloaded = []
        expected_failed = [self.INVALID_VIDEO]
        expected_skipped = [
            self.VIDEO,
            self.SONG_WITH_LYRICS,
            self.SONG_WITHOUT_LYRICS,
        ]
        self._test_download(
            ydl_params,
            self.VIDEOS[:],
            expected_downloaded,
            expected_failed,
            expected_skipped,
        )

    def _test_download(
        self,
        ydl_params: YoutubeDlParams,
        videos: list[VideoId],
        expected_downloaded: list[VideoId],
        expexted_failed: list[VideoId],
        expected_skipped: list[VideoId],
    ):
        downloader = MusicDownloader(ydl_params=ydl_params)
        res = downloader.download(videos)

        assert videos == res.videos
        assert not res.queue

        def to_video_ids(lst: list):
            return [x.videoId for x in lst]

        got_downloaded = to_video_ids(res.downloaded)
        got_failed = to_video_ids(res.failed)
        got_skipped = to_video_ids(res.skipped)

        assert expected_downloaded == got_downloaded
        assert expexted_failed == got_failed
        assert expected_skipped == got_skipped
