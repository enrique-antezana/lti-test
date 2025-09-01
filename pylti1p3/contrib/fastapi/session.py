import json
import time
from typing import Any, Dict, Optional
from fastapi import Request
from pylti1p3.session import SessionService
from pylti1p3.launch_data_storage.base import LaunchDataStorage


class FastAPISessionService(SessionService):
    """FastAPI session service implementation using in-memory storage.
    
    Note: This is a simple in-memory implementation. For production use,
    consider using Redis, database, or JWT-based storage.
    """
    
    def __init__(self, request: Request):
        # Initialize with a simple in-memory storage
        super().__init__(request)
        self._storage: Dict[str, Any] = {}
        self._expirations: Dict[str, float] = {}
    
    def _cleanup_expired(self):
        """Remove expired keys."""
        current_time = time.time()
        expired_keys = [
            key for key, exp in self._expirations.items() 
            if exp < current_time
        ]
        for key in expired_keys:
            self._storage.pop(key, None)
            self._expirations.pop(key, None)
    
    def _set_value(self, key: str, value: Any):
        """Set a value with expiration."""
        self._cleanup_expired()
        self._storage[key] = value
        self._expirations[key] = time.time() + self._launch_data_lifetime
    
    def _get_value(self, key: str) -> Any:
        """Get a value if it exists and hasn't expired."""
        self._cleanup_expired()
        return self._storage.get(key)
    
    def set_data_storage(self, data_storage: LaunchDataStorage[Any]):
        """Set custom data storage implementation."""
        self.data_storage = data_storage
    
    def set_launch_data_lifetime(self, time_sec: int):
        """Set the lifetime for launch data."""
        self._launch_data_lifetime = time_sec


class FastAPIRedisSessionService(SessionService):
    """Redis-based session service for FastAPI (recommended for production)."""
    
    def __init__(self, request: Request, redis_client):
        super().__init__(request)
        self.redis_client = redis_client
    
    def _set_value(self, key: str, value: Any):
        """Set a value in Redis with expiration."""
        serialized_value = json.dumps(value)
        self.redis_client.setex(
            key, 
            self._launch_data_lifetime, 
            serialized_value
        )
    
    def _get_value(self, key: str) -> Any:
        """Get a value from Redis."""
        value = self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    
    def check_value(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        return bool(self.redis_client.exists(key))
