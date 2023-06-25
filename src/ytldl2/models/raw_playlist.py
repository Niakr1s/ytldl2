from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class Track(BaseModel):
    video_id: str = Field(..., alias="videoId")
    title: str


class RawPlaylist(BaseModel):
    id: str
    title: str
    tracks: List[Track]
