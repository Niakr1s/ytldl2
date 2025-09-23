import logging
import pathlib
import tempfile

import ytmusicapi
from dotenv import load_dotenv

from ytldl2 import crypto
from ytldl2.cancellation_tokens import GracefulKiller
from ytldl2.music_downloader import MusicDownloader
from ytldl2.music_library import MusicLibrary
from ytldl2.music_library_config import MusicLibraryConfig
from ytldl2.sqlite_cache import SqliteCache
from ytldl2.terminal.ui import TerminalUi
from ytldl2_cli.args import parse_args

logger = logging.getLogger()


def init_logger(home_dir: pathlib.Path, level: int):
    log_path = home_dir / ".logs" / "main.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=level,
        filename=log_path,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        filemode="w",
        encoding="utf-8",
    )


def init_music_library(home_dir: pathlib.Path, password: str) -> MusicLibrary:
    dot_dir = home_dir / ".ytldl2"
    dot_dir.mkdir(parents=True, exist_ok=True)

    config = MusicLibraryConfig.load(dot_dir / "config.json")
    cache = SqliteCache(dot_dir / "cache.db")

    tmp_dir = pathlib.Path(tempfile.mkdtemp(suffix=".ytldl2_"))
    downloader = MusicDownloader(home_dir, tmp_dir)

    # oauth = Oauth(dot_dir / "oauth", password)
    # oauth = oauth.get_oauth()

    salt_path = home_dir / "salt"
    headers_path = dot_dir / "headers"
    if not headers_path.exists():
        headers = ytmusicapi.setup()
        headers_encoded = crypto.encrypt(headers, password.encode(), salt_path)
        headers_path.write_bytes(headers_encoded)
    else:
        headers_encoded = headers_path.read_bytes()
        headers = crypto.decrypt(headers_encoded, password.encode(), salt_path)

    ui = TerminalUi()

    return MusicLibrary(
        config=config, cache=cache, downloader=downloader, auth=headers, ui=ui
    )


def main():
    load_dotenv()
    args = parse_args()
    log_level = logging.DEBUG if args.debug else logging.INFO

    match args.action:
        case "lib":
            home_dir = pathlib.Path(args.dir)
            init_logger(home_dir, log_level)

            lib = init_music_library(home_dir, args.password)
            logger.info("Music library initiated.")

            match args.lib_action:
                case "update":
                    logger.info("Starting update music library.")
                    lib.update(limit=args.limit, cancellation_token=GracefulKiller())


if __name__ == "__main__":
    main()
