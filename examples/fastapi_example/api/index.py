"""
Vercel serverless function entry point for FastAPI LTI app
"""

import sys
import os

# Add the parent directory to the Python path so we can import pylti1p3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use production version for Vercel deployment
from main_production import app

# Export the FastAPI app for Vercel
handler = app
