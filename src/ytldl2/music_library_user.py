from typing import Protocol

from ytldl2.models.models import HomeItems, HomeItemsFilter, Video


class MusicLibraryUser(Protocol):
    """User for music library."""

    def review_filter(
        self,
        home_items: HomeItems,
        filter: HomeItemsFilter,
    ) -> HomeItemsFilter:
        """
        Called by library to ask user to review filter.
        :return: Reviewed filter, that is intended to be stored in library config.
        """
        return filter

    def review_videos(self, videos: list[Video]) -> list[Video]:
        return videos


class NoLibraryUser(MusicLibraryUser):
    pass
