from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Literal, cast

from ytmusicapi import YTMusic

from ytldl2 import VideoId

_BROWSE_ID = "browseId"
_VIDEO_ID = "videoId"
_PLAYLIST_ID = "playlistId"

HomeItemsKey = Literal["videos", "channels", "playlists"]

HomeItems = dict[HomeItemsKey, list[str]]
"""Value contains id, extracted from:
    'videoId' for video, 'browseId' for channel, 'playlistId' for playlist respectively"""


class ExtractError(Exception):
    pass


class Extractor:
    """
    It's a helper class, that helps extract data from raw data, got by YtMusicApi.
    """

    def parse_home(
        self, home: list[dict[Any, Any]], exclude_titles: list[str] | None = None
    ) -> HomeItems:
        """
        Parses home data, got by YtMusic.get_home() call.
        :param home: Home raw data, got by YtMusic.get_home().
        :param exclude_titles: See YtMusicApi.get_home_items() doc.
        """
        if exclude_titles:
            home = [item for item in home if item["title"] not in exclude_titles]

        home_items_contents = (
            contents for home_item in home for contents in home_item["contents"]
        )

        res: HomeItems = dict(videos=[], playlists=[], channels=[])

        for home_item in home_items_contents:
            title = home_item["title"]

            # channels
            if "subscribers" in home_item and _BROWSE_ID in home_item:
                browse_id = home_item[_BROWSE_ID]
                print(f"Appending channel {title} with {_BROWSE_ID}: {browse_id}")
                res["channels"].append(browse_id)

            # videos
            elif video_id := home_item.get(_VIDEO_ID, None):
                print(f"Appending video {title} with {_VIDEO_ID}: {video_id}")
                res["videos"].append(video_id)

            # playlists
            elif playlist_id := home_item.get(_PLAYLIST_ID, None):
                if exclude_titles and title in exclude_titles:
                    print(
                        f"Skipping playlist {title} with {_PLAYLIST_ID}: {playlist_id}"
                    )
                else:
                    print(
                        f"Appending playlist {title} with {_PLAYLIST_ID}: {playlist_id}"
                    )
                    res["playlists"].append(playlist_id)
        return res

    def extract_video_ids_from_playlist(self, playlist: dict) -> list[VideoId]:
        """
        Extracts videoIds from playlist.
        :param playlist: Raw playlist dict, got from YtMusic.get_watch_playlist() or YtMusic.get_playlist() call.
        """
        tracks: list = playlist["tracks"]
        return [track[_VIDEO_ID] for track in tracks]


class YtMusicApi:
    def __init__(self, oauth: str) -> None:
        """
        :param oauth: oauth file,
        """
        self._yt = YTMusic(auth=oauth)
        self._extractor = Extractor()

    def get_home_items(
        self,
        exclude_titles: list[str] | None = None,
    ) -> HomeItems:
        """
        Returns home items in format of { videos, playlists, channels },
        that can be put into download function.
        :param exclude_titles: Titles of home items and playlists, that will be excluded.
            Example: exclude_titles=["Mixed for you", "Listen again", "My Supermix", "Your Likes"]
        """
        home = self._yt.get_home(limit=100)
        return self._extractor.parse_home(home, exclude_titles=exclude_titles)

    def extract(self, home_items: HomeItems, limit: int = 50) -> list[VideoId]:
        """
        Extracts video_ids from home items, got from YtMusicApi.get_home_items() call.
        """
        video_ids: list[str] = home_items["videos"]

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            if playlists := home_items["playlists"]:
                for playlist in playlists:
                    futures.append(
                        executor.submit(
                            self.extract_video_ids_from_playlist, playlist, limit=limit
                        )
                    )
            if channels := home_items["channels"]:
                for channel in channels:
                    futures.append(
                        executor.submit(
                            self.extract_video_ids_from_channel, channel, limit=limit
                        )
                    )
            for future in as_completed(futures):
                try:
                    video_ids += future.result()
                except Exception as e:
                    print(f"skipping playlist, couldn't extract video ids: {e}")
        print(f"Extracted {len(video_ids)} videos")
        return cast(list[VideoId], video_ids)

    def extract_video_ids_from_playlist(
        self, playlist_id: str, /, limit: int = 50
    ) -> list[VideoId]:
        """
        Extracts videoIds from playlist.
        """
        try:
            contents = self._yt.get_playlist(playlistId=playlist_id, limit=limit)
        except Exception:
            try:
                contents = self._yt.get_watch_playlist(
                    playlistId=playlist_id, limit=limit
                )
            except Exception as e:
                raise ExtractError(
                    f"couldn't get songs from playlist {playlist_id}"
                ) from e
        return self._extractor.extract_video_ids_from_playlist(contents)

    def extract_video_ids_from_channel(
        self, channel_id: str, /, limit: int = 50
    ) -> list[VideoId]:
        """
        Extracts videoIds from channel.
        """
        try:
            artist = self._yt.get_artist(channelId=channel_id)
        except Exception as e:
            raise ExtractError(f"couldn't get channel's {channel_id} artist") from e

        return self.extract_video_ids_from_playlist(
            artist["songs"][_BROWSE_ID], limit=limit
        )