import json
import pathlib

import pytest
import robocrypt
from ytldl2.oauth import Oauth, robo_salt


def test_get_oauth(tmp_path: pathlib.Path):
    oauth_path = tmp_path / "tmp_oauth"
    contents = '{"contents": "some contents"}'
    oauth_path.write_text(contents)

    oauth = Oauth(oauth_path)
    assert contents == oauth.get_oauth()


def test_get_oauth__empty(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch):
    oauth_path = tmp_path / "tmp_oauth"
    contents = '{"contents": "some contents"}'
    monkeypatch.setattr(
        "ytldl2.oauth.setup_oauth", lambda *args, **kwargs: json.loads(contents)
    )

    oauth = Oauth(oauth_path)
    assert contents == oauth.get_oauth()
    assert contents == oauth_path.read_text()


def test_get_oauth_crypto__empty(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    oauth_path = tmp_path / "tmp_oauth"

    contents = '{"contents": "some contents"}'
    monkeypatch.setattr(
        "ytldl2.oauth.setup_oauth", lambda *args, **kwargs: json.loads(contents)
    )

    oauth = Oauth(oauth_path, "123")
    assert contents == oauth.get_oauth()
    assert oauth.password == b"123"
    assert oauth.robo_salt_path.exists()
    assert oauth_path.exists()

    with pytest.raises(robocrypt.DecryptionError):
        robocrypt.decrypt(oauth.oauth_path.read_bytes(), oauth.password)

    with robo_salt(oauth.robo_salt_path):
        decrypted = robocrypt.decrypt(oauth_path.read_bytes(), oauth.password)
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
