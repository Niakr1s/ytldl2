import dataclasses
from dataclasses import dataclass
from typing import Literal, NewType, TypeVar

import pydantic

Title = NewType("Title", str)
VideoId = NewType("VideoId", str)
PlaylistId = NewType("PlaylistId", str)
ChannelId = NewType("ChannelId", str)
BrowseId = NewType("BrowseId", str)


@dataclass
class WithVideoId:
    videoId: VideoId


@dataclass
class WithTitle:
    title: Title


@dataclass
class Video(WithTitle, WithVideoId):
    """
    In raw home data, video is entity, that contains "videoId" field.
    """

    def is_valid(self) -> bool:
        return bool(self.title) and bool(self.videoId)

    @property
    def youtube_music_url(self) -> str:
        return f"https://music.youtube.com/watch?v={self.videoId}"


@dataclass
class Playlist(WithTitle):
    """
    In raw home data, playlist is entity,
    that contains "playlistId" field.
    """

    playlistId: PlaylistId

    def is_valid(self) -> bool:
        return bool(self.title) and bool(self.playlistId)

    @property
    def youtube_music_url(self) -> str:
        return f"https://music.youtube.com/playlist?list={self.playlistId}"


@dataclass
class Channel(WithTitle):
    """
    In raw home data, channel is entity,
    that contains "subscribers" and "browseId" fields
    """

    browseId: BrowseId
    """Actually, in raw home data, this represents as "browseId"."""

    @property
    def channelId(self) -> ChannelId:
        return ChannelId(self.browseId)

    def is_valid(self) -> bool:
        return bool(self.title) and bool(self.browseId)

    @property
    def youtube_music_url(self) -> str:
        return f"https://music.youtube.com/browse/{self.channelId}"


_TitleFilter = list[Title] | Literal["retain_all"]


class HomeItemsFilter(pydantic.BaseModel):
    """
    Class, used in HomeItems.filtered() method.
    """

    videos: _TitleFilter = "retain_all"
    playlists: _TitleFilter = "retain_all"
    channels: _TitleFilter = "retain_all"


@dataclass
class HomeItems:
    videos: list[Video] = dataclasses.field(default_factory=list)
    playlists: list[Playlist] = dataclasses.field(default_factory=list)
    channels: list[Channel] = dataclasses.field(default_factory=list)

    def is_empty(self) -> bool:
        return (
            len(self.videos) == 0
            and len(self.playlists) == 0
            and len(self.channels) == 0
        )

    def filtered(self, filter: HomeItemsFilter) -> "HomeItems":
        """
        Filters home items and returns new copy.
        """
        return HomeItems(
            videos=self._filter(self.videos, filter.videos),
            playlists=self._filter(self.playlists, filter.playlists),
            channels=self._filter(self.channels, filter.channels),
        )

    WithTitleT = TypeVar("WithTitleT", bound=WithTitle)

    @staticmethod
    def _filter(
        items: list[WithTitleT],
        filter: _TitleFilter,
    ) -> list[WithTitleT]:
        if filter == "retain_all":
            return items[:]
        return [x for x in items if x.title in filter]
