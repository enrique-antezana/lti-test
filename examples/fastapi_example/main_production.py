"""
Production-ready FastAPI LTI 1.3 Application for Vercel deployment

This version is optimized for serverless deployment with environment variables.
"""

import os
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import PyLTI1p3 components
from pylti1p3.tool_config import ToolConfDict
from pylti1p3.contrib.fastapi import (
    FastAPIOIDCLogin,
    FastAPIMessageLaunch,
    FastAPISessionService,
    FastAPICookieService
)

# Create FastAPI app
app = FastAPI(
    title="LTI 1.3 FastAPI Example",
    description="Example LTI 1.3 tool built with FastAPI and PyLTI1p3",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Production LTI Configuration from Environment Variables
def get_lti_config():
    """Get LTI configuration from environment variables."""
    client_id = os.getenv("LTI_CLIENT_ID", "your_client_id")
    deployment_id = os.getenv("LTI_DEPLOYMENT_ID", "your_deployment_id")
    private_key = os.getenv("LTI_PRIVATE_KEY")
    public_key = os.getenv("LTI_PUBLIC_KEY")
    
    # Default to Canvas if no specific platform is configured
    platform_url = os.getenv("LTI_PLATFORM_URL", "https://canvas.instructure.com")
    
    config = {
        platform_url: [{
            "default": True,
            "client_id": client_id,
            "auth_login_url": f"{platform_url}/login/oauth2/auth",
            "auth_token_url": f"{platform_url}/login/oauth2/token",
            "auth_audience": f"{platform_url}/login/oauth2/token",
            "key_set_url": f"{platform_url}/api/lti/security/jwks",
            "private_key": private_key,
            "public_key": public_key,
            "deployment_ids": [deployment_id]
        }]
    }
    
    return config

# Initialize tool configuration
LTI_CONFIG = get_lti_config()
tool_conf = ToolConfDict(LTI_CONFIG)

# Load keys from environment variables
def load_keys_from_env():
    """Load RSA keys from environment variables."""
    private_key = os.getenv("LTI_PRIVATE_KEY")
    public_key = os.getenv("LTI_PUBLIC_KEY")
    
    if not private_key or not public_key:
        print("⚠️  RSA keys not found in environment variables.")
        print("ℹ️  Set LTI_PRIVATE_KEY and LTI_PUBLIC_KEY environment variables.")
        return False
    
    try:
        # Set keys for each issuer
        for issuer in LTI_CONFIG:
            for config in LTI_CONFIG[issuer]:
                tool_conf.set_private_key(issuer, private_key, config["client_id"])
                tool_conf.set_public_key(issuer, public_key, config["client_id"])
        
        print("✅ RSA keys loaded from environment variables")
        return True
    except Exception as e:
        print(f"❌ Error loading keys: {e}")
        return False

# Load keys on startup
keys_loaded = load_keys_from_env()

# Pydantic models for request/response
class LTILaunchResponse(BaseModel):
    success: bool
    message: str
    launch_data: Dict[str, Any] = {}

class ErrorResponse(BaseModel):
    error: str
    message: str

# Utility functions
def get_launch_url(request: Request) -> str:
    """Get the launch URL for the current request."""
    return str(request.url_for("launch"))

def get_login_url(request: Request) -> str:
    """Get the login URL for the current request."""
    return str(request.url_for("login"))

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page with LTI launch information."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login(
    request: Request,
    target_link_uri: Optional[str] = None,
    login_hint: Optional[str] = None,
    lti_message_hint: Optional[str] = None
):
    """
    Handle OIDC login request from LTI platform.
    """
    if not keys_loaded:
        raise HTTPException(status_code=503, detail="LTI not configured. Missing RSA keys.")
    
    try:
        # Create OIDC login handler
        oidc_login = FastAPIOIDCLogin(
            request=request,
            tool_config=tool_conf
        )
        
        # Get the launch URL (where the platform will redirect after login)
        launch_url = target_link_uri or get_launch_url(request)
        
        # Perform redirect back to platform
        redirect_obj = oidc_login.get_redirect_object()
        redirect_url = redirect_obj.get_redirect_url()
        
        # Store launch data for later use
        session_service = FastAPISessionService(request)
        session_service.save_state_params(
            redirect_obj.get_state(),
            {
                "target_link_uri": target_link_uri,
                "login_hint": login_hint,
                "lti_message_hint": lti_message_hint
            }
        )
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OIDC Login failed: {str(e)}")

@app.post("/launch")
async def launch(request: Request):
    """
    Handle LTI message launch.
    """
    if not keys_loaded:
        raise HTTPException(status_code=503, detail="LTI not configured. Missing RSA keys.")
    
    try:
        # Create message launch handler
        message_launch = FastAPIMessageLaunch(
            request=request,
            tool_config=tool_conf
        )
        
        # Validate the launch
        launch_data = message_launch.get_launch_data()
        
        # Check launch type
        if message_launch.is_resource_launch():
            launch_type = "Resource Launch"
        elif message_launch.is_deep_link_launch():
            launch_type = "Deep Link Launch"
        else:
            launch_type = "Unknown Launch"
        
        # Check available services
        services = []
        if message_launch.has_ags():
            services.append("Assignments and Grades Service")
        if message_launch.has_nrps():
            services.append("Names and Roles Service")
        
        # Return launch data
        return {
            "success": True,
            "launch_type": launch_type,
            "services": services,
            "launch_data": launch_data,
            "user": launch_data.get("https://purl.imsglobal.org/spec/lti/claim/user", {}),
            "context": launch_data.get("https://purl.imsglobal.org/spec/lti/claim/context", {}),
            "resource_link": launch_data.get("https://purl.imsglobal.org/spec/lti/claim/resource_link", {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Launch failed: {str(e)}")

@app.get("/launch", response_class=HTMLResponse)
async def launch_page(request: Request):
    """Launch page that displays LTI information."""
    return templates.TemplateResponse("launch.html", {"request": request})

@app.get("/jwks")
async def jwks():
    """JSON Web Key Set endpoint for LTI platform verification."""
    if not keys_loaded:
        raise HTTPException(status_code=503, detail="RSA keys not configured. Set LTI_PRIVATE_KEY and LTI_PUBLIC_KEY environment variables.")
    
    try:
        # Get the first issuer's public key
        issuer = list(LTI_CONFIG.keys())[0]
        config = LTI_CONFIG[issuer][0]
        
        public_key = config.get("public_key")
        if not public_key:
            raise HTTPException(status_code=500, detail="Public key not found in configuration")
        
        # Generate JWKS
        from pylti1p3.registration import Registration
        reg = Registration()
        reg.set_tool_public_key(public_key)
        
        return {"keys": reg.get_jwks()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JWKS generation failed: {str(e)}")

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "lti_configured": keys_loaded,
        "environment": os.getenv("VERCEL_ENV", "development")
    }

# Error handlers
@app.exception_handler(404)
async def not_found(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def internal_error(request: Request, exc):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
