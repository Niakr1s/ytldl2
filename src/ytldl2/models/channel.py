from dataclasses import dataclass

from ytldl2.models.types import BrowseId, ChannelId, WithTitle


@dataclass(frozen=True)
class Channel(WithTitle):
    """
    In raw home data, channel is entity,
    that contains "subscribers" and "browseId" fields
    """

    browse_id: BrowseId
    """Actually, in raw home data, this represents as "browseId"."""

    @property
    def channelId(self) -> ChannelId:
        return ChannelId(self.browse_id)

    def is_valid(self) -> bool:
        return bool(self.title) and bool(self.browse_id)

    @property
    def youtube_music_url(self) -> str:
        return f"https://music.youtube.com/browse/{self.channelId}"
