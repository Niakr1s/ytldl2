import signal

from ytldl2.killer import GracefulKiller


class TestGracefulKiller:
    def test_init(self):
        killer = GracefulKiller()
        assert not killer.kill_requested

    def test_request_kill(self):
        killer = GracefulKiller()
        killer.request_kill()
        assert killer.kill_requested

    def test_kill_via_SIGINT(self):
        killer = GracefulKiller()
        signal.raise_signal(signal.SIGINT)
        assert killer.kill_requested

    def test_kill_via_SIGTERM(self):
        killer = GracefulKiller()
        signal.raise_signal(signal.SIGTERM)
        assert killer.kill_requested
