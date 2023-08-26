from dataclasses import dataclass

from ytldl2.models.types import VideoId
from ytldl2.protocols.cache import SongInfo


@dataclass
class Downloaded:
    """Download was processed and downloaded. Should be cached."""

    video_id: VideoId
    info: SongInfo


@dataclass
class Filtered:
    """Download was processed and filtered out. Should be cached."""

    video_id: VideoId
    reason: str


@dataclass
class Error:
    """Download wasn't processed due to error. Shouldn't be cached."""

    video_id: VideoId
    error: Exception


DownloadResult = Downloaded | Filtered | Error
