import contextlib
import os
import pathlib
from typing import Generator

import robocrypt


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


def encrypt(smth: str, password: bytes, salt_path: pathlib.Path) -> bytes:
    with robo_salt(salt_path):
        return robocrypt.encrypt(smth.encode(), password)


def decrypt(smth: bytes, password: bytes, salt_path: pathlib.Path) -> str:
    with robo_salt(salt_path):
        return robocrypt.decrypt(smth, password).decode()
