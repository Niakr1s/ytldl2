from typing import Any

from ytldl2 import VideoId
from ytldl2.models import HomeItems


class ExtractError(Exception):
    pass


_BROWSE_ID = "browseId"
_VIDEO_ID = "videoId"
_PLAYLIST_ID = "playlistId"


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
        try:
            return self._parse_home(home, exclude_titles)
        except Exception as e:
            raise ExtractError(f"error occured in {self.parse_home.__name__}") from e

    def _parse_home(
        self, home: list[dict[Any, Any]], exclude_titles: list[str] | None = None
    ) -> HomeItems:
        if exclude_titles:
            home = [item for item in home if item["title"] not in exclude_titles]

        home_items_contents = (
            contents for home_item in home for contents in home_item["contents"]
        )

        res = HomeItems(videos=[], playlists=[], channels=[])

        for home_item in home_items_contents:
            title = home_item["title"]

            # channels
            if "subscribers" in home_item and _BROWSE_ID in home_item:
                browse_id = home_item[_BROWSE_ID]
                print(f"Appending channel {title} with {_BROWSE_ID}: {browse_id}")
                res.channels.append(browse_id)

            # videos
            elif video_id := home_item.get(_VIDEO_ID, None):
                print(f"Appending video {title} with {_VIDEO_ID}: {video_id}")
                res.videos.append(video_id)

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
                    res.playlists.append(playlist_id)
        return res

    def extract_video_ids_from_playlist(self, playlist: dict) -> list[VideoId]:
        """
        Extracts videoIds from playlist.
        :param playlist: Raw playlist dict, got from YtMusic.get_watch_playlist() or YtMusic.get_playlist() call.
        """
        try:
            tracks: list = playlist["tracks"]
            return [track[_VIDEO_ID] for track in tracks]
        except Exception as e:
            raise ExtractError(
                f"error occured in {self.extract_video_ids_from_playlist.__name__}"
            ) from e

    def extract_songs_browse_id_from_artist(self, artist: dict) -> str:
        """
        Extracts browseId from artist.
        :param artist: Raw artist dict, got from YtMusic.get_artist() call.
        """
        try:
            return artist["songs"][_BROWSE_ID]
        except Exception as e:
            raise ExtractError(
                f"error occured in {self.extract_songs_browse_id_from_artist.__name__}"
            ) from e
