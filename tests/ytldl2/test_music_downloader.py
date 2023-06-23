import logging
import pathlib

import pytest
from yt_dlp.postprocessor.ffmpeg import FFmpegExtractAudioPP

from ytldl2.models import VideoId
from ytldl2.music_downloader import (
    MusicDownloader,
    MusicYoutubeDlBuilder,
    YoutubeDlParams,
)
from ytldl2.postprocessors import FilterSongPP, LyricsPP, MetadataPP, RetainMainArtistPP


class TestMusicYoutubeDlBuilder:
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

    @pytest.fixture
    def ydl_params(self, tmp_path: pathlib.Path) -> YoutubeDlParams:
        music_tmp_dir = tmp_path / "tmp"
        music_home_dir = tmp_path / "home"
        skip_download = False
        return YoutubeDlParams(
            skip_download=skip_download, home_dir=music_home_dir, tmp_dir=music_tmp_dir
        )

    @pytest.fixture
    def ydl_params_with_skip_download(
        self, ydl_params: YoutubeDlParams
    ) -> YoutubeDlParams:
        ydl_params.skip_download = True
        return ydl_params

    def test_download(self, ydl_params: YoutubeDlParams):
        downloader = MusicDownloader(ydl_params=ydl_params)
        videos = [
            self.INVALID_VIDEO,
            self.SONG_WITH_LYRICS,
            self.SONG_WITHOUT_LYRICS,
            self.VIDEO,
        ]
        res = downloader.download(videos)

        expected_downloads = [  # noqa: F841
            self.SONG_WITH_LYRICS,
            self.SONG_WITHOUT_LYRICS,
        ]
        expected_failed = [self.INVALID_VIDEO]  # noqa: F841
        expected_skipped = [self.VIDEO]  # noqa: F841

        assert videos == res.videos
        assert not res.queue
        assert res.downloaded
        assert res.failed
        assert res.skipped
        # assert expected_downloads == res.downloaded
        # assert expected_failed == res.failed
        # assert expected_skipped == res.skipped
