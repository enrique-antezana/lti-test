from fastapi import Request
from pylti1p3.message_launch import MessageLaunch
from pylti1p3.request import Request as LTIRequest
from pylti1p3.tool_config import ToolConfAbstract

from .cookie import FastAPICookieService
from .request import FastAPIRequest
from .session import FastAPISessionService


class FastAPIMessageLaunch(MessageLaunch):
    """FastAPI message launch implementation."""
    
    def __init__(
        self,
        request: Request,
        tool_config: ToolConfAbstract,
        session_service=None,
        cookie_service=None,
        launch_data_storage=None,
        requests_session=None,
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
            requests_session,
        )
    
    def _get_request_param(self, key: str) -> str:
        """Get request parameter."""
        return self._request.get_param(key)
