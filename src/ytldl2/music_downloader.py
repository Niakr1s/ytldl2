import logging
import pathlib
from typing import Literal, cast

from yt_dlp import YoutubeDL

from ytldl2.cache import Cache, CachedVideo, SongInfo
from ytldl2.cancellation_tokens import CancellationToken
from ytldl2.download_queue import (
    DownloadQueue,
    DownloadQueueHasUncompleteItem,
    DownloadResult,
    Item,
)
from ytldl2.models.types import VideoId
from ytldl2.postprocessors import (
    FilterSongPP,
    LyricsPP,
    MetadataPP,
    RetainMainArtistPP,
    SongFiltered,
)
from ytldl2.sqlite_cache import SqliteCache


class YoutubeDlParams:
    def __init__(
        self,
        home_dir: pathlib.Path | None = None,
        tmp_dir: pathlib.Path | None = None,
        progress_hooks: list | None = None,
        postprocessor_hooks: list | None = None,
        skip_download: bool = False,
    ) -> None:
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
        self._params = params

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
            "skip_download": self._params.skip_download,
        }
        ydl_opts["logger"] = logging.getLogger(__name__ + "." + YoutubeDL.__name__)
        if self._params.home_dir:
            ydl_opts["paths"]["home"] = str(self._params.home_dir)
        if self._params.tmp_dir:
            ydl_opts["paths"]["tmp"] = str(self._params.tmp_dir)
        if self._params.progress_hooks:
            ydl_opts["progress_hooks"] = self._params.progress_hooks
        if self._params.postprocessor_hooks:
            ydl_opts["postprocessor_hooks"] = self._params.postprocessor_hooks

        return ydl_opts


class MusicDownloader:
    """
    Class, that downloads music from youtube. So, videos will be skipped.
    Downloaded music will be stored with correct metadata and lyrics.
    Uses MusicYoutubeDlBuilder internally.
    """

    def __init__(
        self,
        cache: Cache = SqliteCache(),
        ydl_params: YoutubeDlParams = YoutubeDlParams(),
    ) -> None:
        """
        :param cache: Songs, contained in cache, will be skipped.
        :param youtubedl_params: Params, of which instance of SongYoutubeDlBuilder
        will be created.
        """
        self._cache = cache
        self._ydl_builder = MusicYoutubeDlBuilder(ydl_params)
        self._skip_download = ydl_params.skip_download

        self._current_item: Item | None = None
        """Item, iterated of queue in download() method."""

    def download(
        self, videos: list[VideoId], cancellation_token: CancellationToken | None = None
    ) -> DownloadResult:
        """
        Download songs in best quality in current thread.
        Downloads only songs (e.g skips videos).
        """
        ydl = self._ydl_builder.build()
        ydl.add_progress_hook(self._progress_hook)

        queue = DownloadQueue(videos)
        while True:
            self._current_item = queue.next()
            if not self._current_item:
                break

            if cancellation_token and cancellation_token.kill_requested:
                self._current_item.complete_as_skipped("cancelled")
                continue

            if self._current_item.video_id in self._cache:
                self._current_item.complete_as_skipped("already in cache")
                continue

            info: SongInfo | None = None
            with ydl:
                try:
                    # complete_as_* will be operated in progress_hook method after this
                    raw_info = ydl.extract_info(
                        self._current_item.video_id, download=not self._skip_download
                    )

                    info = self._raw_info_to_info(raw_info)
                    if self._skip_download:
                        self._current_item.complete_as_skipped("skip_download")
                except SongFiltered:
                    self._current_item.complete_as_filtered("not a song")
                except DownloadQueueHasUncompleteItem:
                    raise
                except Exception as e:
                    self._current_item.complete_as_failed(e)
                finally:
                    if info:
                        self._cache.set_info(info)
        self._current_item = None

        res = queue.to_result()
        for item in res.downloaded:
            self._cache.set(CachedVideo(video_id=item.videoId, filtered_reason=None))
        for item in res.filtered:
            self._cache.set(
                CachedVideo(video_id=item.videoId, filtered_reason=item.filtered_reason)
            )
        return res

    class ProgressHookError(Exception):
        pass

    def _progress_hook(self, progress):
        if not self._current_item:
            raise MusicDownloader.ProgressHookError("called on None current_item")
        status = cast(Literal["downloading", "error", "finished"], progress["status"])
        match status:
            case "downloading":
                pass
            case "finished":
                self._current_item.complete_as_downloaded(
                    pathlib.Path(progress["filename"])
                )
            case "error":
                self._current_item.complete_as_failed(
                    MusicDownloader.ProgressHookError(progress)
                )

    @staticmethod
    def _raw_info_to_info(info) -> SongInfo | None:
        try:
            return SongInfo(**info)
        except Exception:
            return None
