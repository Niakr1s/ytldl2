from dataclasses import dataclass
from typing import NewType, TypeVar

Title = NewType("Title", str)
VideoId = NewType("VideoId", str)
PlaylistId = NewType("PlaylistId", str)
ChannelId = NewType("ChannelId", str)
BrowseId = NewType("BrowseId", str)
Artist = NewType("Artist", str)


@dataclass(frozen=True)
class WithTitle:
    title: Title


@dataclass(frozen=True)
class WithVideoId:
    video_id: VideoId

    @property
    def youtube_url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"

    @property
    def youtube_music_url(self) -> str:
        return f"https://music.youtube.com/watch?v={self.video_id}"


WithVideoIdT = TypeVar("WithVideoIdT", bound=WithVideoId)
