import logging
import pathlib

from yt_dlp import YoutubeDL

from ytldl2.postprocessors import FilterSongPP, LyricsPP, MetadataPP, RetainMainArtistPP


class YoutubeDlBuilder:
    """
    Class, that builds YoutubeDL, that downloads only music. So, videos will be skipped.
    Downloaded song will have valid metadata (including lyrics) written.
    """

    def __init__(
        self,
        home_dir: pathlib.Path,
        tmp_dir: pathlib.Path,
        proxy: str | None = None,
    ) -> None:
        self.home_dir = home_dir
        self.tmp_dir = tmp_dir
        self.proxy = proxy

    def build(self) -> YoutubeDL:
        ydl_opts = self._make_youtube_dl_opts()
        ydl = YoutubeDL(ydl_opts)  # type: ignore
        # pre processors
        ydl.add_post_processor(FilterSongPP(), when="pre_process")
        ydl.add_post_processor(RetainMainArtistPP(), when="pre_process")
        # post processors
        ydl.add_post_processor(LyricsPP(proxy=self.proxy), when="post_process")
        ydl.add_post_processor(MetadataPP(proxy=self.proxy), when="post_process")
        return ydl

    def _make_youtube_dl_opts(self):
        ydl_opts = {
            "format": "m4a/bestaudio/best",
            # See help(yt_dlp.postprocessor) for a list of available Postprocessors
            "postprocessors": [
                {  # Extract audio using ffmpeg
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                },
            ],
            "outtmpl": "%(artist)s - %(title)s [%(id)s].%(ext)s",
            "paths": {},
            "windowsfilenames": True,
        }
        if self.proxy is not None:
            ydl_opts["proxy"] = self.proxy
        ydl_opts["logger"] = logging.getLogger(__name__ + "." + YoutubeDL.__name__)
        if self.home_dir:
            ydl_opts["paths"]["home"] = str(self.home_dir)
        if self.tmp_dir:
            ydl_opts["paths"]["tmp"] = str(self.tmp_dir)

        return ydl_opts
