import mutagen
from mutagen.mp4 import MP4, AtomDataType, MP4Cover, MP4FreeForm


class UnexpectedFileTypeError(Exception):
    pass


def write_metadata(filepath: str, metadata: dict):
    file: mutagen.FileType = mutagen.File(filepath)  # type: ignore
    if file.tags is None:
        file.add_tags()

    if isinstance(file, MP4):
        if "artist" in metadata:
            file.tags["©ART"] = metadata["artist"]  # type: ignore
        if "title" in metadata:
            file.tags["©nam"] = metadata["title"]  # type: ignore
        if "lyrics" in metadata:
            file.tags["©lyr"] = metadata["lyrics"]  # type: ignore
        if "url" in metadata:
            url: str = metadata.get("url", "")
            file.tags["----:com.apple.iTunes:WWW"] = MP4FreeForm(  # type: ignore
                url.encode("utf-8"), dataformat=AtomDataType.UTF8
            )
        if "thumbnail" in metadata:
            thumbnail = metadata["thumbnail"]
            file["covr"] = [MP4Cover(thumbnail)]
    else:
        raise UnexpectedFileTypeError()

    file.save()
