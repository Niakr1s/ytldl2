from io import BytesIO
from typing import Any

import requests
from PIL import Image
from yt_dlp.postprocessor import PostProcessor
from ytmusicapi import YTMusic

from ytldl2.metadata import write_metadata


class LyricsPP(PostProcessor):
    """
    Gets lyrics and adds it to info
    """

    def __init__(self, downloader=None):
        super().__init__(downloader)
        self.yt = YTMusic()

    def run(self, info):
        video_id = info["id"]
        lyrics = self.get_lyrics(video_id) or ""
        if lyrics:
            self.to_screen(f"Got lyrics with len={len(lyrics)}")
        else:
            self.to_screen("Got no lyrics")
        info["lyrics"] = lyrics
        return [], info

    def get_lyrics(self, video_id: str) -> str | None:
        """
        Shouldn't throw invalid key exception
        """

        # type hints for get_watch_playlist are not very correct
        playlist = self.yt.get_watch_playlist(video_id)

        lyrics_browse_id: str | None = playlist.get("lyrics", None)  # type: ignore
        if not lyrics_browse_id:
            return None
        self.write_debug(f"Got lyrics browseId={lyrics_browse_id}")
        return self.yt.get_lyrics(lyrics_browse_id).get("lyrics")




class SongFiltered(Exception):
    pass


class FilterSongPP(PostProcessor):
    """
    Filters out unwanted songs via raising exception.
    Songs hase both "artist" and "title" in info, otherwise it's video.
    Raises SongFiltered whenever not-song videoId was filtered out.
    """

    @staticmethod
    def is_song(info: dict[str, Any]) -> bool:
        return all(k in info for k in ["artist", "title"])

    def run(self, info: dict[str, Any]):
        if not self.is_song(info):
            raise SongFiltered("it's video, not a song", info)
        return [], info
