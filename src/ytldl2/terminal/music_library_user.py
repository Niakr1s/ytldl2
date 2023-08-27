import typing

from rich.progress import Progress, TaskID
from ytldl2.models.download_hooks import (
    DownloadProgress,
    PostprocessorProgress,
    is_postprocessor_finished,
    is_postprocessor_started,
    is_progress_downloading,
)
from ytldl2.models.download_result import Downloaded, DownloadResult, Error, Filtered
from ytldl2.models.home_items import HomeItems, HomeItemsFilter
from ytldl2.models.types import VideoId
from ytldl2.protocols.ui import HomeItemsReviewer, ProgressBar, Ui
from ytldl2.util.console import clear_last_line


class TerminalMusicDownloadTracker(ProgressBar):
    def __init__(
        self,
    ) -> None:
        self._progress = Progress(expand=True)
        self._dl: TaskID | None = None
        self._pp: dict[str, TaskID] = {}

    def new(self, video: VideoId) -> None:
        self._clean()
        self._progress.start()
        self._dl = self._progress.add_task(video, total=None)

    def close(self, video: VideoId) -> None:
        self._clean()
        self._progress.stop()

    def _clean(self) -> None:
        if self._dl is not None:
            self._progress.remove_task(self._dl)
            self._dl = None
        if self._pp:
            for pp in self._pp.values():
                self._progress.remove_task(pp)
            self._pp = {}

    def on_download_progress(self, progress: DownloadProgress) -> None:
        if is_progress_downloading(progress) or is_progress_downloading(progress):
            self._progress.update(
                self._dl,  # type: ignore
                description=progress["filename"],
                total=progress["total_bytes"],
                completed=progress["downloaded_bytes"],
            )

    def on_postprocessor_progress(self, progress: PostprocessorProgress) -> None:
        pp = progress["postprocessor"]
        if is_postprocessor_started(progress):
            self._pp[pp] = self._progress.add_task(f"\t{pp}", total=None)
        if is_postprocessor_finished(progress):
            self._progress.remove_task(self._pp[pp])
            del self._pp[pp]


class TerminalHomeItemsReviewer(HomeItemsReviewer):
    def review_home_items(
        self, home_items: HomeItems, home_items_filter: HomeItemsFilter
    ):
        print("Got following home items:")
        print(f"Videos: {len(home_items.videos)} items.")
        print(f"Channels: {home_items.channels}")
        print(f"Playlistst: {home_items.playlists}")
        print()

        print("They will be filtered with following filters:")
        print(f"Videos: {home_items_filter.videos}")
        print(f"Channels: {home_items_filter.channels}")
        print(f"Playlists: {home_items_filter.playlists}")
        print()

        print("If you wish to review filters, please change them via config.")


class TerminalMusicLibraryUser(Ui):
    def home_items_reviewer(self) -> HomeItemsReviewer:
        return TerminalHomeItemsReviewer()

    def on_download_result(self, result: DownloadResult):
        """Called by library after download to display download result."""

        clear_last_line()
        match result:
            case Downloaded():
                print(
                    f"Downloaded: [{result.video_id}] ({result.info.artist} - {result.info.title})."  # noqa: E501
                )
            case Filtered():
                print(
                    f"Filtered: [{result.video_id}] ({result.info.title}), reason: {result.reason}"  # noqa: E501
                )
            case Error():
                print(f"Error: [{result.video_id}], reason: {result.error}")
            case _:
                typing.assert_never(result)

    def progress_bar(self) -> ProgressBar:
        return TerminalMusicDownloadTracker()
