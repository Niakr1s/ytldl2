import time
from typing import Generator

from yt_dlp import YoutubeDL

from ytldl2.models.download_result import (
    Downloaded,
    DownloadResult,
    Error,
    Filtered,
)
from ytldl2.models.info import SongInfo, VideoInfo
from ytldl2.models.types import VideoId
from ytldl2.postprocessors import (
    SongFiltered,
)
from ytldl2.protocols.ui import (
    ProgressBar,
)
from ytldl2.youtube_dl_builder import YoutubeDlBuilder


class MusicDownloader:
    """
    Class, that downloads music from youtube. So, videos will be skipped.
    Downloaded music will be stored with correct metadata and lyrics.
    Uses MusicYoutubeDlBuilder internally.
    """

    def __init__(self, ytlb: YoutubeDlBuilder) -> None:
        self._ydlb = ytlb

    def download(
        self,
        videos: list[VideoId],
        tracker: ProgressBar | None = None,
    ) -> Generator[DownloadResult, None, None]:
        """
        Download songs in best quality in current thread.
        Downloads only songs (e.g skips videos).
        """
        ydl = self._ydlb.build()
        if tracker is not None:
            ydl.add_progress_hook(tracker.on_download_progress)
            ydl.add_postprocessor_hook(tracker.on_postprocessor_progress)

        DELAY_BETWEEN_DOWNLOADED = 10
        for video_id in videos:
            try:
                if tracker is not None:
                    tracker.new(video_id)
                info = self._download_video(ydl, video_id)
                yield Downloaded(video_id, info)
                time.sleep(DELAY_BETWEEN_DOWNLOADED)
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
        for path in self._ydlb.home_dir.glob("*.part"):
            path.unlink(missing_ok=True)

    def __enter__(self):
        self._clean_home_dir()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._clean_home_dir()
        return False
