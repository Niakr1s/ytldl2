import pathlib
from dataclasses import dataclass
from typing import NewType

import urllib3

Title = NewType("Title", str)
VideoId = NewType("VideoId", str)
PlaylistId = NewType("PlaylistId", str)
ChannelId = NewType("ChannelId", str)
BrowseId = NewType("BrowseId", str)


@dataclass
class Video:
    """In raw home data, video is entity, that contains "videoId" field."""

    title: Title
    videoId: VideoId

    def is_valid(self) -> bool:
        return bool(self.title) and bool(self.videoId)

    def to_url(self) -> str:
        return f"https://music.youtube.com/watch?v={self.videoId}"


@dataclass
class Playlist:
    """In raw home data, playlist is entity, that contains "playlistId" field."""

    title: Title
    playlistId: PlaylistId

    def is_valid(self) -> bool:
        return bool(self.title) and bool(self.playlistId)

    def to_url(self) -> str:
        return f"https://music.youtube.com/playlist?list={self.playlistId}"


@dataclass
class Channel:
    """In raw home data, channel is entity, that contains "subscribers" and "browseId" fields."""

    title: Title
    channelId: ChannelId
    """Actually, in raw home data, this represents as "browseId"."""

    @property
    def browseId(self) -> BrowseId:
        return BrowseId(self.channelId)

    def is_valid(self) -> bool:
        return bool(self.title) and bool(self.channelId)

    def to_url(self) -> str:
        return f"https://music.youtube.com/browse/{self.browseId}"


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
