import logging
from concurrent.futures import Future, ThreadPoolExecutor, as_completed

from ytmusicapi import YTMusic

from ytldl2.extractor import ExtractError, Extractor
from ytldl2.models.home_items import HomeItems
from ytldl2.models.raw_artist import RawArtist
from ytldl2.models.raw_home import Home
from ytldl2.models.raw_playlist import RawPlaylist, RawWatchPlaylist
from ytldl2.models.types import ChannelId, PlaylistId
from ytldl2.models.video import Video

logger = logging.getLogger(__name__)


class YtMusicApiError(Exception):
    pass


class YtMusicApi:
    def __init__(self, auth: str, ytm: YTMusic) -> None:
        """
        :param oauth: oauth file,
        """
        self._yt = ytm
        self._extractor = Extractor()

    def get_home_items(self, home_limit: int = 1000) -> HomeItems:
        """
        Gets home items from user's youtube music home page.
        :param home_limit: Amount of items, requested from home items.
        Better to leave default.
        """
        try:
            home_raw: list = self._yt.get_home(limit=home_limit)
            home = Home.parse_obj(home_raw)
            home_items = self._extractor.parse_home(home)
            home_items.remove_dublicates()
            return home_items
        except ExtractError:
            raise
        except Exception as e:
            raise YtMusicApiError() from e

    def get_videos(
        self,
        home_items: HomeItems,
        each_playlist_limit: int,
    ) -> list[Video]:
        """
        Returns all songs from user's youtube music home page.
        :param home_items: Items, that can be got via method get_home_items().
        :param each_playlist_limit: How much songs to get from each playlist.
        """
        try:
            return self._get_videos(home_items, each_playlist_limit)
        except ExtractError:
            raise
        except Exception as e:
            raise YtMusicApiError() from e

    def _get_videos(
        self, home_items: HomeItems, each_playlist_limit: int
    ) -> list[Video]:
        """Helper method for get_songs()"""
        videos: list[Video] = [video for video in home_items.videos]
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures: list[Future[list[Video]]] = []
            if playlists := home_items.playlists:
                for playlist in playlists:
                    futures.append(
                        executor.submit(
                            self.get_videos_from_playlist,
                            playlist.playlist_id,
                            limit=each_playlist_limit,
                        )
                    )
            if channels := home_items.channels:
                for channel in channels:
                    futures.append(
                        executor.submit(
                            self.get_videos_from_channel,
                            channel.channel_id,
                            limit=each_playlist_limit,
                        )
                    )
            for future in as_completed(futures):
                try:
                    videos += future.result()
                except Exception as e:
                    logger.debug(f"skipping playlist, couldn't extract video ids: {e}")
        logger.debug(f"Extracted {len(videos)} videos")
        return videos

    def get_videos_from_playlist(
        self, playlist_id: PlaylistId, /, limit: int = 200
    ) -> list[Video]:
        """
        Extracts videoIds from playlist.
        """
        contents = RawPlaylist | RawWatchPlaylist
        is_watch = False

        try:
            contents = self._yt.get_playlist(
                playlistId=playlist_id,
                limit=limit,  # type: ignore
            )
        except Exception:
            try:
                contents = self._yt.get_watch_playlist(
                    playlistId=playlist_id,
                    limit=limit,  # type: ignore
                )
                is_watch = True
            except Exception:
                raise
        contents = (
            RawWatchPlaylist.parse_obj(contents)
            if is_watch
            else RawPlaylist.parse_obj(contents)
        )
        return self._extractor.extract_videos_from_playlist(contents)

    def get_videos_from_channel(
        self, channel_id: ChannelId, /, limit: int | None = None
    ) -> list[Video]:
        """
        Extracts videoIds from channel.
        """
        raw_artist = self._yt.get_artist(channelId=channel_id)
        artist = RawArtist.parse_obj(raw_artist)
        return self.get_videos_from_playlist(
            self._extractor.extract_playlist_id_from_artist(artist), limit=limit
        )
