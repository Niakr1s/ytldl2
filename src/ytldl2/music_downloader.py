import logging
import pathlib
from typing import Generator

from yt_dlp import YoutubeDL

from ytldl2.models.download_result import (
    Downloaded,
    DownloadResult,
    Error,
    Filtered,
)
from ytldl2.models.types import VideoId
from ytldl2.postprocessors import (
    FilterSongPP,
    LyricsPP,
    MetadataPP,
    RetainMainArtistPP,
    SongFiltered,
)
from ytldl2.protocols.cache import SongInfo, VideoInfo
from ytldl2.protocols.music_download_tracker import (
    MusicDownloadTracker,
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
        home_dir: pathlib.Path,
        /,
        tmp_dir: pathlib.Path | None = None,
    ) -> None:
        self._home_dir = home_dir
        self._tmp_dir = tmp_dir

    def download(
        self,
        videos: list[VideoId],
        tracker: MusicDownloadTracker | None = None,
    ) -> Generator[DownloadResult, None, None]:
        """
        Download songs in best quality in current thread.
        Downloads only songs (e.g skips videos).
        """
        ydl = MusicYoutubeDlBuilder(
            YoutubeDlParams(home_dir=self._home_dir, tmp_dir=self._tmp_dir)
        ).build()
        if tracker is not None:
            ydl.add_progress_hook(tracker.on_download_progress)
            ydl.add_postprocessor_hook(tracker.on_postprocessor_progress)

        for video_id in videos:
            try:
                if tracker is not None:
                    tracker.new(video_id)
                info = self._download_video(ydl, video_id)
                yield Downloaded(video_id, info)
            except SongFiltered as e:
                yield Filtered(video_id, VideoInfo.parse_obj(e.info), str(e))
            except Exception as e:
                yield Error(video_id, e)
            finally:
                if tracker is not None:
                    tracker.close(video_id)

    def _download_video(self, ydl: YoutubeDL, video_id: VideoId) -> SongInfo:
        with ydl:
            # complete_as_* will be operated in progress_hook method after this
            raw_info = ydl.extract_info(video_id, download=True)
            return SongInfo.parse_obj(raw_info)

    def _clean_home_dir(self):
        """Cleans home directory: removes *.part files."""
        for path in self._home_dir.glob("*.part"):
            path.unlink(missing_ok=True)

    def __enter__(self):
        self._clean_home_dir()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._clean_home_dir()
        return False
