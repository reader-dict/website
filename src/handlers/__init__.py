from . import base, paypal, stripe

CACHE: dict[str, base.Handler] = {}
SUPPORTED_HANDLERS = {"paypal", "stripe"}


def get(source: str) -> base.Handler:
    if not (cached := CACHE.get(source)):
        cached = CACHE[source] = paypal.Handler() if source == "paypal" else stripe.Handler()
    return cached


__all__ = ["get"]
