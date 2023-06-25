from dataclasses import dataclass

from ytldl2.models.types import Artist, WithTitle, WithVideoId


@dataclass
class Video(WithTitle, WithVideoId):
    """
    In raw home data, video is entity, that contains "video_id" field.
    """

    artist: Artist | None = None
