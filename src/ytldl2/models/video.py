from dataclasses import dataclass

from ytldl2.models.types import Artist, WithTitle, WithVideoId


@dataclass(frozen=True)
class Video(WithTitle, WithVideoId):
    artist: Artist | None = None
