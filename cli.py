import argparse
import logging
import pathlib
import shutil
import tempfile

import ytmusicapi
from dotenv import load_dotenv
from uuid_extensions import uuid7str

from ytldl2 import crypto
from ytldl2.cancellation_tokens import GracefulKiller
from ytldl2.music_library import MusicLibrary
from ytldl2.music_library_config import MusicLibraryConfig
from ytldl2.sqlite_cache import SqliteCache
from ytldl2.terminal.ui import TerminalUi

logger = logging.getLogger()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Program to download music library from youtube."
    )

    parser.add_argument("--debug", action="store_true", help="Logger level flag")
    parser.add_argument("-d", "--dir", help="sets output directory", required=True)
    parser.add_argument(
        "-p", "--password", help="password for oauth data", required=True
    )
    parser.add_argument("--proxy", help="proxy:port", required=False)
    parser.add_argument(
        "-e",
        "--endless",
        action="store_true",
        default=False,
        help="endless mode",
        required=False,
    )
    parser.add_argument(
        "-r",
        "--refresh-headers",
        action="store_true",
        default=False,
        help="Refresh headers on first run",
        required=False,
    )

    res = parser.parse_args()
    return res


def init_logger(home_dir: pathlib.Path, level: int):
    log_path = home_dir / ".logs" / f"ytidl2.{uuid7str()}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=level,
        filename=log_path,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        filemode="w",
        encoding="utf-8",
    )


def check_needed_programs_in_path():
    programs = ["deno", "ffmpeg", "ffprobe"]
    for program in programs:
        if not shutil.which(program):
            raise Exception(
                f"No '{program}' found in PATH, add or install it and run this script again"
            )


def main():
    check_needed_programs_in_path()

    args = parse_args()
    load_dotenv()
    log_level = logging.DEBUG if args.debug else logging.INFO

    home_dir = pathlib.Path(args.dir)
    init_logger(home_dir, log_level)

    dot_dir = home_dir / ".ytldl2"
    dot_dir.mkdir(parents=True, exist_ok=True)

    config = MusicLibraryConfig.load(dot_dir / "config.json")
    cache = SqliteCache(dot_dir / "cache.db")

    cancellation_token = GracefulKiller()

    proxy = args.proxy
    password = args.password

    salt_path = dot_dir / "salt"
    headers_path = dot_dir / "headers"
    if not headers_path.exists() or args.refresh_headers:
        headers = ytmusicapi.setup()
        headers_encoded = crypto.encrypt(headers, password.encode(), salt_path)
        headers_path.write_bytes(headers_encoded)
    else:
        headers_encoded = headers_path.read_bytes()
        headers = crypto.decrypt(headers_encoded, password.encode(), salt_path)

    ui = TerminalUi()

    tmp_dir = pathlib.Path(tempfile.mkdtemp(suffix=".ytldl2_"))
    while not cancellation_token.kill_requested:
        lib = MusicLibrary(
            home_dir=home_dir,
            tmp_dir=tmp_dir,
            config=config,
            cache=cache,
            auth=headers,
            proxy=proxy,
            cancellation_token=cancellation_token,
            ui=ui,
        )
        logger.info("Music library initiated.")

        lib.update(each_playlist_limit=100)
        if not args.endless:
            break


if __name__ == "__main__":
    main()
