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


class MetadataPP(PostProcessor):
    """
    Sets metadata to file: artist, title, lyrics, url.
    If info doesn't contain "artist", "title", "webpage_url", raises KeyError.
    Should be run after LyricsPP, othervise will raise KeyError.
    Raises UnexpectedFileTypeError, if file is not MP4
    """

    def __init__(self, with_lyrics_strict: bool = True, downloader=None):
        """
        :param with_lyrics_strict: If set to True, raises KeyError at run() method,
        if "lyrics" not in info.
        Adding LyricsPP as postprocessor before MetadataPP
        will propagate "lyrics" key.
        """
        super().__init__(downloader)
        self._with_lyrics_strict = with_lyrics_strict

    def run(self, info: dict[str, Any]):
        if self._with_lyrics_strict and "lyrics" not in info:
            raise KeyError("'lyrics'")
        lyrics: str = info.get("lyrics", "")

        metadata = dict(
            artist=info["artist"],
            title=info["title"],
            url=info["webpage_url"],
            lyrics=lyrics,
            thumbnail=None,
        )

        THUMBNAIL = "thumbnail"
        thumbnail = info.get(THUMBNAIL)
        if thumbnail:
            metadata[THUMBNAIL] = self.get_image_bytes(thumbnail)

        filepath = info["filepath"]
        self.write_metadata(filepath, metadata)

        return [], info

    def write_metadata(self, filepath: str, metadata):
        self.write_debug(f"Starting to write metadata to {filepath}")
        write_metadata(filepath, metadata)
        self.to_screen(f"Wrote metadata to {filepath}")

    def get_image_bytes(self, url: str, format: str = "png") -> bytes:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img_jpg = BytesIO()
        img.save(img_jpg, format=format)
        return img_jpg.getvalue()


class SongFiltered(Exception):
    def __init__(self, message: str, info: dict[str, Any]):
        super().__init__(message)
        self.info = info


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


class RetainMainArtistPP(PostProcessor):
    """
    Info "artist" tag, in case if there are multiple artists, holds value in format:
    'artist': 'Nightwish, Tuomas Holopainen'.
    This postprocessor removes everything after first comma, remaining only main artist.
    If "artist" is None, does nothing.
    """

    @staticmethod
    def retain_main_artist(artist: str) -> str:
        comma_index = artist.find(",")
        if comma_index == -1:
            return artist
        return artist[:comma_index]

    def run(self, info: dict[str, Any]):
        artist: str | None = info.get("artist")
        if artist:
            info["artist"] = self.retain_main_artist(artist)
        return [], info
