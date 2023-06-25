from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class Track(BaseModel):
    video_id: str = Field(..., alias="videoId")
    title: str


class RawWatchPlaylist(BaseModel):
    tracks: List[Track]
    playlist_id: str = Field(..., alias="playlistId")
