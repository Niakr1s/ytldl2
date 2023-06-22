import pytest

from ytldl2.postprocessors import LyricsPP


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
