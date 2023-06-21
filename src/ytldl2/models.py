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
        return (
            len(self.videos) == 0
            and len(self.playlists) == 0
            and len(self.channels) == 0
        )
