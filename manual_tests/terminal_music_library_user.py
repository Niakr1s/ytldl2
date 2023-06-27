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
    total_bytes = 1_000_000
    for i in range(1000, 1_000_000, 100_000):
        if i >= total_bytes:
            break
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
        case "filtered":
            tracker.on_video_filtered(video, "filtered")
        case "skipped":
            tracker.on_video_skipped(video, "skipped")

    tracker.close(video)


def main():
    user = TerminalMusicLibraryUser()
    tracker = user.music_download_tracker

    videos: list[tuple[VideoId, ExpectedResult]] = [
        (VideoId("finished_video"), "finished"),
        (VideoId("skipped_video"), "skipped"),
        (VideoId("filtered_video"), "filtered"),
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
