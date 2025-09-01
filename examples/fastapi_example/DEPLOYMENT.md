# Deploying FastAPI LTI App to Vercel

This guide shows how to deploy the FastAPI LTI 1.3 example to Vercel.

## 🚀 Quick Deployment

### Option 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub**:

   ```bash
   git init
   git add .
   git commit -m "Initial FastAPI LTI app"
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```

2. **Connect to Vercel**:

   - Go to [vercel.com](https://vercel.com)
   - Sign in with GitHub
   - Click "New Project"
   - Import your repository
   - Vercel will auto-detect the FastAPI app

3. **Configure Environment Variables** (if needed):
   - In Vercel dashboard, go to Settings → Environment Variables
   - Add any required environment variables

### Option 2: Deploy with Vercel CLI

1. **Install Vercel CLI**:

   ```bash
   npm install -g vercel
   ```

2. **Deploy**:

   ```bash
   cd examples/fastapi_example
   vercel
   ```

3. **Follow the prompts**:
   - Link to existing project or create new one
   - Choose deployment settings

## ⚙️ Configuration Files

### `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.9"
  },
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  }
}
```

### `api/index.py`

```python
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Export the FastAPI app for Vercel
handler = app
```

## 🔧 Important Considerations

### 1. **RSA Keys for Production**

- **Don't commit RSA keys to Git** (they're in .gitignore)
- **Generate keys on Vercel** using environment variables
- **Or use a key management service** like AWS Secrets Manager

### 2. **Environment Variables**

Set these in Vercel dashboard:

```bash
# LTI Configuration
LTI_CLIENT_ID=your_client_id
LTI_DEPLOYMENT_ID=your_deployment_id
LTI_PRIVATE_KEY=your_private_key_content
LTI_PUBLIC_KEY=your_public_key_content
```

### 3. **Update main.py for Production**

```python
import os

# Load configuration from environment variables
LTI_CONFIG = {
    "https://canvas.instructure.com": [{
        "default": True,
        "client_id": os.getenv("LTI_CLIENT_ID", "your_client_id"),
        "auth_login_url": "https://canvas.instructure.com/login/oauth2/auth",
        "auth_token_url": "https://canvas.instructure.com/login/oauth2/token",
        "auth_audience": "https://canvas.instructure.com/login/oauth2/token",
        "key_set_url": "https://canvas.instructure.com/api/lti/security/jwks",
        "private_key": os.getenv("LTI_PRIVATE_KEY"),
        "public_key": os.getenv("LTI_PUBLIC_KEY"),
        "deployment_ids": [os.getenv("LTI_DEPLOYMENT_ID", "your_deployment_id")]
    }]
}
```

### 4. **Static Files**

- Vercel handles static files automatically
- Make sure `static/` directory is included in your deployment

## 🌐 Post-Deployment

### 1. **Update LTI Platform Configuration**

Update your LMS (Canvas, Moodle, etc.) with:

- **Login URL**: `https://your-app.vercel.app/login`
- **Launch URL**: `https://your-app.vercel.app/launch`
- **Public Key**: Content from your public key

### 2. **Test the Deployment**

- Visit: `https://your-app.vercel.app/`
- Check API docs: `https://your-app.vercel.app/docs`
- Test health endpoint: `https://your-app.vercel.app/health`

## 🚨 Limitations

### Vercel Serverless Limitations:

- **Cold starts**: First request may be slower
- **Function timeout**: 30 seconds max (can be increased to 60s on Pro)
- **Memory**: 1024MB max
- **No persistent storage**: Use external services for sessions

### Solutions:

- **Use Redis** for session storage (Redis Cloud, Upstash)
- **Use database** for configuration (PlanetScale, Supabase)
- **Optimize cold starts** with keep-alive strategies

## 🔄 Continuous Deployment

Once connected to GitHub:

- **Automatic deployments** on every push
- **Preview deployments** for pull requests
- **Environment-specific** configurations

## 📊 Monitoring

Vercel provides:

- **Function logs** in dashboard
- **Performance metrics**
- **Error tracking**
- **Analytics**

## 🆘 Troubleshooting

### Common Issues:

1. **Import errors**:

   - Check Python path in `api/index.py`
   - Verify all dependencies in `requirements.txt`

2. **Timeout errors**:

   - Increase `maxDuration` in `vercel.json`
   - Optimize your code for faster execution

3. **Environment variables**:

   - Check variable names match exactly
   - Ensure they're set in Vercel dashboard

4. **Static files not loading**:
   - Verify `static/` directory is included
   - Check file paths in templates

## 🎉 Success!

Once deployed, your FastAPI LTI app will be available at:
`https://your-app.vercel.app/`

The app will automatically scale and handle traffic spikes, making it perfect for production LTI tools!
