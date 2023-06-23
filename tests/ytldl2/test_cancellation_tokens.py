import signal

from ytldl2.cancellation_tokens import CancellationToken, GracefulKiller


class TestCancellationToken:
    def test_init(self):
        killer = CancellationToken()
        assert not killer.kill_requested

    def test_request_kill(self):
        killer = CancellationToken()
        killer.request_kill()
        assert killer.kill_requested


class TestGracefulKiller:
    def test_kill_via_SIGINT(self):
        killer = GracefulKiller()
        signal.raise_signal(signal.SIGINT)
        assert killer.kill_requested

    def test_kill_via_SIGTERM(self):
        killer = GracefulKiller()
        signal.raise_signal(signal.SIGTERM)
        assert killer.kill_requested
