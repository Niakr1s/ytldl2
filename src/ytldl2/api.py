from concurrent.futures import Future, ThreadPoolExecutor, as_completed

from ytmusicapi import YTMusic

from ytldl2.extractor import ExtractError, Extractor
from ytldl2.models import ChannelId, HomeItems, PlaylistId, Video


class YtMusicApiError(Exception):
    pass


class YtMusicApi:
    def __init__(self, oauth: str) -> None:
        """
        :param oauth: oauth file,
        """
        self._yt = YTMusic(auth=oauth)
        self._extractor = Extractor()

    def get_home_items(self, home_limit: int = 100) -> HomeItems:
        """
        Gets home items from user's youtube music home page.
        :param home_limit: Amount of items, requested from home items.
        Better to leave default.
        """
        try:
            home = self._yt.get_home(limit=home_limit)
            return self._extractor.parse_home(home)
        except ExtractError:
            raise
        except Exception as e:
            raise YtMusicApiError() from e

    def get_videos(
        self,
        home_items: HomeItems,
        each_playlist_limit: int = 50,
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
        self, home_items: HomeItems, each_playlist_limit: int = 50
    ) -> list[Video]:
        """Helper method for get_songs()"""
        videos: list[Video] = [video for video in home_items.videos]
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures: list[Future[list[Video]]] = []
            if playlists := home_items.playlists:
                for playlist in playlists:
                    futures.append(
                        executor.submit(
                            self.get_videos_from_playlist,
                            playlist.playlistId,
                            limit=each_playlist_limit,
                        )
                    )
            if channels := home_items.channels:
                for channel in channels:
                    futures.append(
                        executor.submit(
                            self.get_videos_from_channel,
                            channel.channelId,
                            limit=each_playlist_limit,
                        )
                    )
            for future in as_completed(futures):
                try:
                    videos += future.result()
                except Exception as e:
                    print(f"skipping playlist, couldn't extract video ids: {e}")
        print(f"Extracted {len(videos)} videos")
        return videos

    def get_videos_from_playlist(
        self, playlist_id: PlaylistId, /, limit: int = 50
    ) -> list[Video]:
        """
        Extracts videoIds from playlist.
        """
        try:
            contents = self._yt.get_playlist(playlistId=playlist_id, limit=limit)
        except Exception:
            contents = self._yt.get_watch_playlist(playlistId=playlist_id, limit=limit)
        return self._extractor.extract_videos_from_playlist(contents)

    def get_videos_from_channel(
        self, channel_id: ChannelId, /, limit: int = 50
    ) -> list[Video]:
        """
        Extracts videoIds from channel.
        """
        artist = self._yt.get_artist(channelId=channel_id)
        return self.get_videos_from_playlist(
            self._extractor.extract_playlist_id_from_artist(artist), limit=limit
        )
