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


def downloader_loop(tracker: MusicDownloadTracker, video: VideoId):
    total_bytes = 10
    for i in range(1, total_bytes + 1):
        time.sleep(0.1)
        tracker.on_download_progress(
            video,
            filename=f"{video}.m4a",
            downloaded_bytes=i,
            total_bytes=total_bytes,
        )


ExpectedResult = Literal["filtered", "skipped", "finished"]


def imitate_music_downloader(
    tracker: MusicDownloadTracker,
    video: VideoId,
    preprocessors: list[str],
    postprocessors: list[str],
    expected_result: ExpectedResult,
):
    tracker.new(video)

    postprocessor_loop(tracker, preprocessors)
    match expected_result:
        case "finished":
            downloader_loop(tracker, video)
            postprocessor_loop(tracker, postprocessors)

    tracker.close(video)


def main():
    user = TerminalMusicLibraryUser()
    tracker = user.progress_bar()

    videos: list[tuple[VideoId, ExpectedResult]] = [
        (VideoId("finished_video1"), "finished"),
        (VideoId("finished_video2"), "finished"),
        (VideoId("skipped_video1"), "skipped"),
        (VideoId("skipped_video2"), "skipped"),
        (VideoId("skipped_video3"), "skipped"),
        (VideoId("filtered_video1"), "filtered"),
        (VideoId("filtered_video2"), "filtered"),
    ]
    for video, expected_result in videos:
        imitate_music_downloader(
            tracker,
            video,
            preprocessors=["Preprocessor1", "Preprocessor2"],
            postprocessors=["Postprocessor1", "Postprocessor2", "Postprocessor3"],
            expected_result=expected_result,
        )


if __name__ == "__main__":
    main()
