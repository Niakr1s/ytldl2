import pathlib

import pytest

from ytldl2.download_queue import (
    Downloaded,
    DownloadQueue,
    DownloadQueueHasUncompleteItem,
    Failed,
    Item,
    ItemModifyNotAllowed,
    ItemNotCompletedError,
    Skipped,
)
from ytldl2.models import VideoId


class TestDownloadQueue:
    @pytest.fixture
    def queue(self) -> DownloadQueue:
        return DownloadQueue([VideoId("a"), VideoId("b")])

    def test_next(self, queue: DownloadQueue):
        item = queue.next()
        assert item
        assert "a" == item.video_id
        with pytest.raises(ItemNotCompletedError):
            queue.next()
        item.complete_as_downloaded(pathlib.Path())

        item = queue.next()
        assert item
        assert "b" == item.video_id
        item.complete_as_downloaded(pathlib.Path())

        assert not queue.next()

    def item_can_not_be_completed_twice(self, item: Item):
        with pytest.raises(ItemModifyNotAllowed):
            item.complete_as_downloaded(pathlib.Path())
        with pytest.raises(ItemModifyNotAllowed):
            item.complete_as_failed(Exception())
        with pytest.raises(ItemModifyNotAllowed):
            item.complete_as_skipped("")

    def test_item__complete_as_downloaded(self, queue: DownloadQueue):
        item = queue.next()
        assert item
        path = pathlib.Path()
        item.complete_as_downloaded(path)
        self.item_can_not_be_completed_twice(item)

        video_id = item.video_id
        assert video_id not in queue._queue

        expected = Downloaded(item.video_id, path)
        assert expected in queue._downloaded
        assert not queue._failed
        assert not queue._skipped

    def test_item__complete_as_failed(self, queue: DownloadQueue):
        item = queue.next()
        assert item
        err = Exception("some error")
        item.complete_as_failed(err)
        self.item_can_not_be_completed_twice(item)

        video_id = item.video_id
        assert video_id not in queue._queue

        expected = Failed(item.video_id, err)
        assert not queue._downloaded
        assert expected in queue._failed
        assert not queue._skipped

    def test_item__complete_as_skipped(self, queue: DownloadQueue):
        item = queue.next()
        assert item
        reason = "some reason"
        item.complete_as_skipped(reason)
        self.item_can_not_be_completed_twice(item)

        video_id = item.video_id
        assert video_id not in queue._queue

        expected = Skipped(item.video_id, reason)
        assert not queue._downloaded
        assert not queue._failed
        assert expected in queue._skipped

    def test_item__return_to_queue(self, queue: DownloadQueue):
        item = queue.next()
        assert item
        video_id = item.video_id

        item.return_to_queue()
        res = queue.to_result()
        assert video_id == res.queue[-1]
        assert not res.downloaded
        assert not res.failed
        assert not res.skipped

        same_item = queue.next()
        assert same_item
        assert video_id == same_item.video_id

    def test_to_result(self, queue: DownloadQueue):
        res = queue.to_result()
        videos = ["a", "b"]
        assert videos == res.videos
        assert list(reversed(videos)) == res.queue
        assert not res.downloaded
        assert not res.failed
        assert not res.skipped

    def test_to_result__with_incompleted_item(self, queue: DownloadQueue):
        assert queue.next()
        with pytest.raises(DownloadQueueHasUncompleteItem):
            queue.to_result()

    def test_to_result_in_loop(self, queue: DownloadQueue):
        while item := queue.next():
            item.complete_as_downloaded(pathlib.Path())
            res = queue.to_result()
            assert ["a", "b"] == res.videos
            assert res.downloaded
            assert not res.failed
            assert not res.skipped

    def test_to_result__item_uncompleted(self, queue: DownloadQueue):
        queue.next()
        with pytest.raises(DownloadQueueHasUncompleteItem):
            queue.to_result()
