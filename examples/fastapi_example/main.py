"""
FastAPI LTI 1.3 Example Application

This example demonstrates how to integrate PyLTI1p3 with FastAPI.
It includes OIDC login, message launch, and basic LTI functionality.
"""

import os
import json
from typing import Dict, Any
from fastapi import FastAPI, Request, Form, HTTPException, Depends
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
from pylti1p3.launch_data_storage.cache import CacheDataStorage

# Create FastAPI app
app = FastAPI(
    title="LTI 1.3 FastAPI Example",
    description="Example LTI 1.3 tool built with FastAPI and PyLTI1p3",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# LTI Configuration
# In production, load this from environment variables or database
LTI_CONFIG = {
    "https://canvas.instructure.com": [{
        "default": True,
        "client_id": "10000000000001",
        "auth_login_url": "https://lms.valis.jala-one.com/login/oauth2/auth",
        "auth_token_url": "https://lms.valis.jala-one.com/login/oauth2/token",
        "key_set_url": "https://lms.valis.jala-one.com/api/lti/security/jwks",
        "private_key_file": "private.key",
        "public_key_file": "public.key",
        "deployment_ids": ["1:d89e331c21d21263871f13e1c0744565df26572c", "2:8ea1541666cdcdf85d9aae194078dbe76077af87"]
    }]
}

# Initialize tool configuration
tool_conf = ToolConfDict(LTI_CONFIG)

# Launch data storage (similar to Flask example)
def get_launch_data_storage():
    """Get launch data storage instance."""
    # For FastAPI, we'll use a simple in-memory cache
    # In production, you might want to use Redis or database storage
    return CacheDataStorage()

# Load keys (in production, load from secure storage)
def load_keys():
    """Load private and public keys."""
    try:
        with open("private.key", "r") as f:
            private_key = f.read()
        with open("public.key", "r") as f:
            public_key = f.read()
        
        # Set keys for each issuer
        for issuer in LTI_CONFIG:
            for config in LTI_CONFIG[issuer]:
                tool_conf.set_private_key(issuer, private_key, config["client_id"])
                tool_conf.set_public_key(issuer, public_key, config["client_id"])
        
        return True
    except FileNotFoundError:
        print("Warning: Key files not found. LTI functionality will not work.")
        return False

# Load keys on startup (optional for basic functionality)
keys_loaded = load_keys()
if not keys_loaded:
    print("ℹ️  RSA keys not found. Run 'python generate_keys.py' to generate them.")
    print("ℹ️  The app will work for basic testing, but LTI functionality requires keys.")

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
    target_link_uri: str = None,
    login_hint: str = None,
    lti_message_hint: str = None
):
    """
    Handle OIDC login request from LTI platform.
    
    This endpoint receives the initial login request and redirects back to the platform
    with the necessary parameters for the LTI launch.
    """
    try:
        
         # iss=https%3A%2F%2Flms.valis.jala-one.com&login_hint=ad9e74438daf253e014e9eceb362c8783116a36a&client_id=10000000000006&lti_deployment_id=9%3Ad89e331c21d21263871f13e1c0744565df26572c&target_link_uri=https%3A%2F%2Ffastapi-example-xi.vercel.app%2Fapi%2Flaunch&lti_message_hint=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2ZXJpZmllciI6ImQ2MDNlZGNmMGFjMWRmMzJmZDY4NDU2YjU3ZWFmZjhjNTBkNGNkODBmMTA0OGVlNTEzZTQwZjM0ZTgzMWM2ZTA4NWI5ODQ4YmRhODE2MDNkMWZhNDJhZDk2NzlhMTEyMDJhNzEzYWYyZWRhZTEyNjRiMzk2MDRmMDNhYzI2NDdhIiwiY2FudmFzX2RvbWFpbiI6Imxtcy52YWxpcy5qYWxhLW9uZS5jb20iLCJjb250ZXh0X3R5cGUiOiJDb3Vyc2UiLCJjb250ZXh0X2lkIjoxMDAwMDAwMDAwMDAwMSwiY2FudmFzX2xvY2FsZSI6ImVuIiwiaW5jbHVkZV9zdG9yYWdlX3RhcmdldCI6dHJ1ZSwiZXhwIjoxNzU2ODYyNDkxfQ.EA3A3S8Gat2aHyOArHO5vM_7bf9jml_fXeavyXMdQho&canvas_environment=prod&canvas_region=not_configured&deployment_id=9%3Ad89e331c21d21263871f13e1c0744565df26572c&lti_storage_target=post_message_forwarding
        target_link_uri = target_link_uri or request.query_params.get('target_link_uri')
        print(f"###################### /login/ target_link_uri: {target_link_uri}")
        # Get the launch URL (where the platform will redirect after login)
        launch_url = target_link_uri or get_launch_url(request)
        print(f"###################### /login/ launch_url: {launch_url}")
        launch_data_storage = get_launch_data_storage()
        # Create OIDC login handler
        oidc_login = FastAPIOIDCLogin(
            request=request,
            tool_config=tool_conf,
            launch_data_storage=launch_data_storage
        )
        
        
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
    
    This endpoint receives the LTI launch message after successful OIDC login.
    """
    try:
        launch_data_storage = get_launch_data_storage()
        
        # Create message launch handler
        message_launch = FastAPIMessageLaunch(
            request=request,
            tool_config=tool_conf,
            launch_data_storage=launch_data_storage
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
        raise HTTPException(status_code=503, detail="RSA keys not configured. Run 'python generate_keys.py' to generate keys.")
    
    try:
        # Get the first issuer's public key
        issuer = list(LTI_CONFIG.keys())[0]
        config = LTI_CONFIG[issuer][0]
        
        with open(config["public_key_file"], "r") as f:
            public_key = f.read()
        
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
    return {"status": "healthy", "lti_configured": bool(tool_conf)}

# # Error handlers
# @app.exception_handler(404)
# async def not_found(request: Request, exc):
#     return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

# @app.exception_handler(500)
# async def internal_error(request: Request, exc):
#     return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

# if __name__ == "__main__":
#     import uvicorn
    
#     print("🚀 Starting FastAPI LTI 1.3 Example Server...")
#     print("📋 Available endpoints:")
#     print("   • Main page: http://localhost:4000/")
#     print("   • API docs: http://localhost:4000/docs")
#     print("   • Health check: http://localhost:4000/health")
#     print("   • JWKS endpoint: http://localhost:4000/jwks")
#     print("   • Login endpoint: http://localhost:4000/login")
#     print("   • Launch endpoint: http://localhost:4000/launch")
    
#     if not keys_loaded:
#         print("\n⚠️  WARNING: RSA keys not found!")
#         print("   Run 'python generate_keys.py' to generate them.")
#         print("   The app will work for basic testing, but LTI functionality requires keys.")
    
#     print("\n🌐 Server starting on http://localhost:4000")
#     print("   Press Ctrl+C to stop the server")
    
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=3030,
#         reload=True,
#         log_level="info"
#     )
