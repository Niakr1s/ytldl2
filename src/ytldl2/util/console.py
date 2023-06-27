import sys


def clear_last_line(n: int = 1):
    sys.stdout.write("\033[F\033[K" * n)
