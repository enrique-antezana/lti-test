"""
FastAPI LTI 1.3 Example Application

This example demonstrates how to integrate PyLTI1p3 with FastAPI.
It includes OIDC login, message launch, and basic LTI functionality.
"""

import os
import json
import time
import httpx
from typing import Dict, Any, List
from fastapi import FastAPI, Form, HTTPException, Depends, Request
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
    FastAPICookieService,
    FastAPICacheDataStorage
)
from pylti1p3.contrib.fastapi import FastAPIRequest
from pylti1p3.deep_link_resource import DeepLinkResource

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
# "default": true,
#       "client_id": "10000000000005",
#       "auth_login_url": "https://lms.valis.jala-one.com/api/lti/authorize_redirect",
#       "auth_token_url": "https://lms.valis.jala-one.com/login/oauth2/token",
#       "key_set_url": "https://lms.valis.jala-one.com/api/lti/security/jwks",
#       "key_set": null,
#       "private_key_file": "/var/task/api/config/private.key",
#       "public_key_file": "/var/task/api/config/public.key",
#       "deployment_ids": [
#         "6:8ea1541666cdcdf85d9aae194078dbe76077af87",
#         "7:d89e331c21d21263871f13e1c0744565df26572c",
#         "8:8ea1541666cdcdf85d9aae194078dbe76077af87"
#       ]
LTI_CONFIG = {
    "https://lms.valis.jala-one.com": [{
        "default": True,
        "client_id": "10000000000006",
        "auth_login_url": "https://lms.valis.jala-one.com/api/lti/authorize_redirect",
        "auth_token_url": "https://lms.valis.jala-one.com/login/oauth2/token",
        "auth_audience": "https://lms.valis.jala-one.com/login/oauth2/token",
        "key_set_url": "https://lms.valis.jala-one.com/api/lti/security/jwks",
        "private_key_file": "private.key",
        "public_key_file": "public.key",
        "deployment_ids": ["9:d89e331c21d21263871f13e1c0744565df26572c", "10:8ea1541666cdcdf85d9aae194078dbe76077af87"]
    }]
}

# Initialize tool configuration
tool_conf = ToolConfDict(LTI_CONFIG)

