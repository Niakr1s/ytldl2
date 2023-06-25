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


class RawWatchPlaylist(BaseModel):
    tracks: List[Track]
    playlist_id: str = Field(..., alias="playlistId")
