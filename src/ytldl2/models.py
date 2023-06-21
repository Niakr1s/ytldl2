from dataclasses import dataclass
from typing import NewType

VideoId = NewType("VideoId", str)
PlaylistId = NewType("PlaylistId", str)
BrowseId = NewType("BrowseId", str)


@dataclass
class Video:
    videoId: VideoId


@dataclass
class Playlist:
    playlistId: PlaylistId


@dataclass
class Channel:
    browseId: BrowseId


@dataclass
class HomeItems:
    videos: list[Video]
    playlists: list[Playlist]
    channels: list[Channel]

    def is_empty(self) -> bool:
        has_any = self.videos or self.playlists or self.channels
        return not has_any
