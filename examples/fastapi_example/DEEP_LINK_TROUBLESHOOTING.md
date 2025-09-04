# Deep Link Troubleshooting Guide

## Issue: "Missing state param" Error

If you're getting the error `{"detail":"Deep link creation failed: Missing state param"}`, this means the LTI launch context is not being preserved properly when submitting the character selection form.

## Root Cause

The issue occurs because:

1. The deep link launch creates a valid LTI context
2. When you submit the character selection form, the LTI state parameters are lost
3. The deep link handler can't validate the request without the proper LTI context

## Solution

The current implementation uses session storage to preserve the LTI launch data. Here's how it works:

1. **Deep Link Launch**: When an LTI platform initiates a deep link launch, the launch data is stored in the session
2. **Character Selection**: The character selection page loads without requiring LTI context
3. **Deep Link Creation**: When you submit character selections, the stored launch data is retrieved from the session

## Debugging Steps

### 1. Check Server Logs

Look for these debug messages in your server logs:

```
###################### Deep Link Launch Detected - Launch data: {...}
###################### Deep Link Handler - Launch data: {...}
```

### 2. Verify Session Storage

The launch data should be stored with the key `"deep_link_launch"` in the session.

### 3. Test the Flow

1. **Start the server**:

   ```bash
   cd examples/fastapi_example
   python -m uvicorn api.main:app --reload --port 8000
   ```

2. **Test basic endpoints**:

   ```bash
   python test_deep_link_manual.py
   ```

3. **Test character selection page**:
   - Visit: http://localhost:8000/character-selection
   - You should see the character selection interface

### 4. LTI Platform Configuration

Make sure your LTI platform is configured with:

- **Deep Link URL**: `http://your-domain.com/api/launch`
- **Launch URL**: `http://your-domain.com/api/launch`
- **Login URL**: `http://your-domain.com/api/login`

## Alternative Solutions

If session storage doesn't work in your environment, here are alternative approaches:

### Option 1: URL Parameters

Pass the LTI state through URL parameters (less secure but simpler):

```python
# In the deep link launch handler
return RedirectResponse(url=f"/character-selection?lti_state={encoded_state}")

# In the character selection handler
lti_state = request.query_params.get('lti_state')
# Decode and use the state
```

### Option 2: Database Storage

Store the launch data in a database with a unique key:

```python
# Store with a unique key
launch_id = str(uuid.uuid4())
# Store in database with launch_id
# Pass launch_id in form submission
```

### Option 3: JWT Token

Encode the launch data in a JWT token:

```python
# Create a JWT with launch data
jwt_token = jwt.encode(launch_data, secret_key, algorithm="HS256")
# Pass token in form submission
```

## Testing Without LTI Platform

To test the deep link functionality without a full LTI platform:

1. **Mock the deep link launch** by creating a test endpoint that simulates the LTI launch
2. **Use the character selection page directly** at `/character-selection`
3. **Test the character detail pages** at `/character-detail/{id}`

## Common Issues

### Issue: Session not persisting

**Solution**: Make sure your FastAPI app has session middleware configured:

```python
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
```

### Issue: CORS errors

**Solution**: Add CORS middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: HTTPS required

**Solution**: LTI platforms often require HTTPS. Use a tool like ngrok for local testing:

```bash
ngrok http 8000
# Use the HTTPS URL provided by ngrok
```

## Verification

To verify the deep link functionality is working:

1. Check that the character selection page loads
2. Verify that character selection works (cards highlight when clicked)
3. Confirm that the "Create Deep Links" button is enabled when characters are selected
4. Check server logs for successful deep link creation
5. Verify that the deep link response is generated and submitted back to the LMS

## Need Help?

If you're still experiencing issues:

1. Check the server logs for error messages
2. Verify your LTI platform configuration
3. Test with a simple LTI platform like LTI 1.3 Test Tool
4. Review the PyLTI1p3 documentation for deep linking
5. Check that your RSA keys are properly configured
