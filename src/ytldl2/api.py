from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import cast

from ytmusicapi import YTMusic

from ytldl2.extractor import ExtractError, Extractor
from ytldl2.models import HomeItems, VideoId


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
        home_limit: int = 100,
        each_playlist_limit: int = 50,
    ) -> list[VideoId]:
        """
        Returns all songs from user's youtube music home page.
        :param home_limit: Amount of items, requested from home items. Better to leave default.
        :param each_playlist_limit: How much songs to get from each playlist.
        """
        try:
            home_items = self.get_home_items(home_limit=home_limit)
            video_ids: list[str] = self._get_video_ids_from_home_items(
                home_items, each_playlist_limit
            )
            return cast(list[VideoId], video_ids)
        except ExtractError:
            raise
        except Exception as e:
            raise YtMusicApiError() from e

    def get_home_items(self, home_limit: int = 100) -> HomeItems:
        """
        Gets home items from user's youtube music home page.
        :param home_limit: Amount of items, requested from home items. Better to leave default.
        """
        try:
            home = self._yt.get_home(limit=home_limit)
            return self._extractor.parse_home(home)
        except ExtractError:
            raise
        except Exception as e:
            raise YtMusicApiError() from e

    def _get_video_ids_from_home_items(
        self, home_items: HomeItems, each_playlist_limit: int = 50
    ) -> list[str]:
        """Helper method for get_songs()"""
        video_ids: list[str] = [video.videoId for video in home_items.videos]
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            if playlists := home_items.playlists:
                for playlist in playlists:
                    futures.append(
                        executor.submit(
                            self._get_video_ids_from_playlist,
                            playlist.playlistId,
                            limit=each_playlist_limit,
                        )
                    )
            if channels := home_items.channels:
                for channel in channels:
                    futures.append(
                        executor.submit(
                            self._get_video_ids_from_channel,
                            channel.browseId,
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
