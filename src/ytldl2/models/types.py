from dataclasses import dataclass
from typing import NewType

Title = NewType("Title", str)
VideoId = NewType("VideoId", str)
PlaylistId = NewType("PlaylistId", str)
ChannelId = NewType("ChannelId", str)
BrowseId = NewType("BrowseId", str)
Artist = NewType("Artist", str)


@dataclass
class WithTitle:
    title: Title


@dataclass
class WithVideoId:
    video_id: VideoId
