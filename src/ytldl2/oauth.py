import contextlib
import json
import os
import pathlib
from typing import Generator

import robocrypt
from ytmusicapi import setup_oauth


def get_oauth(
    oauth_path: pathlib.Path = pathlib.Path.home() / ".ytldl2" / "oauth.json",
    /,
    open_browser: bool = True,
) -> str:
    """
    Gets oauth from oauth file.
    :param oauth_path: Path oauth will be read from. If not exists, it will be created.
    If exists, function will just return it's contents.
    """
    oauth: str
    if oauth_path.exists():
        oauth = oauth_path.read_text()
    else:
        oauth_path.parent.mkdir(parents=True, exist_ok=True)
        oauth = json.dumps(setup_oauth(str(oauth_path), open_browser=open_browser))
        oauth_path.write_text(oauth)
    return oauth


def get_oauth_crypto(
    oauth_path: pathlib.Path,
    robo_salt_path: pathlib.Path,
    password: bytes,
    /,
    open_browser: bool = True,
) -> str:
    """
    Gets oauth from encrypted oauth file.
    :param oauth_path: Path oauth will be read from. If not exists, it will be created.
    If exists, function will just return it's contents.
    """
    with robo_salt(robo_salt_path):
        oauth: str
        if oauth_path.exists():
            decrypted = robocrypt.decrypt(oauth_path.read_bytes(), password)
            oauth = decrypted.decode()
        else:
            oauth = json.dumps(setup_oauth(open_browser=open_browser))
            oauth_path.parent.mkdir(parents=True, exist_ok=True)
            encrypted = robocrypt.encrypt(oauth.encode(encoding="utf-8"), password)
            oauth_path.write_bytes(encrypted)
        return oauth


@contextlib.contextmanager
def robo_salt(
    robo_salt_path: pathlib.Path,
    salt_length: int = 10,
) -> Generator:
    """
    Context manager, that bring salt path into robocrypt context.
    :param robo_salt_path: If not exist - creates it.
    :param length: Salt length.
    Used only for creating robo salt file, if it doesn't exists.
    """
    ROBO_SALT_FILE = "ROBO_SALT_FILE"
    prev_robo_salt_file_env = os.environ[ROBO_SALT_FILE]
    os.environ[ROBO_SALT_FILE] = str(robo_salt_path.absolute().as_posix())
    try:
        if not robo_salt_path.exists():
            robocrypt.generate_salt(salt_length)
        yield
    finally:
        os.environ[ROBO_SALT_FILE] = prev_robo_salt_file_env
