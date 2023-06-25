from __future__ import annotations

from pydantic import BaseModel, Field


class Songs(BaseModel):
    browse_id: str = Field(..., alias="browseId")


class RawArtist(BaseModel):
    description: str
    views: str
    name: str
    channel_id: str = Field(..., alias="channelId")
    subscribers: str
    subscribed: bool
    songs: Songs
