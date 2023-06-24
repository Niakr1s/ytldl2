from dataclasses import dataclass
from typing import NewType

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

    def filtered(
        self,
        /,
        incl_videos: list[Title] | None = None,
        incl_playlists: list[Title] | None = None,
        incl_channels: list[Title] | None = None,
    ) -> "HomeItems":
        """
        Filters home items and returns new copy.
        """
        incl_videos = incl_videos or []
        incl_playlists = incl_playlists or []
        incl_channels = incl_channels or []

        return HomeItems(
            [x for x in self.videos if x.title in incl_videos],
            [x for x in self.playlists if x.title in incl_playlists],
            [x for x in self.channels if x.title in incl_channels],
        )
