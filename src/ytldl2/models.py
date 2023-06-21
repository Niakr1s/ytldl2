from dataclasses import dataclass
from typing import Literal

HomeItemsKey = Literal["videos", "channels", "playlists"]


@dataclass
class Video:
    videoId: str


@dataclass
class Playlist:
    playlistId: str


@dataclass
class Channel:
    browseId: str


@dataclass
class HomeItems:
    videos: list[Video]
    playlists: list[Playlist]
    channels: list[Channel]

    def is_empty(self) -> bool:
        has_any = self.videos or self.playlists or self.channels
        return not has_any
