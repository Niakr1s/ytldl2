import typing

from rich import box
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table
from typing_extensions import override
from ytldl2.models.download_hooks import (
    DownloadProgress,
    PostprocessorProgress,
    is_postprocessor_finished,
    is_postprocessor_started,
    is_progress_downloading,
    is_progress_finished,
)
from ytldl2.models.download_result import Downloaded, DownloadResult, Error, Filtered
from ytldl2.models.home_items import HomeItems, HomeItemsFilter
from ytldl2.models.song import Song
from ytldl2.models.types import VideoId
from ytldl2.protocols.ui import BatchDownloadTracker, HomeItemsReviewer, ProgressBar, Ui
from ytldl2.util.console import clear_last_line

console = Console()


class TerminalProgressBar(ProgressBar):
    def __init__(
        self,
    ) -> None:
        self._progress = Progress(expand=True)
        self._dl: TaskID | None = None
        self._pp: dict[str, TaskID] = {}

    @override
    def new(self, video: VideoId) -> None:
        self._clean()
        self._progress.start()
        self._dl = self._progress.add_task(video, total=None)

    @override
    def close(self, video: VideoId) -> None:
        self._clean()
        self._progress.stop()
        clear_last_line()

    def _clean(self) -> None:
        if self._dl is not None:
            self._progress.remove_task(self._dl)
            self._dl = None
        if self._pp:
            for pp in self._pp.values():
                self._progress.remove_task(pp)
            self._pp = {}

    @override
    def on_download_progress(self, progress: DownloadProgress) -> None:
        if is_progress_downloading(progress) or is_progress_finished(progress):
            self._progress.update(
                self._dl,  # type: ignore
                description=progress["filename"],
                total=progress["total_bytes"],
                completed=progress["downloaded_bytes"],
            )

    @override
    def on_postprocessor_progress(self, progress: PostprocessorProgress) -> None:
        pp = progress["postprocessor"]
        if is_postprocessor_started(progress):
            self._pp[pp] = self._progress.add_task(f"\t{pp}", total=None)
        if is_postprocessor_finished(progress):
            self._progress.remove_task(self._pp[pp])
            del self._pp[pp]


class TerminalHomeItemsReviewer(HomeItemsReviewer):
    @override
    def review_home_items(
        self, home_items: HomeItems, home_items_filter: HomeItemsFilter
    ):
        print("\nGot following home items:")
        print(f"Videos: {len(home_items.videos)} items.")
        print(f"Channels: {[c.title for c in home_items.channels]}")
        print(f"Playlists: {[c.title for c in home_items.playlists]}")

        print("\nThey will be filtered with following filters:")
        print(f"Videos: {home_items_filter.videos}")
        print(f"Channels: {home_items_filter.channels}")
        print(f"Playlists: {home_items_filter.playlists}")


class TerminalBatchDownloadTracker(BatchDownloadTracker):
    def __init__(self) -> None:
        self._downloaded: list[Downloaded] = []
        self._filtered: list[Filtered] = []
        self._errors: list[Error] = []

    @override
    def start(self, songs: list[Song], limit: int | None):
        print(f"\nStarting to download batch of {len(songs)} songs, limit={limit}:")

    @override
    def on_download_result(self, result: DownloadResult):
        clear_last_line()
        match result:
            case Downloaded():
                print(
                    f"Downloaded: [{result.video_id}] ({result.info.artist} - {result.info.title})."  # noqa: E501
                )
                self._downloaded.append(result)
            case Filtered():
                print(
                    f"Filtered: [{result.video_id}] ({result.info.title}), reason: {result.reason}"  # noqa: E501
                )
                self._filtered.append(result)
            case Error():
                print(f"Error: [{result.video_id}], reason: {result.error}")
                self._errors.append(result)
            case _:
                typing.assert_never(result)

    @override
    def end(self):
        print()
        self._print_download_result_table()

    def _print_download_result_table(self):
        d = len(self._downloaded)
        f = len(self._filtered)
        e = len(self._errors)

        table = Table(show_footer=True, box=box.MINIMAL)
        table.add_column("Result", footer="Total")
        table.add_column("Count", justify="center", footer=str(d + f + e))

        table.add_row("Downloaded", str(d))
        table.add_row("Filtered", str(f))
        table.add_row("Errors", str(e))

        console.print(table)


class TerminalUi(Ui):
    @override
    def library_update_started(self):
        print("Library update started...")

    @override
    def home_items_reviewer(self) -> HomeItemsReviewer:
        return TerminalHomeItemsReviewer()

    @override
    def batch_download_tracker(self):
        return TerminalBatchDownloadTracker()

    @override
    def progress_bar(self) -> ProgressBar:
        return TerminalProgressBar()
