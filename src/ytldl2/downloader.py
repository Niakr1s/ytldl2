import logging
import pathlib

from yt_dlp import YoutubeDL

from ytldl2.cache import Cache
from ytldl2.killer import CancellationToken
from ytldl2.models import Video
from ytldl2.postprocessors import FilterSongPP, LyricsPP, MetadataPP, RetainMainArtistPP


class YoutubeDlParams:
    def __init__(
        self,
        logger: logging.Logger | None = None,
        home_dir: pathlib.Path | None = None,
        tmp_dir: pathlib.Path | None = None,
        progress_hooks: list | None = None,
        postprocessor_hooks: list | None = None,
        skip_download: bool = False,
    ) -> None:
        self.logger = logger
        self.home_dir = home_dir
        self.tmp_dir = tmp_dir
        self.progress_hooks = progress_hooks
        self.postprocessor_hooks = postprocessor_hooks
        self.skip_download = skip_download


class SongYoutubeDlBuilder:
    """
    Class, that builds YoutubeDL, that downloads only songs. So, videos will be skipped.
    Downloaded song will have valid metadata (including lyrics) written.
    """

    def __init__(self, params: YoutubeDlParams) -> None:
        self.params = params

    def build(self) -> YoutubeDL:
        ydl_opts = self._make_youtube_dl_opts()
        ydl = YoutubeDL(ydl_opts)
        # pre processors
        ydl.add_post_processor(FilterSongPP(), when="pre_process")
        ydl.add_post_processor(RetainMainArtistPP(), when="pre_process")
        # post processors
        ydl.add_post_processor(LyricsPP(), when="post_process")
        ydl.add_post_processor(MetadataPP(), when="post_process")
        return ydl

    def _make_youtube_dl_opts(self):
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
            "skip_download": self.params.skip_download,
        }
        if self.params.logger:
            ydl_opts["logger"] = self.params.logger
        if self.params.home_dir:
            ydl_opts["paths"]["home"] = str(self.params.home_dir)
        if self.params.tmp_dir:
            ydl_opts["paths"]["tmp"] = str(self.params.tmp_dir)
        if self.params.progress_hooks:
            ydl_opts["progress_hooks"] = self.params.progress_hooks
        if self.params.postprocessor_hooks:
            ydl_opts["postprocessor_hooks"] = self.params.postprocessor_hooks

        return ydl_opts


class SongDownloader:
    """
    Class, that downloads music from youtube. So, videos will be skipped.
    Downloaded music will be stored with correct metadata and lyrics.
    Uses SongYoutubeDlBuilder internally.
    """

    def __init__(
        self, cache: Cache, youtubedl_params: YoutubeDlParams = YoutubeDlParams()
    ) -> None:
        """
        :param cache: Songs, contained in cache, will be skipped.
        :param youtubedl_params: Params, of which instance of SongYoutubeDlBuilder
        will be created.
        """
        self.cache = cache
        self.ydl = SongYoutubeDlBuilder(youtubedl_params).build()

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
