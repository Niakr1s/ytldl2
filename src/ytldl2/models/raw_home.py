from __future__ import annotations

import logging
from typing import Iterator, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Thumbnail(BaseModel):
    url: str
    width: int
    height: int


class Artist(BaseModel):
    name: str
    id: Optional[str]


class AuthorItem(BaseModel):
    name: str
    id: str


class Album(BaseModel):
    name: str
    id: str


class Content(BaseModel):
    title: str
    playlist_id: Optional[Optional[str]] = Field(None, alias="playlistId")
    thumbnails: List[Thumbnail]
    description: Optional[str] = None
    browse_id: Optional[str] = Field(None, alias="browseId")
    subscribers: Optional[str] = None
    video_id: Optional[str] = Field(None, alias="videoId")
    artists: Optional[List[Artist]] = None
    views: Optional[str] = None
    year: Optional[str] = None
    is_explicit: Optional[bool] = Field(None, alias="isExplicit")
    count: Optional[str] = None
    author: Optional[List[AuthorItem]] = None
    album: Optional[Album] = None


class HomeItem(BaseModel):
    title: str
    contents: List[Content]


class Home(BaseModel):
    root: List[HomeItem]

    def parse_obj(obj: list) -> Home:
        root = []
        for raw_home_item in obj:
            try:
                home_item = HomeItem.parse_obj(raw_home_item)
                root.append(home_item)
            except Exception as e:
                logger.error(e)
        return Home(root=root)

    def __iter__(self) -> Iterator[HomeItem]:
        return iter(self.root)

    def __getitem__(self, item) -> HomeItem:
        return self.root[item]
