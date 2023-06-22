from typing import Any, cast

from ytldl2.models import (
    BrowseId,
    Channel,
    ChannelId,
    HomeItems,
    Playlist,
    PlaylistId,
    Title,
    Video,
    VideoId,
)


class ExtractError(Exception):
    pass


_BROWSE_ID = "browseId"
_VIDEO_ID = "videoId"
_PLAYLIST_ID = "playlistId"


class Extractor:
    """
    It's a helper class, that helps extract data from raw data, got by YtMusicApi.
    """

    def parse_home(self, home: list[dict[Any, Any]]) -> HomeItems:
        """
        Parses home data, got by YtMusic.get_home() call.
        :param home: Home raw data, got by YtMusic.get_home().
        """
        try:
            return self._parse_home(home)
        except Exception as e:
            raise ExtractError(f"error occured in {self.parse_home.__name__}") from e

    def _parse_home(self, home: list[dict[Any, Any]]) -> HomeItems:
        home_items_contents = (
            contents for home_item in home for contents in home_item["contents"]
        )

        res = HomeItems(videos=[], playlists=[], channels=[])

        for home_item in home_items_contents:
            title = Title(home_item["title"])

            # channels
            if "subscribers" in home_item and _BROWSE_ID in home_item:
                browse_id = cast(str, home_item[_BROWSE_ID])
                print(f"Appending channel {title} with {_BROWSE_ID}: {browse_id}")
                res.channels.append(Channel(title=title, browseId=BrowseId(browse_id)))

            # videos
            elif video_id := cast(str, home_item.get(_VIDEO_ID, None)):
                print(f"Appending video {title} with {_VIDEO_ID}: {video_id}")
                res.videos.append(Video(title=title, videoId=VideoId(video_id)))

            # playlists
            elif playlist_id := cast(str, home_item.get(_PLAYLIST_ID, None)):
                print(f"Appending playlist {title} with {_PLAYLIST_ID}: {playlist_id}")
                res.playlists.append(
                    Playlist(title=title, playlistId=PlaylistId(playlist_id))
                )
        return res

    def extract_videos_from_playlist(self, playlist: dict) -> list[Video]:
        """
        Extracts videoIds from playlist.
        :param playlist: Raw playlist dict, got from YtMusic.get_watch_playlist() or YtMusic.get_playlist() call.
        """
        try:
            tracks: list = playlist["tracks"]
            return [
                Video(title=track["title"], videoId=VideoId(track[_VIDEO_ID]))
                for track in tracks
            ]
        except Exception as e:
            raise ExtractError(
                f"error occured in {self.extract_videos_from_playlist.__name__}"
            ) from e

    def extract_playlist_id_from_artist(self, artist: dict) -> PlaylistId:
        """
        Extracts browseId from artist.
        :param artist: Raw artist dict, got from YtMusic.get_artist() call.
        """
        try:
            # it's kinda tricky: songs have "browseId" key, but it actually playlistId key
            return artist["songs"][_BROWSE_ID]
        except Exception as e:
            raise ExtractError(
                f"error occured in {self.extract_playlist_id_from_artist.__name__}"
            ) from e
