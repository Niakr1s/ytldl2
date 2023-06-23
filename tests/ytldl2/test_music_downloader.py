import logging
import pathlib

from yt_dlp.postprocessor.ffmpeg import FFmpegExtractAudioPP

from ytldl2.music_downloader import MusicYoutubeDlBuilder, YoutubeDlParams
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
