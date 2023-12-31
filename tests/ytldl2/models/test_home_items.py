import pytest
from ytldl2.models.channel import Channel
from ytldl2.models.home_items import HomeItems, HomeItemsFilter
from ytldl2.models.playlist import Playlist
from ytldl2.models.types import BrowseId, PlaylistId, Title, VideoId
from ytldl2.models.video import Video


class TestHomeItems:
    VIDEO_TITLES = ["video1", "video2"]
    PLAYLIST_TITLES = ["playlist1", "playlist2"]
    CHANNEL_TITLES = ["channel1", "channel2"]

    @pytest.fixture
    def home_items(self) -> HomeItems:
        return HomeItems(
            videos=[
                Video(
                    video_id=VideoId(str(id)),
                    title=Title(title),
                )
                for id, title in enumerate(self.VIDEO_TITLES)
            ],
            playlists=[
                Playlist(playlist_id=PlaylistId(str(id)), title=Title(title))
                for id, title in enumerate(self.PLAYLIST_TITLES)
            ],
            channels=[
                Channel(browse_id=BrowseId(str(id)), title=Title(title))
                for id, title in enumerate(self.CHANNEL_TITLES)
            ],
        )

    def test_filtered__unknown_titles(self, home_items: HomeItems):
        home_items = home_items.filtered(
            HomeItemsFilter(
                videos=[Title("another video")],
                playlists=[Title("unknown playlist")],
                channels=[Title("unknown channel")],
            )
        )
        assert not home_items.videos
        assert not home_items.playlists
        assert not home_items.channels

    def test_filtered__videos(self, home_items: HomeItems):
        video_title = Title(self.VIDEO_TITLES[0])
        filtered = home_items.filtered(
            HomeItemsFilter(videos=[video_title], playlists=[], channels=[])
        )
        assert len(filtered.videos) == 1
        assert len(filtered.playlists) == 0
        assert len(filtered.channels) == 0
        assert video_title == filtered.videos[0].title

    def test_filtered__playlists(self, home_items: HomeItems):
        playlist_title = Title(self.PLAYLIST_TITLES[0])
        filtered = home_items.filtered(
            HomeItemsFilter(videos=[], playlists=[playlist_title], channels=[])
        )
        assert len(filtered.videos) == 0
        assert len(filtered.playlists) == 1
        assert len(filtered.channels) == 0
        assert playlist_title == filtered.playlists[0].title

    def test_filtered__channels(self, home_items: HomeItems):
        filtered = home_items.filtered(
            HomeItemsFilter(videos=[], playlists=[], channels=None)
        )
        assert len(filtered.videos) == 0
        assert len(filtered.playlists) == 0
        assert len(filtered.channels) == 2

    def test_filtered__videos_None(self, home_items: HomeItems):
        filtered = home_items.filtered(
            HomeItemsFilter(videos=None, playlists=[], channels=[])
        )
        assert len(filtered.videos) == 2
        assert len(filtered.playlists) == 0
        assert len(filtered.channels) == 0

    def test_filtered__playlists_None(self, home_items: HomeItems):
        filtered = home_items.filtered(
            HomeItemsFilter(videos=[], playlists=None, channels=[])
        )
        assert len(filtered.videos) == 0
        assert len(filtered.playlists) == 2
        assert len(filtered.channels) == 0

    def test_filtered__channels_None(self, home_items: HomeItems):
        channel_title = Title(self.CHANNEL_TITLES[0])
        filtered = home_items.filtered(
            HomeItemsFilter(videos=[], playlists=[], channels=[channel_title])
        )
        assert len(filtered.videos) == 0
        assert len(filtered.playlists) == 0
        assert len(filtered.channels) == 1
        assert channel_title == filtered.channels[0].title

    def test_filtered__default_filter(self, home_items: HomeItems):
        filtered = home_items.filtered(HomeItemsFilter())
        assert home_items.videos is not filtered.videos
        assert home_items.playlists is not filtered.playlists
        assert home_items.channels is not filtered.channels
        assert home_items.videos == filtered.videos
        assert home_items.playlists == filtered.playlists
        assert home_items.channels == filtered.channels
