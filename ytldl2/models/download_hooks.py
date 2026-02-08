from typing import Callable, Literal, TypedDict, TypeGuard

Status = Literal["downloading", "error", "finished"]


class DownloadProgressBase(TypedDict):
    filename: str
    status: Status
    info_dict: dict


class DownloadProgressDownloading(DownloadProgressBase):
    downloaded_bytes: int
    total_bytes: int


class DownloadProgressFinished(DownloadProgressBase):
    downloaded_bytes: int
    total_bytes: int


class DownloadProgressError(DownloadProgressBase):
    pass


DownloadProgress = (
    DownloadProgressDownloading | DownloadProgressFinished | DownloadProgressError
)


class PostprocessorProgressBase(TypedDict):
    status: Literal["started", "finished"]
    info_dict: dict
    postprocessor: str


class PostprocessorProgressStarted(PostprocessorProgressBase):
    pass


class PostprocessorProgressFinished(PostprocessorProgressBase):
    pass


PostprocessorProgress = PostprocessorProgressStarted | PostprocessorProgressFinished


def is_progress_downloading(
    progress: DownloadProgress,
) -> TypeGuard[DownloadProgressDownloading]:
    return progress["status"] == "downloading"


def is_progress_finished(
    progress: DownloadProgress,
) -> TypeGuard[DownloadProgressFinished]:
    return progress["status"] == "finished"


def is_progress_error(
    progress: DownloadProgress,
) -> TypeGuard[DownloadProgressError]:
    return progress["status"] == "error"


def is_postprocessor_started(
    postprocessor_progress: PostprocessorProgress,
) -> TypeGuard[PostprocessorProgressStarted]:
    return postprocessor_progress["status"] == "started"


def is_postprocessor_finished(
    postprocessor_progress: PostprocessorProgress,
) -> TypeGuard[PostprocessorProgressFinished]:
    return postprocessor_progress["status"] == "finished"


ProgressHook = Callable[[DownloadProgress], None]
PostprocessorHook = Callable[[PostprocessorProgress], None]
