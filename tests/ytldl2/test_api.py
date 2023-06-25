import pytest
from ytldl2.api import YtMusicApi
from ytldl2.models.models import ChannelId, HomeItems, PlaylistId

from tests.ytldl2 import marks


class TestYtMusicApi:
    @pytest.fixture()
    def yt_music_api(self, oauth) -> YtMusicApi:
        return YtMusicApi(oauth=oauth)

    @pytest.fixture()
    def home_items(self, yt_music_api: YtMusicApi) -> HomeItems:
        return yt_music_api.get_home_items(home_limit=2)

    @marks.slow_test
    def test_get_home_items(self, home_items):
        assert not home_items.is_empty()

    @marks.slow_test
    def test_get_videos(self, yt_music_api: YtMusicApi, home_items: HomeItems):
        videos = yt_music_api.get_videos(home_items, each_playlist_limit=1)
        assert videos

    @marks.slow_test
    def test_get_videos_from_playlist(self, yt_music_api: YtMusicApi):
        videos = yt_music_api.get_videos_from_playlist(
            PlaylistId("RDTMAK5uy_kset8DisdE7LSD4TNjEVvrKRTmG7a56sY")
        )
        assert videos

    @marks.slow_test
    def test_get_videos_from_channel(self, yt_music_api: YtMusicApi):
        videos = yt_music_api.get_videos_from_channel(
            ChannelId("UCpFgEr3XUXk_8wK8H9Dn6Cg")
        )
        assert videos
        assert videos
