import time

from fastapi import HTTPException, Request, status

from app.utils.redis import redis


async def rate_limit(request: Request, max_requests: int = 100, window_seconds: int = 60):
    key = f"ratelimit:{request.client.host}:{request.url.path}"
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
            detail="Too many requests. Slow down.",
        )
