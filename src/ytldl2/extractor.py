import logging

from ytldl2.models.channel import Channel
from ytldl2.models.home_items import HomeItems
from ytldl2.models.playlist import Playlist
from ytldl2.models.raw_artist import RawArtist
from ytldl2.models.raw_home import Home
from ytldl2.models.raw_playlist import RawPlaylist, RawWatchPlaylist, Track
from ytldl2.models.types import (
    Artist,
    BrowseId,
    PlaylistId,
    Title,
    VideoId,
)
from ytldl2.models.video import Video

logger = logging.getLogger(__name__)


class ExtractError(Exception):
    pass


class Extractor:
    """
    It's a helper class, that helps extract data from raw data, got by YtMusicApi.
    """

    def parse_home(self, home: Home) -> HomeItems:
        """
        Parses home data, got by YtMusic.get_home() call.
        :param home: Home raw data, got by YtMusic.get_home().
        """
        contents = (contents for home_item in home for contents in home_item.contents)

        res = HomeItems(videos=[], playlists=[], channels=[])

        for content in contents:
            title = Title(content.title)

            # channels
            if content.subscribers and (browse_id := content.browse_id):
                logger.debug(f"Appending channel {title} with browseId: {browse_id}")
                res.channels.append(Channel(title=title, browse_id=BrowseId(browse_id)))

            # videos
            elif video_id := content.video_id:
                logger.debug(f"Appending video {title} with videoId: {video_id}")
                artist = Artist(content.artists[0].name) if content.artists else None
                res.videos.append(
                    Video(title=title, artist=artist, video_id=VideoId(video_id))
                )

            # playlists
            elif playlist_id := content.playlist_id:
                logger.debug(
                    f"Appending playlist {title} with playlistId: {playlist_id}"
                )
                res.playlists.append(
                    Playlist(title=title, playlist_id=PlaylistId(playlist_id))
                )
        return res

    def extract_videos_from_playlist(
        self, playlist: RawPlaylist | RawWatchPlaylist
    ) -> list[Video]:
        """
        Extracts videoIds from playlist.
        :param playlist: Raw playlist dict,
        got from YtMusic.get_watch_playlist() or YtMusic.get_playlist() call.
        """
        tracks = playlist.tracks

        def get_artist(track: Track) -> Artist | None:
            return Artist(track.artists[0].name) if track.artists else None

        videos = [
            Video(
                title=Title(track.title),
                artist=get_artist(track),
                video_id=VideoId(track.video_id),
            )
            for track in tracks
        ]
        logger.debug(
            f"Extracted {len(videos)} videos from playlist {playlist}: {videos}"
        )
        return videos

    def extract_playlist_id_from_artist(self, artist: RawArtist) -> PlaylistId:
        """
        Extracts browseId from artist.
        :param artist: Raw artist dict, got from YtMusic.get_artist() call.
        """
        try:
            # it's kinda tricky: songs have "browseId" key, but it actually playlistId
            res = PlaylistId(artist.songs.browse_id)
            logger.debug(f"Extracted playlist id {res} from artist {artist}")
            return res
        except Exception as e:
            raise ExtractError(
                f"error occured in {self.extract_playlist_id_from_artist.__name__}"
            ) from e
