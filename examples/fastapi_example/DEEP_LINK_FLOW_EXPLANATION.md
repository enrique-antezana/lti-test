# Deep Link Flow Explanation

## Problem with Previous Approach

The previous implementation had issues with the "Missing state param" error because:

1. **Session Storage Issues**: The LTI launch context wasn't being preserved properly in the session
2. **Complex State Management**: Trying to manually reconstruct the deep link context was error-prone
3. **Different from Working Examples**: The approach didn't follow the proven pattern from the Flask example

## New Approach (Based on Flask App)

The new implementation follows the exact same pattern as the working Flask example:

### 1. Single Launch Endpoint

```python
@app.post("/api/launch")
async def launch(request: Request):
    # ... launch validation ...

    if message_launch.is_deep_link_launch():
        # Render character selection with launch context
        return templates.TemplateResponse("character_selection.html", {
            "request": request,
            "is_deep_link": True,
            "launch_data": launch_data,
            "launch_id": message_launch.get_launch_id()  # Key difference!
        })
```

### 2. Character Selection with Launch ID

The character selection page now receives the `launch_id` and includes it in the form:

```html
<form
  id="character-selection-form"
  method="POST"
  action="/api/character-selection"
>
  <input type="hidden" name="launch_id" value="{{ launch_id }}" />
</form>
```

### 3. Form Submission Handler

```python
@app.post("/api/character-selection")
async def handle_character_selection(request: Request):
    # Get launch_id and selected characters
    launch_id = form_data.get('launch_id')
    selected_character_ids = form_data.getlist('selected_characters')

    # Redirect to configuration endpoint
    redirect_url = f"/api/configure/{launch_id}?{character_params}"
    return RedirectResponse(url=redirect_url)
```

### 4. Configuration Endpoint (Key Innovation)

```python
@app.get("/api/configure/{launch_id}")
async def configure_deep_link(request: Request, launch_id: str):
    # Use FastAPIMessageLaunch.from_cache() - same as Flask!
    message_launch = FastAPIMessageLaunch.from_cache(
        launch_id,
        fastapi_request,
        tool_conf,
        launch_data_storage=launch_data_storage
    )

    # Create deep link resources
    deep_link = message_launch.get_deep_link()
    # ... create resources ...

    # Return deep link response
    return HTMLResponse(content=deep_link.output_response_form(resources))
```

## Key Differences from Previous Approach

| Aspect                 | Previous Approach     | New Approach                     |
| ---------------------- | --------------------- | -------------------------------- |
| **State Storage**      | Session storage       | Launch ID + cache                |
| **Deep Link Creation** | Manual reconstruction | `message_launch.get_deep_link()` |
| **Launch Context**     | Stored in session     | Retrieved via `from_cache()`     |
| **Pattern**            | Custom implementation | Follows Flask example exactly    |
| **Reliability**        | Error-prone           | Proven to work                   |

## Why This Works

1. **`from_cache()` Method**: This is the same method used in the working Flask example. It properly reconstructs the message launch context from the cached launch data.

2. **Launch ID**: The launch ID is a unique identifier that allows the system to retrieve the complete launch context, including all the necessary LTI parameters.

3. **Proven Pattern**: This exact pattern is used in the working Flask example, so we know it works correctly.

4. **No Manual State Management**: We don't try to manually reconstruct the LTI context - we let PyLTI1p3 handle it.

## Flow Diagram

```
LTI Platform
    ↓ (deep link launch)
/api/launch
    ↓ (detects deep link, renders template with launch_id)
character_selection.html
    ↓ (user selects characters, submits form)
/api/character-selection
    ↓ (redirects with selected characters)
/api/configure/{launch_id}
    ↓ (uses from_cache() to get launch context)
Deep Link Response
    ↓ (submits back to LMS)
LTI Platform
```

## Testing

Run the test script to verify the flow:

```bash
python test_deep_link_flow.py
```

This will test:

- Character selection page loading
- Character API functionality
- Character detail pages
- Deep link configuration endpoint
- Form submission

## Debugging

Look for these debug messages in the server logs:

```
###################### Deep Link Launch Detected - Launch data: {...}
###################### Configure Deep Link - Launch ID: {launch_id}
###################### Attempting to load from cache with launch_id: {launch_id}
###################### Successfully loaded message launch from cache
```

## Benefits

1. **Reliability**: Uses the same proven pattern as the working Flask example
2. **Simplicity**: No complex session management or manual state reconstruction
3. **Maintainability**: Follows established patterns in the PyLTI1p3 library
4. **Debugging**: Clear separation of concerns and better error handling

This approach should resolve the "Missing state param" error and provide a robust deep link implementation.
