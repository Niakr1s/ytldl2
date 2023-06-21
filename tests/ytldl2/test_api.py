import json

import pytest
from ytmusicapi import YTMusic

from tests.ytldl2 import DATA, OAUTH_PATH, TEST_CONFIG_DIR
from ytldl2 import VideoId
from ytldl2.api import HomeItems, YtMusicApi


@pytest.fixture(scope="session")
def oauth() -> str:
    if OAUTH_PATH.exists():
        return OAUTH_PATH.read_text()
    raise FileNotFoundError(
        f"oauth path {OAUTH_PATH} not found, please run command 'python -m tests.ytldl2' to init it"
    )


@pytest.fixture()
def yt_music_api(oauth, monkeypatch: pytest.MonkeyPatch) -> YtMusicApi:
    def get_home(*args, **kwargs):
        with (DATA / "home.json").open(encoding="utf-8") as file:
            return json.load(file)

    monkeypatch.setattr(YTMusic, "get_home", get_home)
    return YtMusicApi(oauth=oauth)


@pytest.fixture
def home_items(yt_music_api: YtMusicApi) -> HomeItems:
    return yt_music_api.get_home_items()


def test_oauth_works(oauth):
    assert oauth


def test_get_home_items_monkeypatch_works(yt_music_api: YtMusicApi):
    items = yt_music_api.get_home_items()
    assert 3 == len(items)
    assert 1 == len(items["videos"])
    assert 2 == len(items["channels"])
    assert 3 == len(items["playlists"])


def test_get_home_items_exlude_titles_works(yt_music_api: YtMusicApi):
    items = yt_music_api.get_home_items(
        exclude_titles=["Mixed for you", "Listen again"]
    )
    for item in items.values():
        assert not item


def test_get_home_items_exlude_playlists_works(yt_music_api: YtMusicApi):
    items = yt_music_api.get_home_items(
        exclude_playlists=[
            "My Supermix",
            "Your Likes",
            "Suzume no Tojimari Car Playlist",
        ]
    )
    assert not items["playlists"]


def test_extract_video_ids_from_playlist__get_playlist(
    yt_music_api: YtMusicApi, monkeypatch: pytest.MonkeyPatch
):
    def get_playlist(*args, **kwargs):
        with (DATA / "get_playlist.json").open(encoding="utf-8") as file:
            return json.load(file)

    monkeypatch.setattr(YTMusic, "get_playlist", get_playlist)

    res = yt_music_api.extract_video_ids_from_playlist(
        "RDTMAK5uy_kset8DisdE7LSD4TNjEVvrKRTmG7a56sY"
    )
    assert ["9amPGYrVxFA", "OHcFfF3w0Ok"] == res


def test_extract_video_ids_from_playlist__get_watch_playlist(
    yt_music_api: YtMusicApi, monkeypatch: pytest.MonkeyPatch
):
    def get_watch_playlist(*args, **kwargs):
        with (DATA / "get_watch_playlist.json").open(encoding="utf-8") as file:
            return json.load(file)

    monkeypatch.setattr(YTMusic, "get_watch_playlist", get_watch_playlist)

    res = yt_music_api.extract_video_ids_from_playlist("RDAMVMpm9JyMiAU6A")
    assert ["6xZWW8ZQvVs", "mrGYm1djl3A", "T_iLqam_f4E"] == res


def test_extract(yt_music_api: YtMusicApi, monkeypatch: pytest.MonkeyPatch):
    VIDEO_ID = "video_id"
    PLAYLIST_VIDEO_ID = "playlist_video_id"
    CHANNEL_VIDEO_ID = "channel_video_id"

    def extract_video_ids_from_playlist(*args, **kwargs) -> list[VideoId]:
        return [VideoId(PLAYLIST_VIDEO_ID)]

    def extract_video_ids_from_channel(*args, **kwargs) -> list[VideoId]:
        return [VideoId(CHANNEL_VIDEO_ID)]

    monkeypatch.setattr(
        YtMusicApi, "extract_video_ids_from_playlist", extract_video_ids_from_playlist
    )
    monkeypatch.setattr(
        YtMusicApi, "extract_video_ids_from_channel", extract_video_ids_from_channel
    )

    home_items: HomeItems = {
        "videos": [VIDEO_ID],
        "channels": ["channel"] * 2,
        "playlists": ["playlist"] * 3,
    }

    extracted = yt_music_api.extract(home_items=home_items)
    assert 6 == len(extracted)
    assert {VIDEO_ID, PLAYLIST_VIDEO_ID, CHANNEL_VIDEO_ID} == set(extracted)
