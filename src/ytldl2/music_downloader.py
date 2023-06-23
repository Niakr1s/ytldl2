import logging
import pathlib
from typing import Literal, cast

from yt_dlp import YoutubeDL

from ytldl2.cache import Cache
from ytldl2.download_queue import DownloadQueue, DownloadResult, Item
from ytldl2.killer import CancellationToken
from ytldl2.models import VideoId
from ytldl2.postprocessors import (
    FilterSongPP,
    LyricsPP,
    MetadataPP,
    RetainMainArtistPP,
    SongFiltered,
)


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


class MusicYoutubeDlBuilder:
    """
    Class, that builds YoutubeDL, that downloads only music. So, videos will be skipped.
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


class MusicDownloader:
    """
    Class, that downloads music from youtube. So, videos will be skipped.
    Downloaded music will be stored with correct metadata and lyrics.
    Uses MusicYoutubeDlBuilder internally.
    """

    def __init__(
        self, cache: Cache, ydl_params: YoutubeDlParams = YoutubeDlParams()
    ) -> None:
        """
        :param cache: Songs, contained in cache, will be skipped.
        :param youtubedl_params: Params, of which instance of SongYoutubeDlBuilder
        will be created.
        """
        self._cache = cache
        self._ydl_builder = MusicYoutubeDlBuilder(ydl_params)

    def download(
        self, videos: list[VideoId], cancellation_token: CancellationToken | None = None
    ) -> DownloadResult:
        """
        Download songs in best quality in current thread.
        Downloads only songs (e.g skips videos).
        """
        ydl = self._ydl_builder.build()  # noqa: F841
        queue = DownloadQueue(videos)  # noqa: F841
        current_item: Item | None

        class ProgressHookError(Exception):
            pass

        def progress_hook(progress):
            if not current_item:
                raise ProgressHookError("called on None current_item")
            status = cast(
                Literal["downloading", "error", "finished"], progress["status"]
            )
            match status:
                case "downloading":
                    pass
                case "finished":
                    current_item.complete_as_downloaded(
                        pathlib.Path(progress["filename"])
                    )
                case "error":
                    current_item.complete_as_failed(ProgressHookError(progress))

        ydl.add_progress_hook(progress_hook)

        while current_item := queue.next():
            if cancellation_token and cancellation_token.kill_requested:
                current_item.return_to_queue()
                return queue.to_result()

            with ydl:
                try:
                    ydl.download([current_item.video_id])
                    # complete_as_* will be operated in progress_hook function from now
                except SongFiltered as song_filtered:
                    current_item.complete_as_skipped(str(song_filtered))
                except ProgressHookError as e:
                    current_item.complete_as_failed(e)

        return queue.to_result()
