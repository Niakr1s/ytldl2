from typing import Callable, Literal, TypedDict

Status = Literal["downloading", "error", "finished"]


class DownloadProgressBase(TypedDict):
    filename: str
    status: Status
    info_dict: dict


class DownloadProgressDownloading(DownloadProgressBase):
    downloaded_bytes: int
    total_bytes_estimate: float


class DownloadProgressFinished(DownloadProgressBase):
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


ProgressHook = Callable[[DownloadProgress], None]
PostprocessorHook = Callable[[PostprocessorProgress], None]
