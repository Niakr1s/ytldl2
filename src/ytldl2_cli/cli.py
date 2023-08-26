import logging
import pathlib

from robocrypt.library import DecryptionError
from ytldl2.cancellation_tokens import GracefulKiller
from ytldl2.music_library import MusicLibrary
from ytldl2.terminal.music_library_user import TerminalMusicLibraryUser

from ytldl2_cli.args import parse_args

logger = logging.getLogger()


def main():
    args = parse_args()

    match args.action:
        case "lib":
            home_dir = pathlib.Path(args.dir)
            log_path = home_dir / ".logs" / "main.log"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            logging.basicConfig(level=logging.INFO, filename=log_path)

            match args.lib_action:
                case "update":
                    cancellation_token = GracefulKiller()
                    user = TerminalMusicLibraryUser()
                    try:
                        lib = MusicLibrary(
                            home_dir,
                            user=user,
                            password=args.password,
                        )
                        with lib:
                            lib.update(
                                limit=args.limit, cancellation_token=cancellation_token
                            )
                    except DecryptionError:
                        print("Error: Couldn't decrypt oauth file.")


if __name__ == "__main__":
    main()
