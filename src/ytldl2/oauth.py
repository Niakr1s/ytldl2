import json
import pathlib

from ytmusicapi import setup_oauth


def get_oauth(
    oauth_json_path: pathlib.Path = pathlib.Path.home() / ".ytldl2" / "oauth.json",
) -> str:
    """"""
    oauth_json_path.parent.mkdir(parents=True, exist_ok=True)
    if oauth_json_path.exists():
        return oauth_json_path.read_text()
    else:
        return json.dumps(setup_oauth(str(oauth_json_path), open_browser=True))
