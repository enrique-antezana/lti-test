from typing import Optional
from fastapi import Request, Response
from pylti1p3.cookie import CookieService


class FastAPICookieService(CookieService):
    """FastAPI cookie service implementation."""
    
    def __init__(self, request: Request):
        self._request = request
        self._cookies_to_set: dict = {}
    
    def _get_key(self, key: str) -> str:
        """Get the full cookie key with prefix."""
        return self._cookie_prefix + "-" + key
    
    def get_cookie(self, name: str) -> Optional[str]:
        """Get cookie value from request."""
        return self._request.cookies.get(self._get_key(name))
    
    def set_cookie(self, name: str, value: str, exp: int = 3600, **kwargs):
        """Set cookie to be added to response."""
        self._cookies_to_set[self._get_key(name)] = {
            'value': value,
            'max_age': exp,
            **kwargs
        }
    
    def update_response(self, response: Response):
        """Update response with cookies."""
        for key, cookie_data in self._cookies_to_set.items():
            cookie_kwargs = {
                'key': key,
                'value': cookie_data['value'],
                'max_age': cookie_data.get('max_age', 3600),
                'secure': self._request.url.scheme == 'https',
                'httponly': True,
                'path': '/',
            }
            
            # Add SameSite attribute for HTTPS
            if self._request.url.scheme == 'https':
                cookie_kwargs['samesite'] = 'None'
            
            # Add any additional kwargs
            for k, v in cookie_data.items():
                if k not in ['value', 'max_age']:
                    cookie_kwargs[k] = v
            
            response.set_cookie(**cookie_kwargs)
    
    def get_cookies_to_set(self) -> dict:
        """Get cookies that need to be set."""
        return self._cookies_to_set.copy()
