from ytldl2.cache import Cache


class Downloader:
    def __init__(self, cache: Cache) -> None:
        self._cache = cache
