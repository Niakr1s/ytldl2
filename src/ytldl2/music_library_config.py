from __future__ import annotations

import json
import logging
import pathlib

import pydantic

from ytldl2.models.home_items import HomeItemsFilter
from ytldl2.models.types import Title

logger = logging.getLogger(__name__)


class MusicLibraryConfig(pydantic.BaseModel):
    @staticmethod
    def default_home_items_filter() -> HomeItemsFilter:
        my_mixes = (f"My Mix {i}" for i in range(1, 7))
        return HomeItemsFilter(
            playlists=[
                Title("Your Likes"),
                Title("Archive Mix"),
                Title("Replay Mix"),
                *[Title(x) for x in ["My Supermix", *my_mixes]],
            ],
            channels=[],
            videos=[],
        )

    config_path: pathlib.Path
    home_items_filter: HomeItemsFilter = pydantic.Field(
        default_factory=default_home_items_filter
    )

    def save(self):
        """Saves config to config_path."""
        with self.config_path.open("w", encoding="utf-8") as file:
            file.write(self.model_dump_json(exclude={"config_path"}, indent=4))

    @staticmethod
    def load(config_path: pathlib.Path) -> MusicLibraryConfig:
        try:
            jsn = json.loads(config_path.read_bytes())
            return MusicLibraryConfig(config_path=config_path, **jsn)
        except FileNotFoundError:
            logger.debug(f"file {config_path} not found, creating new config")
            config = MusicLibraryConfig(config_path=config_path)
            config.save()
            logger.debug(f"created new config at {config_path}")
            return config
