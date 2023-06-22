import pathlib

import pytest
from mutagen.mp4 import MP4
from PIL import Image

from tests.ytldl2 import DATA
from ytldl2.metadata import write_metadata


@pytest.fixture
def audio_file(tmp_path: pathlib.Path) -> pathlib.Path:
    audio = DATA / "test_audio_no_tags.m4a"
    copy_to = tmp_path / "audio.m4a"
    copy_to.write_bytes(audio.read_bytes())
    return copy_to


@pytest.fixture
def thumbnail() -> bytes:
    img_path = DATA / "img.jpg"
    return Image.open(str(img_path)).tobytes()


@pytest.fixture
def metadata(thumbnail: bytes) -> dict:
    return dict(
        artist="artist",
        title="title",
        lyrics="lyrics",
        url="url",
        thumbnail=thumbnail,
    )


TAGS = {"©ART", "©nam", "©lyr", "----:com.apple.iTunes:WWW", "covr"}


def test_write_metadata(audio_file: pathlib.Path, metadata: dict):
    write_metadata(str(audio_file), metadata)

    audio = MP4(str(audio_file))
    assert audio.tags
    keys = set(audio.tags.keys())
    want = TAGS
    assert want.issubset(keys)


def test_write_empty_metadata(audio_file: pathlib.Path):
    write_metadata(str(audio_file), {})

    audio = MP4(str(audio_file))
    assert audio.tags
    keys = set(audio.tags.keys())
    not_want = TAGS
    assert len(not_want.intersection(keys)) == 0
