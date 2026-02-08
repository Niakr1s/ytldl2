from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass
from typing import OrderedDict, TypeVar

import pydantic

from ytldl2.models.channel import Channel
from ytldl2.models.playlist import Playlist
from ytldl2.models.types import Title, WithTitle
from ytldl2.models.video import Video

_TitleFilter = list[Title] | None
"""Can be regex also"""


@dataclass
class HomeItemsFilterRe:
    videos: list[re.Pattern]
    playlists: list[re.Pattern]
    channels: list[re.Pattern]


class HomeItemsFilter(pydantic.BaseModel):
    """
    Class, used in HomeItems.filtered() method.
    """

    videos: _TitleFilter = None
    playlists: _TitleFilter = None
    channels: _TitleFilter = None

    def to_re(self):
        videos = [re.compile(f) for f in self.videos or []]
        playlists = [re.compile(f) for f in self.playlists or []]
        channels = [re.compile(f) for f in self.channels or []]

        return HomeItemsFilterRe(videos=videos, playlists=playlists, channels=channels)


@dataclass
class HomeItems:
    videos: list[Video] = dataclasses.field(default_factory=list)
    playlists: list[Playlist] = dataclasses.field(default_factory=list)
    channels: list[Channel] = dataclasses.field(default_factory=list)

    def remove_dublicates(self):
        self.videos = list(OrderedDict.fromkeys(self.videos))
        self.playlists = list(OrderedDict.fromkeys(self.playlists))
        self.channels = list(OrderedDict.fromkeys(self.channels))

    def is_empty(self) -> bool:
        return (
            len(self.videos) == 0
            and len(self.playlists) == 0
            and len(self.channels) == 0
        )

    def filtered(self, filter: HomeItemsFilterRe) -> HomeItems:
        """
        Filters home items and returns new copy.
        """
        return HomeItems(
            videos=self._filter(self.videos, filter.videos),
            playlists=self._filter(self.playlists, filter.playlists),
            channels=self._filter(self.channels, filter.channels),
        )

    def filter(self, filter: HomeItemsFilterRe):
        """Filters home items in place."""
        self.videos = self._filter(self.videos, filter.videos)
        self.playlists = self._filter(self.playlists, filter.playlists)
        self.channels = self._filter(self.channels, filter.channels)

    WithTitleT = TypeVar("WithTitleT", bound=WithTitle)

    @staticmethod
    def _filter(
        items: list[WithTitleT],
        filter: list[re.Pattern],
    ) -> list[WithTitleT]:
        return [x for x in items if any((f for f in filter if f.match(x.title)))]
