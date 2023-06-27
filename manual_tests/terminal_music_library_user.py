import time
from typing import Literal

from ytldl2.models.download_hooks import (
    PostprocessorProgressStarted,
)
from ytldl2.models.types import VideoId
from ytldl2.protocols.music_download_tracker import MusicDownloadTracker
from ytldl2.terminal.music_library_user import TerminalMusicLibraryUser


def postprocessor_loop(tracker: MusicDownloadTracker, preprocessors: list[str]):
    for pp in preprocessors:
        tracker.on_postprocessor_progress(
            PostprocessorProgressStarted(
                postprocessor=pp, status="started", info_dict={}
            )
        )
        time.sleep(1)
        tracker.on_postprocessor_progress(
            PostprocessorProgressStarted(
                postprocessor=pp, status="finished", info_dict={}
            )
        )


def downloader_loop(
    tracker: MusicDownloadTracker,
    video: VideoId,
    typ: Literal["filtered", "skipped", "finished"],
):
    tracker.new(video)
    match typ:
        case "finished":
            total_bytes = 10
            for i in range(total_bytes + 1):
                time.sleep(0.1)
                tracker.on_download_progress(
                    video,
                    f"{VideoId}.m4a",
                    downloaded_bytes=i,
                    total_bytes=total_bytes,
                )
        case "filtered":
            tracker.on_video_filtered(video, "filtered")
        case "skipped":
            tracker.on_video_skipped(video, "skipped")
    tracker.close(video)


def main():
    user = TerminalMusicLibraryUser()
    tracker: MusicDownloadTracker = user.music_download_tracker
    preprocessors = ["Preprocessor 1", "Preprocessor 2"]
    postprocessors = ["Postprocessor 1", "Postprocessor 2", "Postprocessor 3"]

    postprocessor_loop(tracker, preprocessors)
    downloader_loop(tracker, VideoId("video"), "finished")
    postprocessor_loop(tracker, postprocessors)


if __name__ == "__main__":
    main()
