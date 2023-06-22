import pytest
import requests

from tests.ytldl2 import DATA
from ytldl2.postprocessors import FilterSongPP, LyricsPP, MetadataPP, SongFiltered


class TestLyricsPP:
    VIDEO_ID_WITH_LYRICS = "pm9JyMiAU6A"
    VIDEO_ID_WITHOUT_LYRICS = "5O34Y486wPg"

    @pytest.fixture
    def lyrics_pp(self) -> LyricsPP:
        return LyricsPP()

    def test_get__song_with_lyrics(self, lyrics_pp: LyricsPP):
        assert lyrics_pp.get_lyrics(self.VIDEO_ID_WITH_LYRICS)

    def test_get__song_without_lyrics(self, lyrics_pp: LyricsPP):
        assert not lyrics_pp.get_lyrics(self.VIDEO_ID_WITHOUT_LYRICS)

    def test_run__song_with_lyrics(
        self, lyrics_pp: LyricsPP, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(LyricsPP, "get_lyrics", lambda *_: "lyrics")

        info = {"id": "id"}
        lyrics_pp.run(info)
        assert info["lyrics"]

    def test_run__song_without_lyrics(
        self, lyrics_pp: LyricsPP, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(LyricsPP, "get_lyrics", lambda *_: None)

        info = {"id": "id"}
        lyrics_pp.run(info)
        assert info["lyrics"] == ""


class TestMetadataPP:
    info = {
        "artist": "artist",
        "title": "title",
        "webpage_url": "webpage_url",
        "filepath": "filepath",
        # "lyrics": "lyrics",
        # "thumbnail": "path_to_thumbnail",
    }

    def test_run__valid_info__with_lyrics_strict_false(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        metadata_pp = MetadataPP(with_lyrics_strict=False)
        monkeypatch.setattr(MetadataPP, "write_metadata", lambda *_: ...)
        metadata_pp.run(self.info)

    def test_run__valid_info__with_lyrics_strict_true(self):
        metadata_pp = MetadataPP(with_lyrics_strict=True)
        with pytest.raises(KeyError):
            metadata_pp.run(self.info)

    def test_run__invalid_info(self):
        metadata_pp = MetadataPP()
        info = {}
        with pytest.raises(KeyError):
            metadata_pp.run(info)

    def test_get_image_bytes(self, monkeypatch: pytest.MonkeyPatch):
        res = requests.Response()
        res._content = (DATA / "img.jpg").read_bytes()

        monkeypatch.setattr("ytldl2.postprocessors.requests.get", lambda *_: res)
        assert MetadataPP().get_image_bytes("url")


class TestFilterSongPP:
    @pytest.fixture
    def filter_song_pp(self) -> FilterSongPP:
        return FilterSongPP()

    def test_run__is_song(self, filter_song_pp: FilterSongPP):
        info = {"artist": "artist", "title": "title"}
        filter_song_pp.run(info)

    def test_run__is_not_song(self, filter_song_pp: FilterSongPP):
        info = {"title": "title"}
        with pytest.raises(SongFiltered):
            filter_song_pp.run(info)
