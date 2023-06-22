import signal
from typing import Protocol


class CancellationToken(Protocol):
    @property
    def kill_requested(self) -> bool:
        ...


class GracefulKiller(CancellationToken):
    """Simpler graceful exit manager, that intercepts SIGINT and SIGTERM signals."""

    def __init__(self):
        self._kill_requested = False

        signal.signal(signal.SIGINT, self._request_kill)
        signal.signal(signal.SIGTERM, self._request_kill)

    @property
    def kill_requested(self) -> bool:
        return self._kill_requested

    def request_kill(self) -> None:
        """Use this method to request kill."""
        self._request_kill()

    def _request_kill(self, *args) -> None:
        self._kill_requested = True
