import pydantic
from ytldl2.models.types import VideoId


class SongInfo(pydantic.BaseModel):
    id: VideoId
    title: str
    duration: int
    channel: str | None
    """I'm pretty sure it won't have None, but made optional just in case"""
    artist: str


class VideoInfo(pydantic.BaseModel):
    id: VideoId
    title: str
    duration: int
