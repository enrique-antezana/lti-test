from typing import Optional, Union
from fastapi import Request as FastAPIRequest
from pylti1p3.request import Request


class FastAPIRequest(Request):
    """FastAPI adapter for the Request abstract class."""
    
    def __init__(self, request: FastAPIRequest):
        self._request = request
        self._form_data = None
        self._cached_form = False
    
    @property
    def session(self):
        """FastAPI doesn't have built-in sessions, so we return None.
        Session handling should be implemented separately."""
        return None
    
    def is_secure(self) -> bool:
        """Check if the request is secure (HTTPS)."""
        return self._request.url.scheme == "https"
    
    def get_param(self, key: str) -> str:
        """Get parameter from query params or form data."""
        # Try query parameters first
        value = self._request.query_params.get(key)
        if value is not None:
            return value
        
        # For form data, we'll handle this differently in FastAPI
        # since form() is async and we can't call it here
        # This will be handled by the FastAPI endpoint directly
        return ""
    
    def get_cookie(self, key: str) -> Optional[str]:
        """Get cookie value."""
        return self._request.cookies.get(key)
    
    def get_header(self, key: str) -> Optional[str]:
        """Get header value."""
        return self._request.headers.get(key)
    
    def get_method(self) -> str:
        """Get HTTP method."""
        return self._request.method
    
    def get_url(self) -> str:
        """Get full URL."""
        return str(self._request.url)
