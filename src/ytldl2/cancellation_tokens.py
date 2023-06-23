import signal


class CancellationToken:
    def __init__(self):
        self._kill_requested = False

    @property
    def kill_requested(self) -> bool:
        return self._kill_requested

    def request_kill(self) -> None:
        """Use this method to request kill."""
        self._kill_requested = True


class GracefulKiller(CancellationToken):
    """Simpler graceful exit manager, that intercepts SIGINT and SIGTERM signals."""

    def __init__(self):
        super().__init__()

        signal.signal(signal.SIGINT, self._request_kill)
        signal.signal(signal.SIGTERM, self._request_kill)

    def _request_kill(self, *args) -> None:
        super().request_kill()
