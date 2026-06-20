import time

from fastapi import HTTPException, Request, status

from app.config import settings
from app.utils.redis import redis


async def rate_limit(
    request: Request,
    max_requests: int = 100,
    window_seconds: int = 60,
):
    # skip rate limiting in test environment
    if settings.ENV == "test":
        return

    user_id = getattr(request.state, "user_id", None)
    identifier = str(user_id) if user_id else request.client.host
    key = f"ratelimit:{identifier}:{request.url.path}"
    now = time.time()
    window_start = now - window_seconds

    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window_seconds)
    results = await pipe.execute()

    count = results[2]
    if count > max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down.",
        )


def strict_limit(max_requests: int = 5, window_seconds: int = 60):
    async def dependency(request: Request):
        await rate_limit(request, max_requests, window_seconds)
    return dependency