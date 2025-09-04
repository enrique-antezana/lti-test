"""
Simple test FastAPI app for Vercel deployment testing
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Create FastAPI app
app = FastAPI(
    title="Test FastAPI App",
    description="Simple test app for Vercel deployment",
    version="1.0.0"
)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>Test App</title></head>
        <body>
            <h1>🚀 Test FastAPI App</h1>
            <p>If you can see this, FastAPI deployment is working!</p>
            <p><a href="/health">Health Check</a></p>
            <p><a href="/docs">API Documentation</a></p>
        </body>
    </html>
    """

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "FastAPI is working!"}
