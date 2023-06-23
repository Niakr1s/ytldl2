import pathlib

import pytest

from ytldl2.download_queue import (
    Downloaded,
    DownloadQueue,
    Failed,
    Item,
    ItemAlreadyCompletedError,
    ItemNotCompletedError,
    Skipped,
)
from ytldl2.models import VideoId


class TestDownloadQueue:
    @pytest.fixture
    def queue(self) -> DownloadQueue:
        return DownloadQueue([VideoId("a"), VideoId("b")])

    def test_next(self, queue: DownloadQueue):
        item = queue.__next__()
        assert "a" == item.video_id
        with pytest.raises(ItemNotCompletedError):
            queue.__next__()
        item.mark_as_downloaded(pathlib.Path())
        item = queue.__next__()
        assert "b" == item.video_id
        item.mark_as_downloaded(pathlib.Path())
        with pytest.raises(StopIteration):
            queue.__next__()

    def item_can_not_be_completed_twice(self, item: Item):
        with pytest.raises(ItemAlreadyCompletedError):
            item.mark_as_downloaded(pathlib.Path())
        with pytest.raises(ItemAlreadyCompletedError):
            item.mark_as_failed(Exception())
        with pytest.raises(ItemAlreadyCompletedError):
            item.mark_as_skipped("")

    def test_item__mark_as_downloaded(self, queue: DownloadQueue):
        item = queue.__next__()
        path = pathlib.Path()
        item.mark_as_downloaded(path)
        self.item_can_not_be_completed_twice(item)

        video_id = item.video_id
        assert video_id not in queue.remained

        expected = Downloaded(item.video_id, path)
        assert expected in queue.downloaded
        assert not queue.failed
        assert not queue.skipped

    def test_item__mark_as_failed(self, queue: DownloadQueue):
        item = queue.__next__()
        err = Exception("some error")
        item.mark_as_failed(err)
        self.item_can_not_be_completed_twice(item)

        video_id = item.video_id
        assert video_id not in queue.remained

        expected = Failed(item.video_id, err)
        assert not queue.downloaded
        assert expected in queue.failed
        assert not queue.skipped

    def test_item__mark_as_skipped(self, queue: DownloadQueue):
        item = queue.__next__()
        reason = "some reason"
        item.mark_as_skipped(reason)
        self.item_can_not_be_completed_twice(item)

        video_id = item.video_id
        assert video_id not in queue.remained

        expected = Skipped(item.video_id, reason)
        assert not queue.downloaded
        assert not queue.failed
        assert expected in queue.skipped
