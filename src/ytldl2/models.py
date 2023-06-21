from dataclasses import dataclass
from typing import NewType

Title = NewType("Title", str)
VideoId = NewType("VideoId", str)
PlaylistId = NewType("PlaylistId", str)
BrowseId = NewType("BrowseId", str)


@dataclass
class Video:
    title: Title
    videoId: VideoId

    def is_valid(self) -> bool:
        return bool(self.title) and bool(self.videoId)


@dataclass
class Playlist:
    title: Title
    playlistId: PlaylistId

    def is_valid(self) -> bool:
        return bool(self.title) and bool(self.playlistId)


@dataclass
class Channel:
    title: Title
    browseId: BrowseId

    def is_valid(self) -> bool:
        return bool(self.title) and bool(self.browseId)


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
