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

    def extract_songs_browse_id_from_artist(self, artist: dict) -> str:
        """
        Extracts browseId from artist.
        :param artist: Raw artist dict, got from YtMusic.get_artist() call.
        """
        return artist["songs"][_BROWSE_ID]


class YtMusicApiError(Exception):
    pass


class YtMusicApi:
    def __init__(self, oauth: str) -> None:
        """
        :param oauth: oauth file,
        """
        self._yt = YTMusic(auth=oauth)
        self._extractor = Extractor()

    def get_songs(
        self,
        exclude_titles: list[str] | None = None,
        home_limit: int = 100,
        each_playlist_limit: int = 50,
    ) -> list[VideoId]:
        """
        Returns all songs from user's youtube music home page.
        :param exclude_titles: Titles of home items and playlists, that will be excluded.
            Example: exclude_titles=["Mixed for you", "Listen again", "My Supermix", "Your Likes"]
        :param home_limit: Amount of items, requested from home items. Better to leave default.
        :param each_playlist_limit: How much songs to get from each playlist.
        """
        try:
            home_items = self._get_home_items(exclude_titles, home_limit)
            video_ids: list[str] = self._get_video_ids_from_home_items(
                home_items, each_playlist_limit
            )
            return cast(list[VideoId], video_ids)
        except ExtractError:
            raise
        except Exception as e:
            raise YtMusicApiError() from e

    def _get_home_items(
        self, exclude_titles: list[str] | None = None, limit: int = 100
    ) -> HomeItems:
        """Helper method for get_songs()"""
        home = self._yt.get_home(limit=limit)
        return self._extractor.parse_home(home, exclude_titles=exclude_titles)

    def _get_video_ids_from_home_items(
        self, home_items: HomeItems, each_playlist_limit: int = 50
    ) -> list[str]:
        """Helper method for get_songs()"""
        video_ids: list[str] = home_items["videos"]
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            if playlists := home_items["playlists"]:
                for playlist in playlists:
                    futures.append(
                        executor.submit(
                            self._get_video_ids_from_playlist,
                            playlist,
                            limit=each_playlist_limit,
                        )
                    )
            if channels := home_items["channels"]:
                for channel in channels:
                    futures.append(
                        executor.submit(
                            self._get_video_ids_from_channel,
                            channel,
                            limit=each_playlist_limit,
                        )
                    )
            for future in as_completed(futures):
                try:
                    video_ids += future.result()
                except Exception as e:
                    print(f"skipping playlist, couldn't extract video ids: {e}")
        print(f"Extracted {len(video_ids)} videos")
        return video_ids

    def _get_video_ids_from_playlist(
        self, playlist_id: str, /, limit: int = 50
    ) -> list[VideoId]:
        """
        Extracts videoIds from playlist.
        """
        try:
            contents = self._yt.get_playlist(playlistId=playlist_id, limit=limit)
        except Exception:
            contents = self._yt.get_watch_playlist(playlistId=playlist_id, limit=limit)
        return self._extractor.extract_video_ids_from_playlist(contents)

    def _get_video_ids_from_channel(
        self, channel_id: str, /, limit: int = 50
    ) -> list[VideoId]:
        """
        Extracts videoIds from channel.
        """
        artist = self._yt.get_artist(channelId=channel_id)
        return self._get_video_ids_from_playlist(
            self._extractor.extract_songs_browse_id_from_artist(artist), limit=limit
        )