# Simple in-memory cache implementation (Vercel-compatible)
class SimpleCache:
    """
    Simple in-memory cache with expiration support.
    Compatible with Vercel serverless functions.
    Similar to Flask-Caching's 'simple' cache type.
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

# Initialize cache instance
# Cache configuration similar to Flask's CACHE_TYPE="simple" with CACHE_DEFAULT_TIMEOUT=600
cache = SimpleCache()

def get_launch_data_storage():
    """Get launch data storage instance with proper cache support."""
    # Use FastAPICacheDataStorage with our simple cache implementation
    # This provides the same functionality as Flask's FlaskCacheDataStorage
    return FastAPICacheDataStorage(cache)

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

class CharacterData(BaseModel):
    id: int
    name: str
    status: str
    species: str
    type: str
    gender: str
    origin: Dict[str, Any]
    location: Dict[str, Any]
    image: str
    episode: List[str]
    url: str
    created: str

class DeepLinkRequest(BaseModel):
    characters: List[CharacterData]

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

@app.get("/api/login")
@app.post("/api/login")
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
        # Handle both GET and POST requests
        if request.method == "GET":
            # For GET requests, parameters come from query parameters
            print("###################### /login/ GET request - Query parameters:")
            for key, value in request.query_params.items():
                print(f"  {key}: {value}")
            print("###################### /login/ End query parameters")
            
            target_link_uri = request.query_params.get('target_link_uri')
            form_data = {}  # Empty form data for GET requests
        else:
            # For POST requests, parameters come from form data
            form_data = await request.form()
            
            print("###################### /login/ POST request - Form data:")
            for key, value in form_data.items():
                print(f"  {key}: {value}")
            print("###################### /login/ End form data")
            
            target_link_uri = form_data.get('target_link_uri')
        
        print(f"###################### /login/ target_link_uri: {target_link_uri}")
        # Get the launch URL (where the platform will redirect after login)
        launch_data_storage = get_launch_data_storage()
        fastapi_request = FastAPIRequest(request, form_data)
        launch_url = target_link_uri
        print(f"###################### /login/ launch_url: {launch_url}")
        # Create OIDC login handler
        oidc_login = FastAPIOIDCLogin(
            request=fastapi_request,
            tool_config=tool_conf,
            launch_data_storage=launch_data_storage
        )
        
        return oidc_login.enable_check_cookies().redirect(launch_url)
        # # Get the launch URL (where the platform will redirect after login)
        # launch_url = target_link_uri or get_launch_url(fastapi_request)
        
        # # Perform redirect back to platform
        # redirect_obj = oidc_login.get_redirect_object(launch_url)
        # redirect_url = redirect_obj.get_redirect_url()
        # print(launch_url, redirect_url)
        # # Store launch data for later use
        # session_service = FastAPISessionService(request)
        # session_service.save_state_params(
        #     redirect_obj.get_state(),
        #     {
        #         "target_link_uri": target_link_uri,
        #         "login_hint": login_hint,
        #         "lti_message_hint": lti_message_hint
        #     }
        # )
        
        # return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OIDC Login failed: {str(e)}")

@app.post("/api/launch")
async def launch(request: Request):
    """
    Handle LTI message launch.
    
    This endpoint receives the LTI launch message after successful OIDC login.
    """
    try:
        launch_data_storage = get_launch_data_storage()
        form_data = await request.form()
            
        print("###################### /login/ POST request - Form data:")
        for key, value in form_data.items():
            print(f"  {key}: {value}")
        print("###################### /login/ End form data")
        
        target_link_uri = form_data.get('target_link_uri')
        
        print(f"###################### /login/ target_link_uri: {target_link_uri}")
        # Get the launch URL (where the platform will redirect after login)
        fastapi_request = FastAPIRequest(request, form_data)
        # Create message launch handler
        message_launch = FastAPIMessageLaunch(
            request=fastapi_request,
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
            print(f"###################### Deep Link Launch Detected - Launch data: {launch_data}")
            
            # Handle deep link launch - show character selection with launch context
            return templates.TemplateResponse("character_selection.html", {
                "request": request,
                "is_deep_link": True,
                "launch_data": launch_data,
                "launch_id": message_launch.get_launch_id()
            })
        else:
            launch_type = "Unknown Launch"
        
        # Check available services
        services = []
        if message_launch.has_ags():
            services.append("Assignments and Grades Service")
        if message_launch.has_nrps():
            services.append("Names and Roles Service")
        
        # Initialize members as None
        members = None
        
        # Get members if NRPS is available
        if message_launch.has_nrps():
            try:
                # Get the NRPS service
                nrps = message_launch.get_nrps()
                # Then get members from the service
                members = nrps.get_members()
                print(f"Members: {members}")
            except Exception as e:
                print(f"Error getting members: {e}")
                members = None
        else:
            print("Names and Roles Service not available")
        
        # Return launch data
        return {
            "success": True,
            "launch_type": launch_type,
            "services": services,
            "launch_data": launch_data,
            "user": launch_data.get("https://purl.imsglobal.org/spec/lti/claim/user", {}),
            "context": launch_data.get("https://purl.imsglobal.org/spec/lti/claim/context", {}),
            "resource_link": launch_data.get("https://purl.imsglobal.org/spec/lti/claim/resource_link", {}),
            "members": members
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Launch failed: {str(e)}")

@app.get("/api/launch", response_class=HTMLResponse)
async def launch_page(request: Request):
    """Launch page that displays LTI information."""
    return templates.TemplateResponse("launch.html", {"request": request})

@app.get("/api/characters")
async def get_characters():
    """Fetch the first 5 characters from Rick and Morty API."""
    try:
        async with httpx.AsyncClient() as client:
            # Fetch first 5 characters (IDs 1-5)
            characters = []
            for character_id in range(1, 6):
                response = await client.get(f"https://rickandmortyapi.com/api/character/{character_id}")
                if response.status_code == 200:
                    character_data = response.json()
                    characters.append(character_data)
                else:
                    print(f"Failed to fetch character {character_id}: {response.status_code}")
            
            return characters
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch characters: {str(e)}")

@app.get("/character-selection", response_class=HTMLResponse)
async def character_selection_page(request: Request):
    """Character selection page for deep link creation."""
    return templates.TemplateResponse("character_selection.html", {"request": request})

@app.get("/api/configure/{launch_id}", response_class=HTMLResponse)
@app.post("/api/configure/{launch_id}", response_class=HTMLResponse)
async def configure_deep_link(request: Request, launch_id: str):
    """Configure deep link resources for selected characters."""
    try:
        # Get form data to see which characters were selected
        form_data = await request.form()
        selected_character_ids = form_data.getlist('selected_characters') if form_data else []
        
        # If no characters selected via form, get from query params
        if not selected_character_ids:
            selected_character_ids = request.query_params.getlist('selected_characters')
        
        # If still no characters selected, use all 5 characters
        if not selected_character_ids:
            selected_character_ids = ['1', '2', '3', '4', '5']
        
        print(f"###################### Configure Deep Link - Launch ID: {launch_id}")
        print(f"###################### Selected Characters: {selected_character_ids}")
        
        # Recreate the message launch from cache (like Flask app does)
        launch_data_storage = get_launch_data_storage()
        fastapi_request = FastAPIRequest(request, {})
        
        print(f"###################### Attempting to load from cache with launch_id: {launch_id}")
        message_launch = FastAPIMessageLaunch.from_cache(
            launch_id, 
            fastapi_request, 
            tool_conf,
            launch_data_storage=launch_data_storage
        )
        print(f"###################### Successfully loaded message launch from cache")
        
        if not message_launch.is_deep_link_launch():
            raise HTTPException(status_code=400, detail="Must be a deep link launch!")
        
        # Get the deep link object
        deep_link = message_launch.get_deep_link()
        
        # Fetch selected characters
        async with httpx.AsyncClient() as client:
            characters = []
            for character_id in selected_character_ids:
                response = await client.get(f"https://rickandmortyapi.com/api/character/{character_id}")
                if response.status_code == 200:
                    character_data = response.json()
                    characters.append(character_data)
        
        # Create deep link resources for each character
        deep_link_resources = []
        for character in characters:
            resource = DeepLinkResource()
            resource.set_title(f"Rick and Morty Character: {character['name']}")
            resource.set_url(f"{str(request.base_url)}api/character-detail")
            resource.set_icon_url(character['image'])
            resource.set_custom_params({
                "character_id": str(character['id']),
                "character_name": character['name'],
                "character_status": character['status'],
                "character_species": character['species']
            })
            deep_link_resources.append(resource)
        
        # Generate the deep link response
        response_html = deep_link.output_response_form(deep_link_resources)
        return HTMLResponse(content=response_html)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Deep link configuration failed: {str(e)}")

@app.post("/api/character-selection", response_class=HTMLResponse)
async def handle_character_selection(request: Request):
    """Handle character selection and redirect to configuration."""
    try:
        # Get form data
        form_data = await request.form()
        launch_id = form_data.get('launch_id')
        selected_character_ids = form_data.getlist('selected_characters')
        
        if not launch_id:
            raise HTTPException(status_code=400, detail="Missing launch_id")
        
        # Redirect to configuration endpoint with selected characters
        character_params = "&".join([f"selected_characters={id}" for id in selected_character_ids])
        redirect_url = f"/api/configure/{launch_id}?{character_params}"
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Character selection failed: {str(e)}")

@app.get("/character-detail/{character_id}", response_class=HTMLResponse)
async def character_detail_get(request: Request, character_id: int):
    """Display character details for a specific character (GET method)."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://rickandmortyapi.com/api/character/{character_id}")
            if response.status_code == 200:
                character = response.json()
                return templates.TemplateResponse("character_detail.html", {
                    "request": request,
                    "character": character
                })
            else:
                raise HTTPException(status_code=404, detail="Character not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch character: {str(e)}")

