import time
from typing import Any, Dict

from pylti1p3.launch_data_storage.cache import CacheDataStorage

# Global shared cache instance to persist across requests
_shared_cache = None

class SimpleCache:
    """
    Simple in-memory cache with expiration support.
    """
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._expires: Dict[str, float] = {}
    
    def get(self, key: str):
        """Get value from cache, checking expiration."""
        if key in self._expires and time.time() > self._expires[key]:
            # Clean up expired entries
            self._cache.pop(key, None)
            self._expires.pop(key, None)
            return None
        return self._cache.get(key)
    
    def set(self, key: str, value: Any, timeout: int = None):
        """Set value in cache with optional expiration."""
        self._cache[key] = value
        if timeout:
            self._expires[key] = time.time() + timeout
        else:
            # Remove expiration if timeout is None
            self._expires.pop(key, None)
    
    def delete(self, key: str):
        """Delete key from cache."""
        self._cache.pop(key, None)
        self._expires.pop(key, None)
    
    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()
        self._expires.clear()

class FastAPICacheDataStorage(CacheDataStorage):
    _cache = None

    def __init__(self, cache=None, **kwargs):
        global _shared_cache
        if cache is None:
            # Use shared cache instance to persist across requests
            if _shared_cache is None:
                _shared_cache = SimpleCache()
            self._cache = _shared_cache
        else:
            self._cache = cache
        super().__init__(self._cache, **kwargs)