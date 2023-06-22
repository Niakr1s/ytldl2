import logging
import pathlib

from yt_dlp.postprocessor.ffmpeg import FFmpegExtractAudioPP

from ytldl2.downloader import make_youtube_dl, make_youtube_dl_opts
from ytldl2.postprocessors import FilterSongPP, LyricsPP, MetadataPP, RetainMainArtistPP


def test_make_youtube_dl_opts__filled():
    logger = logging.Logger("logger")
    home_dir = pathlib.Path("~")
    tmp_dir = pathlib.Path("f:/")
    progress_hooks = ["progress_hook"]
    postprocessor_hooks = ["postprocessor_hook"]
    skip_download = True

    ydl_opts = make_youtube_dl_opts(
        logger=logger,
        home_dir=home_dir,
        tmp_dir=tmp_dir,
        progress_hooks=progress_hooks,
        postprocessor_hooks=postprocessor_hooks,
        skip_download=skip_download,
    )

    assert logger == ydl_opts["logger"]
    assert str(home_dir) == ydl_opts["paths"]["home"]
    assert str(tmp_dir) == ydl_opts["paths"]["tmp"]
    assert progress_hooks == ydl_opts["progress_hooks"]
    assert postprocessor_hooks == ydl_opts["postprocessor_hooks"]
    assert skip_download == ydl_opts["skip_download"]


def test_make_youtube_dl_opts__empty():
    ydl_opts = make_youtube_dl_opts()
    assert "logger" not in ydl_opts
    assert "paths" in ydl_opts
    assert "home" not in ydl_opts["paths"]
    assert "tmp" not in ydl_opts["paths"]
    assert "progress_hooks" not in ydl_opts
    assert "postprocessor_hooks" not in ydl_opts
    assert not ydl_opts["skip_download"]


def test_make_youtube_dl():
    ydl = make_youtube_dl()

    pre_processes = ydl._pps["pre_process"]
    assert len(pre_processes) == 2
    assert isinstance(pre_processes[0], FilterSongPP)
    assert isinstance(pre_processes[1], RetainMainArtistPP)

    post_processes = ydl._pps["post_process"]
    assert len(post_processes) == 3
    assert isinstance(post_processes[0], FFmpegExtractAudioPP)
    assert isinstance(post_processes[1], LyricsPP)
    assert isinstance(post_processes[2], MetadataPP)