@app.post("/api/character-detail", response_class=HTMLResponse)
async def character_detail_post(request: Request):
    """Display character details for a specific character (POST method with LTI launch)."""
    try:
        # Get form data for LTI launch
        form_data = await request.form()
        launch_data_storage = get_launch_data_storage()
        fastapi_request = FastAPIRequest(request, form_data)
        
        # Create message launch handler to get LTI data
        message_launch = FastAPIMessageLaunch(
            request=fastapi_request,
            tool_config=tool_conf,
            launch_data_storage=launch_data_storage
        )
        
        # Get launch data
        launch_data = message_launch.get_launch_data()
        
        # Extract character_id from LTI custom claims
        custom_claims = launch_data.get("https://purl.imsglobal.org/spec/lti/claim/custom", {})
        character_id = custom_claims.get("character_id")
        
        print(f"###################### Character Detail - Launch data: {launch_data}")
        print(f"###################### Character Detail - Custom claims: {custom_claims}")
        print(f"###################### Character Detail - Character ID: {character_id}")
        
        if not character_id:
            raise HTTPException(status_code=400, detail="Missing character_id in LTI custom claims")
        
        try:
            character_id = int(character_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid character_id format")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://rickandmortyapi.com/api/character/{character_id}")
            if response.status_code == 200:
                character = response.json()
                return templates.TemplateResponse("character_detail.html", {
                    "request": request,
                    "character": character
                })
            else:
                raise HTTPException(status_code=404, detail="Character not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch character: {str(e)}")

@app.post("/api/create-deep-links")
async def create_deep_links(request: Request, deep_link_request: DeepLinkRequest):
    """Create deep links for selected characters."""
    try:
        # This endpoint would typically be called during a deep link launch
        # For now, we'll just return success - in a real implementation,
        # this would handle the deep link response generation
        
        # In a real deep link launch, you would:
        # 1. Get the deep link object from the message launch
        # 2. Create DeepLinkResource objects for each character
        # 3. Generate the deep link response
        
        return {
            "success": True,
            "message": f"Deep links created for {len(deep_link_request.characters)} characters",
            "characters": [char.name for char in deep_link_request.characters]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create deep links: {str(e)}")

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

# Error handlers
@app.exception_handler(404)
async def not_found(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def internal_error(request: Request, exc):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)
