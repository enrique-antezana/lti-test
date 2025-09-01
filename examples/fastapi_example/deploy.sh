#!/bin/bash

# FastAPI LTI App Deployment Script for Vercel

echo "🚀 Deploying FastAPI LTI App to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ vercel.json not found. Make sure you're in the fastapi_example directory."
    exit 1
fi

# Check if RSA keys exist (optional for deployment)
if [ ! -f "private.key" ] || [ ! -f "public.key" ]; then
    echo "⚠️  RSA keys not found locally."
    echo "ℹ️  Make sure to set LTI_PRIVATE_KEY and LTI_PUBLIC_KEY environment variables in Vercel."
fi

# Deploy to Vercel
echo "📦 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at the URL shown above."
echo ""
echo "📋 Next steps:"
echo "1. Set environment variables in Vercel dashboard:"
echo "   - LTI_CLIENT_ID"
echo "   - LTI_DEPLOYMENT_ID" 
echo "   - LTI_PRIVATE_KEY"
echo "   - LTI_PUBLIC_KEY"
echo "2. Update your LTI platform with the new URLs"
echo "3. Test the deployment"
