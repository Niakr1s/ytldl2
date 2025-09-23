import pytest

from ytldl2.api import YtMusicApi
from ytldl2.models.home_items import HomeItems
from ytldl2.models.types import ChannelId, PlaylistId


class TestYtMusicApi:
    @pytest.fixture()
    def yt_music_api(self, auth) -> YtMusicApi:
        return YtMusicApi(auth=auth)

    @pytest.fixture()
    def home_items(self, yt_music_api: YtMusicApi) -> HomeItems:
        return yt_music_api.get_home_items(home_limit=2)

    @pytest.mark.slow
    def test_get_home_items(self, home_items):
        assert not home_items.is_empty()

    @pytest.mark.slow
    def test_get_videos(self, yt_music_api: YtMusicApi, home_items: HomeItems):
        videos = yt_music_api.get_videos(home_items, each_playlist_limit=1)
        assert videos

    @pytest.mark.slow
    def test_get_videos_from_playlist(self, yt_music_api: YtMusicApi):
        videos = yt_music_api.get_videos_from_playlist(
            PlaylistId("RDTMAK5uy_kset8DisdE7LSD4TNjEVvrKRTmG7a56sY")
        )
        assert videos

    @pytest.mark.slow
    def test_get_videos_from_channel(self, yt_music_api: YtMusicApi):
        videos = yt_music_api.get_videos_from_channel(
            ChannelId("UCpFgEr3XUXk_8wK8H9Dn6Cg")
        )
        assert videos
