from typing import Optional
from fastapi import Request, Response
from pylti1p3.cookie import CookieService


class FastAPICookieService(CookieService):
    """FastAPI cookie service implementation."""
    
    def __init__(self, request: Request):
        self._request = request
        self._cookies_to_set: dict = {}
    
    def get_cookie(self, key: str) -> Optional[str]:
        """Get cookie value from request."""
        return self._request.cookies.get(key)
    
    def set_cookie(self, key: str, value: str, **kwargs):
        """Set cookie to be added to response."""
        self._cookies_to_set[key] = {
            'value': value,
            **kwargs
        }
    
    def update_response(self, response: Response):
        """Update response with cookies."""
        for key, cookie_data in self._cookies_to_set.items():
            response.set_cookie(
                key=key,
                value=cookie_data['value'],
                **{k: v for k, v in cookie_data.items() if k != 'value'}
            )
    
    def get_cookies_to_set(self) -> dict:
        """Get cookies that need to be set."""
        return self._cookies_to_set.copy()
