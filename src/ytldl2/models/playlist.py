from dataclasses import dataclass

from ytldl2.models.types import PlaylistId, WithTitle


@dataclass(frozen=True)
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
