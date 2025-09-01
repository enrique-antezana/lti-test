from fastapi import Request
from pylti1p3.oidc_login import OIDCLogin
from pylti1p3.request import Request as LTIRequest
from pylti1p3.tool_config import ToolConfAbstract

from .cookie import FastAPICookieService
from .redirect import FastAPIRedirect
from .request import FastAPIRequest
from .session import FastAPISessionService


class FastAPIOIDCLogin(OIDCLogin):
    """FastAPI OIDC login implementation."""
    
    def __init__(
        self,
        request: Request,
        tool_config: ToolConfAbstract,
        session_service=None,
        cookie_service=None,
        launch_data_storage=None,
    ):
        # Convert FastAPI request to LTI request
        lti_request = (
            request if isinstance(request, LTIRequest) else FastAPIRequest(request)
        )
        
        # Set up services
        cookie_service = (
            cookie_service if cookie_service else FastAPICookieService(request)
        )
        session_service = (
            session_service if session_service else FastAPISessionService(lti_request)
        )
        
        super().__init__(
            lti_request,
            tool_config,
            session_service,
            cookie_service,
            launch_data_storage,
        )
    
    def get_redirect(self, url: str) -> FastAPIRedirect:
        """Get redirect object for FastAPI."""
        return FastAPIRedirect(url, self._cookie_service)
    
    def get_response(self, html: str):
        """Get HTML response for FastAPI."""
        from fastapi.responses import HTMLResponse
        response = HTMLResponse(content=html)
        if self._cookie_service:
            self._cookie_service.update_response(response)
        return response
