import pathlib

import pytest
from yt_dlp.postprocessor.ffmpeg import FFmpegExtractAudioPP
from ytldl2.models.download_result import Downloaded, Error, Filtered
from ytldl2.models.types import VideoId
from ytldl2.music_downloader import (
    MusicDownloader,
    MusicYoutubeDlBuilder,
    YoutubeDlParams,
)
from ytldl2.postprocessors import FilterSongPP, LyricsPP, MetadataPP, RetainMainArtistPP


class TestMusicYoutubeDlBuilder:
    @pytest.mark.slow
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

    @pytest.mark.slow
    def test_download(self, tmp_path):
        expected_errors = {self.INVALID_VIDEO}
        expected_filtered = {self.VIDEO}
        expected_downloaded = {
            self.SONG_WITH_LYRICS,
            self.SONG_WITHOUT_LYRICS,
        }

        downloader = MusicDownloader(tmp_path)

        got_downloaded: set[VideoId] = set()
        got_filtered: set[VideoId] = set()
        got_errors: set[VideoId] = set()

        for res in downloader.download(
            [
                self.INVALID_VIDEO,
                self.SONG_WITH_LYRICS,
                self.SONG_WITHOUT_LYRICS,
                self.VIDEO,
            ]
        ):
            match res:
                case Downloaded():
                    got_downloaded.add(res.video_id)
                case Filtered():
                    got_filtered.add(res.video_id)
                case Error():
                    got_errors.add(res.video_id)

        assert expected_downloaded == got_downloaded
        assert expected_filtered == got_filtered
        assert expected_errors == got_errors
