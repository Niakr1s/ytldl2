import logging
import pathlib

from ytldl2.cancellation_tokens import GracefulKiller
from ytldl2.music_library import MusicLibrary

logger = logging.getLogger()


def main():
    home_dir = pathlib.Path("d:/") / "!YT"
    log_path = home_dir / ".logs" / "main.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.touch()

    logging.basicConfig(level=logging.INFO, filename=log_path)

    cancellation_token = GracefulKiller()
    lib = MusicLibrary(home_dir)
    with lib:
        lib.update(limit=10, cancellation_token=cancellation_token)


if __name__ == "__main__":
    main()
