import json

import pytest
from ytmusicapi import YTMusic

from tests.ytldl2 import DATA, OAUTH_PATH, TEST_CONFIG_DIR
from ytldl2.api import YtMusicApi


@pytest.fixture(scope="session")
def oauth() -> str:
    if OAUTH_PATH.exists():
        return OAUTH_PATH.read_text()
    raise FileNotFoundError(
        f"oauth path {OAUTH_PATH} not found, please run command 'python -m tests.ytldl2' to init it"
    )


@pytest.fixture
def home():
    """
    It's mock home items, returned from YTMusic.get_home() method.
    """
    home_filepath = DATA / "home.json"
    with home_filepath.open(encoding="utf-8") as file:
        return json.load(file)


@pytest.fixture()
def yt_music_api(oauth, home, monkeypatch: pytest.MonkeyPatch):
    def get_home(*args, **kwargs):
        return home

    monkeypatch.setattr(YTMusic, "get_home", get_home)
    return YtMusicApi(oauth=oauth)


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
