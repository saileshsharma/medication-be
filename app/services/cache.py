"""
Redis Cache Service
Provides caching for analysis results
"""

import redis
import json
from typing import Optional, Dict
from app.core.config import settings


class CacheService:
    """Redis-based caching service"""

    def __init__(self):
        """Initialize Redis connection"""
        try:
            # Use REDIS_URL if provided (Railway), otherwise use individual settings (local)
            if settings.REDIS_URL:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
            else:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
            # Test connection
            self.redis_client.ping()
            self.enabled = settings.ENABLE_CACHING
        except Exception as e:
            print(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False

    def get(self, key: str) -> Optional[Dict]:
        """Get cached value"""
        if not self.enabled or not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")

        return None

    def set(self, key: str, value: Dict, ttl: int = None) -> bool:
        """Set cache value with optional TTL"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            ttl = ttl or settings.CACHE_TTL
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete cache entry"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all cache (use with caution)"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.enabled or not self.redis_client:
            return {'enabled': False}

        try:
            info = self.redis_client.info()
            return {
                'enabled': True,
                'connected': True,
                'keys': self.redis_client.dbsize(),
                'memory_used': info.get('used_memory_human', 'N/A'),
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0)
            }
        except Exception as e:
            return {'enabled': True, 'connected': False, 'error': str(e)}

    def is_healthy(self) -> bool:
        """Check if cache is healthy"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            return self.redis_client.ping()
        except:
            return False


# Singleton instance
cache = CacheService()
