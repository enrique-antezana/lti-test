# Vercel Deployment Troubleshooting

## 🚨 Current Issue: Pip Installation Error

You're encountering a pip installation error during Vercel deployment. Here are several solutions to try:

## 🔧 Solution 1: Use Simple Requirements (Recommended)

Try using the simplified requirements file:

```bash
# Copy the simple requirements
cp requirements-vercel-simple.txt requirements-vercel.txt

# Deploy to Vercel
vercel
```

## 🔧 Solution 2: Test Basic Deployment First

Test if the basic FastAPI deployment works without pylti1p3:

```bash
# Use minimal requirements
cp requirements-minimal.txt requirements-vercel.txt

# Use test app
cp api/test-index.py api/index.py

# Deploy to Vercel
vercel
```

## 🔧 Solution 3: Use Local Package Copy

If the published package is causing issues, use your local package:

```bash
# Create a script to copy your local package
cat > copy_package.sh << 'EOF'
#!/bin/bash
mkdir -p pylti1p3_local
cp -r ../../pylti1p3/* pylti1p3_local/
touch pylti1p3_local/__init__.py

cat > requirements-vercel.txt << 'INNER_EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
jinja2==3.1.2
python-multipart==0.0.6
pydantic==2.5.0
cryptography==41.0.7
./pylti1p3_local
INNER_EOF

echo "✅ Local package copied and requirements updated"
EOF

chmod +x copy_package.sh
./copy_package.sh

# Deploy to Vercel
vercel
```

## 🔧 Solution 4: Check Python Version

The error might be related to Python version compatibility. Try updating `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "runtime": "python3.8"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

## 🔧 Solution 5: Manual Package Installation

If all else fails, you can manually install the package during build:

```bash
# Create a build script
cat > vercel-build.sh << 'EOF'
#!/bin/bash
echo "Installing dependencies..."
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 jinja2==3.1.2 python-multipart==0.0.6 pydantic==2.5.0

echo "Installing local pylti1p3..."
mkdir -p pylti1p3_local
cp -r ../../pylti1p3/* pylti1p3_local/
touch pylti1p3_local/__init__.py
pip install -e pylti1p3_local

echo "Build completed"
EOF

chmod +x vercel-build.sh
```

Then update `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "buildCommand": "./vercel-build.sh"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

## 🔍 Debugging Steps

1. **Check Vercel logs** in the dashboard for more detailed error messages
2. **Try deploying locally** first: `vercel --dev`
3. **Check package compatibility** with Python 3.9/3.8
4. **Verify requirements format** - no hidden characters

## 📋 Recommended Order

1. Try **Solution 1** (Simple Requirements)
2. If that fails, try **Solution 2** (Test Basic Deployment)
3. If basic deployment works, try **Solution 3** (Local Package)
4. If still failing, try **Solution 4** (Python Version)
5. Last resort: **Solution 5** (Manual Installation)

## 🎯 Success Indicators

- ✅ Build completes without errors
- ✅ App is accessible at your Vercel URL
- ✅ Health endpoint returns `{"status": "healthy"}`
- ✅ API documentation is available at `/docs`

Let me know which solution works for you!
