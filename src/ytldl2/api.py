from typing import Any, Literal, TypeVar

from ytmusicapi import YTMusic

HomeItemsKey = Literal["videos", "channels", "playlists"]

HomeItems = dict[HomeItemsKey, list[str]]
"""Value contains id, extracted from:
    'videoId' for video, 'browseId' for channel, 'playlistId' for playlist respectively"""


class YtMusicApi:
    _BROWSE_ID = "browseId"
    _VIDEO_ID = "videoId"
    _PLAYLIST_ID = "playlistId"

    def __init__(self, oauth: str) -> None:
        """
        :param oauth: oauth file,
        """
        self._yt = YTMusic(auth=oauth)

    def get_home_items(
        self,
        exclude_titles: list[str] | None = None,
        exclude_playlists: list[str] | None = None,
    ) -> HomeItems:
        """
        Returns home items in format of { videos, playlists, channels },
        that can be put into download function.
        :param filter_titles: Optional. Here you can exclude some items from parsing.
            Example: filter_titles = ['Mixed for you', 'Forgotten favorites']
        """
        home = self._yt.get_home(limit=100)
        if exclude_titles:
            home = [item for item in home if item["title"] not in exclude_titles]
        return self._parse_home(home, exclude_playlists=exclude_playlists)

    def _parse_home(
        self, home: list[dict[Any, Any]], exclude_playlists: list[str] | None = None
    ) -> HomeItems:
        home_items_contents = (
            contents for home_item in home for contents in home_item["contents"]
        )

        res: HomeItems = dict(videos=[], playlists=[], channels=[])

        for home_item in home_items_contents:
            title = home_item["title"]

            # channels
            if "subscribers" in home_item and self._BROWSE_ID in home_item:
                browse_id = home_item[self._BROWSE_ID]
                print(f"Appending channel {title} with {self._BROWSE_ID}: {browse_id}")
                res["channels"].append(browse_id)

            # videos
            elif video_id := home_item.get(self._VIDEO_ID, None):
                print(f"Appending video {title} with {self._VIDEO_ID}: {video_id}")
                res["videos"].append(video_id)

            # playlists
            elif playlist_id := home_item.get(self._PLAYLIST_ID, None):
                if exclude_playlists and title in exclude_playlists:
                    print(
                        f"Skipping playlist {title} with {self._PLAYLIST_ID}: {playlist_id}"
                    )
                else:
                    print(
                        f"Appending playlist {title} with {self._PLAYLIST_ID}: {playlist_id}"
                    )
                    res["playlists"].append(playlist_id)
        return res
