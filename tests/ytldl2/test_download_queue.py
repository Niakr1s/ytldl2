import pathlib

import pytest
from ytldl2.download_queue import (
    DownloadQueue,
    QueueError,
)
from ytldl2.models.types import VideoId


class TestDownloadQueue:
    @pytest.fixture
    def videos(self) -> list[VideoId]:
        return [VideoId("a"), VideoId("b"), VideoId("c")]

    def test_next_downloaded(self, videos: list[VideoId]):
        queue = DownloadQueue(videos)

        for i, item in enumerate(queue):
            assert videos[i] == item
            if i < len(videos) - 1:
                with pytest.raises(QueueError, match="has item, pending mark"):
                    queue.__next__()
            queue.mark_downloaded(pathlib.Path())
        assert len(queue) == 0
        assert videos == [v.video_id for v in queue.downloaded]
        assert all(v.path for v in queue.downloaded)
        assert not queue.skipped
        assert not queue.filtered
        self._test_after(queue)

    def test_next_skipped(self, videos: list[VideoId]):
        queue = DownloadQueue(videos)

        for i, item in enumerate(queue):
            assert videos[i] == item
            if i < len(videos) - 1:
                with pytest.raises(QueueError, match="has item, pending mark"):
                    queue.__next__()
            queue.mark_skipped("skipped")
        assert len(queue) == 0
        assert videos == [v.video_id for v in queue.skipped]
        assert all(v.reason for v in queue.skipped)
        assert not queue.downloaded
        assert not queue.filtered
        self._test_after(queue)

    def test_next_filtered(self, videos: list[VideoId]):
        queue = DownloadQueue(videos)

        for i, item in enumerate(queue):
            assert videos[i] == item
            if i < len(videos) - 1:
                with pytest.raises(QueueError, match="has item, pending mark"):
                    queue.__next__()
            queue.mark_filtered("filtered")
        assert len(queue) == 0
        assert videos == [v.video_id for v in queue.filtered]
        assert all(v.filtered_reason for v in queue.filtered)
        assert not queue.skipped
        assert not queue.downloaded
        self._test_after(queue)

    def _test_after(self, queue: DownloadQueue):
        with pytest.raises(StopIteration):
            queue.__next__()

        with pytest.raises(QueueError, match="no item, pending mark"):
            queue.mark_downloaded(pathlib.Path())
            queue.mark_filtered("reason")
            queue.mark_skipped("reason")

    def test_revert(self, videos: list[VideoId]):
        queue = DownloadQueue(videos)
        with pytest.raises(QueueError, match="no item"):
            queue.revert()
        first = queue.__next__()
        queue.revert()
        with pytest.raises(QueueError, match="no item"):
            queue.revert()
        second = queue.__next__()
        assert first == second
