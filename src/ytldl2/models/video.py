from dataclasses import dataclass

from ytldl2.models.types import Artist, WithTitle, WithVideoId


@dataclass
class Video(WithTitle, WithVideoId):
    """
    In raw home data, video is entity, that contains "videoId" field.
    """

    artist: Artist | None = None

    def is_valid(self) -> bool:
        return bool(self.title) and bool(self.videoId)

    @property
    def youtube_music_url(self) -> str:
        return f"https://music.youtube.com/watch?v={self.videoId}"
