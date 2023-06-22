import logging
import pathlib

from yt_dlp import YoutubeDL

from ytldl2.cache import Cache
from ytldl2.killer import CancellationToken
from ytldl2.models import Video
from ytldl2.postprocessors import FilterSongPP, LyricsPP, MetadataPP, RetainMainArtistPP


class Downloader:
    def __init__(
        self,
        cache: Cache,
        logger: logging.Logger | None = None,
        home_dir: pathlib.Path | None = None,
        tmp_dir: pathlib.Path | None = None,
        progress_hooks: list | None = None,
        postprocessor_hooks: list | None = None,
        skip_download: bool = False,
    ) -> None:
        self._cache = cache

        ydl_opts = make_youtube_dl_opts(
            logger=logger,
            home_dir=home_dir,
            tmp_dir=tmp_dir,
            progress_hooks=progress_hooks,
            postprocessor_hooks=postprocessor_hooks,
            skip_download=skip_download,
        )
        self.ydl = make_youtube_dl(ydl_opts=ydl_opts)

    def download_songs(
        self, videos: list[Video], cancellation_token: CancellationToken | None = None
    ) -> pathlib.Path | None:
        """
        Download songs in best quality in current thread.
        Downloads only songs (e.g skips videos).
        """
        for video in videos:
            if cancellation_token and cancellation_token.kill_requested:
                return
            with self.ydl:
                self.ydl.download([video.videoId])


def make_youtube_dl_opts(
    logger: logging.Logger | None = None,
    home_dir: pathlib.Path | None = None,
    tmp_dir: pathlib.Path | None = None,
    progress_hooks: list | None = None,
    postprocessor_hooks: list | None = None,
    skip_download: bool = False,
):
    ydl_opts = {
        "format": "m4a/bestaudio/best",
        # See help(yt_dlp.postprocessor) for a list of available Postprocessors
        "postprocessors": [
            {  # Extract audio using ffmpeg
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            },
        ],
        "outtmpl": "%(artist)s - %(title)s [%(id)s].%(ext)s",
        "paths": {},
        "windowsfilenames": True,
        "skip_download": skip_download,
    }
    if logger:
        ydl_opts["logger"] = logger
    if home_dir:
        ydl_opts["paths"]["home"] = str(home_dir)
    if tmp_dir:
        ydl_opts["paths"]["tmp"] = str(tmp_dir)
    if progress_hooks:
        ydl_opts["progress_hooks"] = progress_hooks
    if postprocessor_hooks:
        ydl_opts["postprocessor_hooks"] = postprocessor_hooks

    return ydl_opts


def make_youtube_dl(ydl_opts: dict | None = None) -> YoutubeDL:
    if not ydl_opts:
        ydl_opts = make_youtube_dl_opts()
    ydl = YoutubeDL(ydl_opts)
    # pre processors
    ydl.add_post_processor(FilterSongPP(), when="pre_process")
    ydl.add_post_processor(RetainMainArtistPP(), when="pre_process")
    # post processors
    ydl.add_post_processor(LyricsPP(), when="post_process")
    ydl.add_post_processor(MetadataPP(), when="post_process")
    return ydl
