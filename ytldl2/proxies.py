def to_proxies(proxy: str | None) -> dict | None:
    """
    Converts a proxy string to a dict with proxies.
    If a proxy string is empty returns None.
    """
    proxy = proxy or None
    if proxy is not None:
        proxies = {
            "http": proxy,
            "https": proxy,
        }
    else:
        proxies = None
    return proxies
