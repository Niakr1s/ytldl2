import json
import pathlib
import tempfile

import pydantic

from ytldl2.api import YtMusicApi
from ytldl2.cancellation_tokens import CancellationToken
from ytldl2.models.home_items import HomeItemsFilter
from ytldl2.models.song import Song
from ytldl2.models.types import Title
from ytldl2.music_downloader import MusicDownloader, YoutubeDlParams
from ytldl2.music_library_user import MusicLibraryUser, NoLibraryUser
from ytldl2.oauth import get_oauth
from ytldl2.sqlite_cache import SqliteCache


def default_home_items_filter() -> HomeItemsFilter:
    my_mixes = (f"My Mix {i}" for i in range(1, 7))
    return HomeItemsFilter(playlists=[Title(x) for x in ["My Supermix", *my_mixes]])


class MusicLibraryConfig(pydantic.BaseModel):
    config_path: pathlib.Path
    home_items_filter: HomeItemsFilter = pydantic.Field(
        default_factory=default_home_items_filter
    )

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
        user: MusicLibraryUser = NoLibraryUser(),
        skip_download: bool = False,
    ):
        self._user = user
        self._home_dir = home_dir
        self._dot_dir = home_dir / ".ytldl2"
        self._db_path = self._dot_dir / "cache.db"
        self._init_dirs([self._home_dir, self._dot_dir])

        self._config = MusicLibraryConfig.load(self._dot_dir / "config.json")
        self._downloader = self._init_downloader(
            home_dir=home_dir, db_path=self._db_path, skip_download=skip_download
        )

        oauth_json_path = self._dot_dir / "oauth.json"
        self._api = YtMusicApi(get_oauth(oauth_json_path))

    @staticmethod
    def _init_dirs(dirs: list[pathlib.Path]):
        for dir in dirs:
            dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _init_downloader(
        home_dir: pathlib.Path, db_path: pathlib.Path, skip_download: bool
    ) -> MusicDownloader:
        tmp_dir = pathlib.Path(tempfile.mkdtemp(suffix=".ytldl2_"))
        ydl_params = YoutubeDlParams(
            home_dir=home_dir,
            tmp_dir=tmp_dir,
        )

        cache = SqliteCache(db_path)
        return MusicDownloader(cache=cache, ydl_params=ydl_params)

    def update(
        self,
        cancellation_token: CancellationToken = CancellationToken(),
        skip_download: bool = False,
    ):
        """
        Updates library
        """
        home_items = self._api.get_home_items()

        self._config.home_items_filter = self._user.review_filter(
            home_items, self._config.home_items_filter
        )
        self._config.save()
        home_items = home_items.filtered(self._config.home_items_filter)

        videos = self._api.get_videos(home_items=home_items)
        songs = [
            Song(v.video_id, v.title, v.artist) for v in videos if v.artist is not None
        ]
        songs = self._user.review_songs(songs)

        result = self._downloader.download(
            videos=[v.video_id for v in videos],
            cancellation_token=cancellation_token,
            skip_download=skip_download,
        )
        self._user.display_result(result)
