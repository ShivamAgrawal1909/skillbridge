from app.config import settings

redis = None

if settings.REDIS_URL:
    import redis.asyncio as aioredis
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)