import json
import pathlib
import tempfile

from pydantic import BaseModel, Field

from ytldl2.api import YtMusicApi
from ytldl2.cancellation_tokens import CancellationToken
from ytldl2.models import Title
from ytldl2.music_downloader import MusicDownloader, YoutubeDlParams
from ytldl2.oauth import get_oauth
from ytldl2.sqlite_cache import SqliteCache


def default_include_playlists() -> list[Title]:
    my_mixes = (f"My Mix {i}" for i in range(1, 7))
    return [Title(x) for x in ["My Supermix", *my_mixes]]


class MusicLibraryConfig(BaseModel):
    config_path: pathlib.Path
    include_playlists: list[Title] = Field(default_factory=default_include_playlists)
    include_channels: list[Title] = []

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


class MusicLibrary:
    def __init__(
        self,
        home_dir: pathlib.Path,
        skip_download: bool = False,
    ):
        self.home_dir = home_dir
        self.dot_dir = home_dir / ".ytldl2"
        self._init_dirs([self.home_dir, self.dot_dir])

        self.config = MusicLibraryConfig.load(self.dot_dir / "config.json")
        self._downloader = self._init_downloader(
            home_dir=home_dir, skip_download=skip_download
        )

        oauth_json_path = self.dot_dir / "oauth.json"
        self._api = YtMusicApi(get_oauth(oauth_json_path))

    @staticmethod
    def _init_dirs(dirs: list[pathlib.Path]):
        for dir in dirs:
            dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _init_downloader(
        home_dir: pathlib.Path, skip_download: bool
    ) -> MusicDownloader:
        tmp_dir = pathlib.Path(tempfile.mkdtemp(suffix=".ytldl2_"))
        ydl_params = YoutubeDlParams(
            home_dir=home_dir,
            tmp_dir=tmp_dir,
            skip_download=skip_download,
        )

        cache = SqliteCache(home_dir / "cache.db")
        return MusicDownloader(cache=cache, ydl_params=ydl_params)

    def update(self, cancellation_token: CancellationToken = CancellationToken()):
        """
        Updates library
        """
        home_items = self._api.get_home_items()
        home_items = home_items.filtered(
            incl_videos=None,
            incl_playlists=self.config.include_playlists,
            incl_channels=self.config.include_channels,
        )

        videos = self._api.get_videos(home_items=home_items)
        result = self._downloader.download(
            videos=[v.videoId for v in videos], cancellation_token=cancellation_token
        )
        print(result)
