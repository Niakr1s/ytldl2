import json
import pathlib
import tempfile

from pydantic import BaseModel, Field

from ytldl2.music_downloader import MusicDownloader, YoutubeDlParams
from ytldl2.sqlite_cache import SqliteCache


def default_include_playlists() -> list[str]:
    my_mixes = (f"My Mix {i}" for i in range(1, 7))
    return ["My Supermix", *my_mixes]


class MusicLibraryConfig(BaseModel):
    config_path: pathlib.Path
    include_playlists: list[str] = Field(default_factory=default_include_playlists)
    include_channels: list[str] = []

    def save(self):
        """Saves config to config_path."""
        with self.config_path.open("w", encoding="utf-8") as file:
            file.write(self.json(exclude=self._exclude(), indent=4))

    @staticmethod
    def _exclude() -> dict:
        return {"config_path": True}

    @staticmethod
    def load(config_path: pathlib.Path) -> "MusicLibraryConfig":
        try:
            jsn = json.loads(config_path.read_bytes())
            return MusicLibraryConfig(config_path=config_path, **jsn)
        except FileNotFoundError:
            print(f"file {config_path} not found, creating new config")
            config = MusicLibraryConfig(config_path=config_path)
            config.save()
            print(f"created new config at {config_path}")
            return config
