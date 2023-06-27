import logging
import pathlib
from typing import TypeGuard

import yt_dlp
from yt_dlp import YoutubeDL

from ytldl2.cancellation_tokens import CancellationToken
from ytldl2.download_queue import DownloadQueue
from ytldl2.models.download_hooks import (
    DownloadProgress,
    PostprocessorProgress,
    is_progress_downloading,
    is_progress_error,
    is_progress_finished,
)
from ytldl2.models.types import VideoId
from ytldl2.postprocessors import (
    FilterSongPP,
    LyricsPP,
    MetadataPP,
    RetainMainArtistPP,
    SongFiltered,
)
from ytldl2.protocols.cache import Cache, CachedVideo, SongInfo
from ytldl2.protocols.music_download_tracker import (
    MusicDownloadTracker,
    NoMusicDownloadTracker,
)


class YoutubeDlParams:
    def __init__(
        self,
        home_dir: pathlib.Path | None = None,
        tmp_dir: pathlib.Path | None = None,
    ) -> None:
        self.home_dir = home_dir
        self.tmp_dir = tmp_dir


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
        }
        ydl_opts["logger"] = logging.getLogger(__name__ + "." + YoutubeDL.__name__)
        if self._params.home_dir:
            ydl_opts["paths"]["home"] = str(self._params.home_dir)
        if self._params.tmp_dir:
            ydl_opts["paths"]["tmp"] = str(self._params.tmp_dir)

        return ydl_opts


class MusicDownloader:
    """
    Class, that downloads music from youtube. So, videos will be skipped.
    Downloaded music will be stored with correct metadata and lyrics.
    Uses MusicYoutubeDlBuilder internally.
    """

    def __init__(
        self,
        cache: Cache,
        ydl_params: YoutubeDlParams,
    ) -> None:
        """
        :param cache: Songs, contained in cache, will be skipped.
        :param youtubedl_params: Params, of which instance of SongYoutubeDlBuilder
        will be created.
        """
        self._cache = cache
        self._ydl_builder = MusicYoutubeDlBuilder(ydl_params)

    def download(
        self,
        videos: list[VideoId],
        limit: int | None = None,
        cancellation_token: CancellationToken | None = None,
        skip_download: bool = False,
        tracker: MusicDownloadTracker | None = None,
    ) -> DownloadQueue:
        """
        Download songs in best quality in current thread.
        Downloads only songs (e.g skips videos).
        """
        return _MusicDownloadExecutor(
            self._cache,
            self._ydl_builder,
            videos,
            limit=limit,
            cancellation_token=cancellation_token,
            skip_download=skip_download,
            tracker=tracker,
        ).download()


class MusicDownloadError(Exception):
    def __init__(self, queue: DownloadQueue) -> None:
        super().__init__()
        self.queue = queue


class _MusicDownloadExecutor:
    """
    Class, internally used by MusicDownloader.
    """

    def __init__(
        self,
        cache: Cache,
        ydl_builder: MusicYoutubeDlBuilder,
        videos: list[VideoId],
        limit: int | None = None,
        cancellation_token: CancellationToken | None = None,
        skip_download: bool = False,
        tracker: MusicDownloadTracker | None = None,
    ) -> None:
        self._cache = cache
        self._ydl = self._init_ydl(ydl_builder)
        self._cancellation_token = cancellation_token
        self._skip_download = skip_download
        self._tracker = tracker if tracker is not None else NoMusicDownloadTracker()

        self._queue = DownloadQueue(videos)
        """
        Don't call self._queue.mark_as* methods directly, use self._mark_as* instead to
        also call self._tracker methods.
        """
        self._limit = limit if limit is not None else len(videos)

    def _init_ydl(
        self,
        ydl_builder: MusicYoutubeDlBuilder,
    ) -> YoutubeDL:
        ydl = ydl_builder.build()
        ydl.add_progress_hook(self._progress_hook)
        ydl.add_postprocessor_hook(self._postprocessor_hook)
        return ydl

    class VideoSkipped(Exception):
        def __init__(self, skip_reason: str) -> None:
            super().__init__()
            self.skip_reason = skip_reason

    def download(
        self,
    ) -> DownloadQueue:
        """
        Download songs in best quality in current thread.
        Downloads only songs (e.g skips videos).
        Should be called only once.
        """
        for video_id in self._queue:
            if self._limit <= 0:
                break
            try:
                self._tracker.new(video_id)
                self._download_video(video_id)
                self._limit -= 1
            except self.VideoSkipped as e:
                self._queue.mark_skipped("cancelled by cancellation token")
                self._tracker.on_video_skipped(video_id, e.skip_reason)
                self._limit -= 1
            except SongFiltered as e:
                filter_reason = str(e)
                self._queue.mark_filtered(filter_reason)
                self._tracker.on_video_filtered(video_id, filter_reason)
            except Exception as e:
                self._dump_queue()
                self._queue.revert()
                raise MusicDownloadError(self._queue) from e
            finally:
                self._tracker.close(video_id)

        self._dump_queue()
        return self._queue

    def _download_video(self, video_id: VideoId) -> None:
        if self._cancellation_token and self._cancellation_token.kill_requested:
            raise self.VideoSkipped("cancellation requested")

        if video_id in self._cache:
            raise self.VideoSkipped("already in cache")

        info: SongInfo | None = None
        with self._ydl:
            try:
                # complete_as_* will be operated in progress_hook method after this
                raw_info = self._ydl.extract_info(
                    video_id, download=not self._skip_download
                )
                info = SongInfo.parse_obj(raw_info)

                if self._skip_download:
                    raise self.VideoSkipped("skip_download")
            finally:
                if info:
                    self._cache.set_info(info)

    def _dump_queue(self):
        for item in self._queue.downloaded:
            self._cache.set(CachedVideo(video_id=item.video_id, filtered_reason=None))
        for item in self._queue.filtered:
            self._cache.set(
                CachedVideo(
                    video_id=item.video_id, filtered_reason=item.filtered_reason
                )
            )

    def _progress_hook(self, progress: DownloadProgress):
        filename = progress["filename"]

        if self._queue_current_not_none_check(current := self._queue.current):
            if is_progress_downloading(progress) or is_progress_finished(progress):
                self._tracker.on_download_progress(
                    current,
                    filename,
                    total_bytes=progress["total_bytes"],
                    downloaded_bytes=progress["downloaded_bytes"],
                )
            if is_progress_finished(progress):
                path = pathlib.Path(filename)
                self._queue.mark_downloaded(path)
        if is_progress_error(progress):
            raise yt_dlp.utils.DownloadError("download error", progress["info_dict"])

    def _postprocessor_hook(self, progress: PostprocessorProgress):
        self._tracker.on_postprocessor_progress(progress)

    @staticmethod
    def _queue_current_not_none_check(current: VideoId | None) -> TypeGuard[VideoId]:
        if not current:
            raise RuntimeError("no current video in queue")
        return True
