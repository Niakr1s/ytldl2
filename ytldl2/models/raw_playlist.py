from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Artist(BaseModel):
    name: str
    id: Optional[str]


class Track(BaseModel):
    video_id: str = Field(..., alias="videoId")
    title: str
    artists: Optional[List[Artist]] = None


class RawPlaylist(BaseModel):
    id: str
    title: str
    tracks: List[Track]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, title={self.title})"


class RawWatchPlaylist(BaseModel):
    playlist_id: str = Field(..., alias="playlistId")
    tracks: List[Track]

    def __str__(self) -> str:
        return f"{self.__class__.__name__} (playlist_id={self.playlist_id})"
