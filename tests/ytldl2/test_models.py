import pytest
from ytldl2.models import (
    BrowseId,
    Channel,
    HomeItems,
    Playlist,
    PlaylistId,
    Title,
    Video,
    VideoId,
)


class TestHomeItems:
    VIDEO_TITLES = ["video1", "video2"]
    PLAYLIST_TITLES = ["playlist1", "playlist2"]
    CHANNEL_TITLES = ["channel1", "channel2"]

    @pytest.fixture
    def home_items(self) -> HomeItems:
        return HomeItems(
            videos=[
                Video(videoId=VideoId(str(id)), title=Title(title))
                for id, title in enumerate(self.VIDEO_TITLES)
            ],
            playlists=[
                Playlist(playlistId=PlaylistId(str(id)), title=Title(title))
                for id, title in enumerate(self.PLAYLIST_TITLES)
            ],
            channels=[
                Channel(browseId=BrowseId(str(id)), title=Title(title))
                for id, title in enumerate(self.CHANNEL_TITLES)
            ],
        )

    def test_filtered__empty(self, home_items: HomeItems):
        assert home_items.filtered().is_empty()

    def test_filtered__unknown_titles(self, home_items: HomeItems):
        home_items = home_items.filtered(
            incl_videos=[Title("another video")],
            incl_playlists=[Title("unknown playlist")],
            incl_channels=[Title("unknown channel")],
        )
        assert not home_items.videos
        assert not home_items.playlists
        assert not home_items.channels

    def test_filtered__videos(self, home_items: HomeItems):
        incl = Title(self.VIDEO_TITLES[0])
        filtered = home_items.filtered(incl_videos=[incl])
        assert len(filtered.videos) == 1
        assert len(filtered.playlists) == 0
        assert len(filtered.channels) == 0
        assert incl == filtered.videos[0].title

    def test_filtered__playlists(self, home_items: HomeItems):
        incl = Title(self.PLAYLIST_TITLES[0])
        filtered = home_items.filtered(incl_playlists=[incl])
        assert len(filtered.videos) == 0
        assert len(filtered.playlists) == 1
        assert len(filtered.channels) == 0
        assert incl == filtered.playlists[0].title

    def test_filtered__channels(self, home_items: HomeItems):
        incl = Title(self.CHANNEL_TITLES[0])
        filtered = home_items.filtered(incl_channels=[incl])
        assert len(filtered.videos) == 0
        assert len(filtered.playlists) == 0
        assert len(filtered.channels) == 1
        assert incl == filtered.channels[0].title

    def test_filtered__makes_copy(self, home_items: HomeItems):
        filtered = home_items.filtered()
        assert home_items.videos is not filtered.videos
        assert home_items.playlists is not filtered.playlists
        assert home_items.channels is not filtered.channels
