from dataclasses import dataclass

from ytldl2.models.types import BrowseId, ChannelId, WithTitle


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
