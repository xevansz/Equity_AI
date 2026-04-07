from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def get_rate_limit_key(request: Request) -> str:
    return get_remote_address(request)


limiter = Limiter(key_func=get_rate_limit_key)


def get_limiter_for_method(request: Request) -> str:
    if request.method in ["GET", "HEAD", "OPTIONS"]:
        return "100/minute"
    else:
        return "60/minute"
