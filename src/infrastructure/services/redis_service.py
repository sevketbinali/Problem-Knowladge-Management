"""Service for interacting with Redis for caching and rate limiting."""
import json
from typing import Any, Optional

import redis.asyncio as redis
from src.core.config import settings


class RedisService:
    def __init__(self):
        # Requirement 17.3: Redis connection pool
        self.pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20
        )
        self.client = redis.Redis(connection_pool=self.pool)

    async def get_cache(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache."""
        data = await self.client.get(key)
        if data:
            return json.loads(data)
        return None

    async def set_cache(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set a value in cache with TTL."""
        ttl = ttl or settings.REDIS_CACHE_TTL
        await self.client.set(key, json.dumps(value), ex=ttl)

    async def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user has exceeded rate limit.
        Returns True if allowed, False if limited.
        Requirement 17.2: 10 requests/min/user
        """
        key = f"rate_limit:{user_id}"
        current = await self.client.get(key)
        
        if current is None:
            # First request in the minute window
            await self.client.set(key, 1, ex=60)
            return True
        
        if int(current) >= settings.RATE_LIMIT_PER_MINUTE:
            return False
        
        await self.client.incr(key)
        return True

    async def close(self):
        """Close the connection pool."""
        await self.pool.disconnect()
