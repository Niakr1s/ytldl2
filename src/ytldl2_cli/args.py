import argparse


def parse_args() -> argparse.Namespace:
    """Returns:
    {!action='lib', !dir='tmp', !password='qwerty', !lib_action='update', !limit=50}
    """

    parser = argparse.ArgumentParser(
        description="Program to download music library from youtube."
    )

    action_parsers = parser.add_subparsers(dest="action", required=True)
    _configure_lib_parser(action_parsers.add_parser("lib"))

    res = parser.parse_args()
    return res


def _configure_lib_parser(lib_parser: argparse.ArgumentParser):
    lib_parser.add_argument("-d", "--dir", help="sets output directory", required=True)
    lib_parser.add_argument(
        "-p", "--password", help="password for oauth data", required=True
    )
    lib_action_parsers = lib_parser.add_subparsers(dest="lib_action", required=True)

    lib_action_update_parser = lib_action_parsers.add_parser("update")
    lib_action_update_parser.add_argument(
        "-l",
        "--limit",
        help="limit of downloaded tracks per playlist or channel",
        default=50,
        type=int,
    )
