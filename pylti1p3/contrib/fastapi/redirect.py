from typing import Optional
from fastapi import Response
from fastapi.responses import RedirectResponse, HTMLResponse
from pylti1p3.redirect import Redirect


class FastAPIRedirect(Redirect):
    """FastAPI redirect implementation."""
    
    def __init__(self, location: str, cookie_service=None):
        super().__init__()
        self._location = location
        self._cookie_service = cookie_service
    
    def do_redirect(self) -> Response:
        """Perform HTTP redirect."""
        response = RedirectResponse(url=self._location)
        if self._cookie_service:
            self._cookie_service.update_response(response)
        return response
    
    def do_js_redirect(self) -> Response:
        """Perform JavaScript redirect."""
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Redirecting...</title>
        </head>
        <body>
            <script type="text/javascript">
                window.location = "{self._location}";
            </script>
            <p>Redirecting to <a href="{self._location}">{self._location}</a>...</p>
        </body>
        </html>
        '''
        response = HTMLResponse(content=html_content)
        if self._cookie_service:
            self._cookie_service.update_response(response)
        return response
    
    def set_redirect_url(self, location: str):
        """Set the redirect URL."""
        self._location = location
    
    def get_redirect_url(self) -> str:
        """Get the redirect URL."""
        return self._location
