from typing import Literal

HomeItemsKey = Literal["videos", "channels", "playlists"]

HomeItems = dict[HomeItemsKey, list[str]]
"""Value contains id, extracted from:
    'videoId' for video, 'browseId' for channel, 'playlistId' for playlist respectively"""
