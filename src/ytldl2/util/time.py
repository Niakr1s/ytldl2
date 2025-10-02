from time import sleep, time

from ytldl2.cancellation_tokens import CancellationToken


def sleep_with_cancel(delay: int, cancellation_token: CancellationToken):
    """
    delay: in seconds
    """

    until = time() + delay
    while time() < until and not cancellation_token.kill_requested:
        sleep(5)


if __name__ == "__main__":
    c = CancellationToken()
    c.request_kill()
    now = time()
    sleep_with_cancel(5, c)
    assert time() - now < 5
