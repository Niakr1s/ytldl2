import logging
import pathlib
import tempfile

from ytldl2.cancellation_tokens import GracefulKiller
from ytldl2.music_downloader import MusicDownloader
from ytldl2.music_library import MusicLibrary
from ytldl2.music_library_config import MusicLibraryConfig
from ytldl2.oauth import Oauth
from ytldl2.sqlite_cache import SqliteCache
from ytldl2.terminal.ui import TerminalUi

from ytldl2_cli.args import parse_args

logger = logging.getLogger()


def init_logger(home_dir: pathlib.Path):
    log_path = home_dir / ".logs" / "main.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
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

    oauth = Oauth(dot_dir / "oauth", password)
    oauth = oauth.get_oauth()

    ui = TerminalUi()

    return MusicLibrary(
        config=config, cache=cache, downloader=downloader, oauth=oauth, ui=ui
    )


def main():
    args = parse_args()

    match args.action:
        case "lib":
            home_dir = pathlib.Path(args.dir)
            init_logger(home_dir)

            lib = init_music_library(home_dir, args.password)
            logger.info("Music library initiated.")

            match args.lib_action:
                case "update":
                    logger.info("Starting update music library.")
                    lib.update(limit=args.limit, cancellation_token=GracefulKiller())


if __name__ == "__main__":
    main()
