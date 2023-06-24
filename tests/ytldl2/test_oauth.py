import json
import pathlib

import pytest
import robocrypt
from ytldl2.oauth import get_oauth, get_oauth_crypto, robo_salt


def test_get_oauth(tmp_path: pathlib.Path):
    oauth_path = tmp_path / "tmp_oauth"
    contents = '{"contents": "some contents"}'
    oauth_path.write_text(contents)

    assert contents == get_oauth(oauth_path)


def test_get_oauth__empty(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch):
    oauth_path = tmp_path / "tmp_oauth"
    contents = '{"contents": "some contents"}'
    monkeypatch.setattr(
        "ytldl2.oauth.setup_oauth", lambda *args, **kwargs: json.loads(contents)
    )

    assert contents == get_oauth(oauth_path)
    assert contents == oauth_path.read_text()


def test_get_oauth_crypto__empty(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    oauth_path = tmp_path / "tmp_oauth"
    robo_salt_path = tmp_path / "salt.txt"
    password = b"123"
    contents = '{"contents": "some contents"}'
    monkeypatch.setattr(
        "ytldl2.oauth.setup_oauth", lambda *args, **kwargs: json.loads(contents)
    )

    assert contents == get_oauth_crypto(oauth_path, robo_salt_path, password)
    assert robo_salt_path.exists()
    assert oauth_path.exists()

    with pytest.raises(robocrypt.DecryptionError):
        robocrypt.decrypt(oauth_path.read_bytes(), password)

    with robo_salt(robo_salt_path):
        decrypted = robocrypt.decrypt(oauth_path.read_bytes(), password)
        assert contents == decrypted.decode()


def test_robo_salt(tmp_path: pathlib.Path):
    contents = b"some contents"
    password = b"12345"
    robo_salt_path = tmp_path / "salt.txt"
    with robo_salt(robo_salt_path):
        encrypted = robocrypt.encrypt(contents, password)

    with pytest.raises(robocrypt.DecryptionError):
        robocrypt.decrypt(encrypted, password)

    with robo_salt(robo_salt_path):
        assert contents == robocrypt.decrypt(encrypted, password)
