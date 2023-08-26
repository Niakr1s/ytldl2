import pathlib


def init_dirs(dirs: list[pathlib.Path]):
    for dir in dirs:
        dir.mkdir(parents=True, exist_ok=True)
