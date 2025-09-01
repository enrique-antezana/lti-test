# FastAPI LTI 1.3 Example

This is a complete example of how to integrate PyLTI1p3 with FastAPI to create an LTI 1.3 tool.

## 🚀 Features

- **FastAPI Integration**: Modern, fast web framework with automatic API documentation
- **LTI 1.3 Support**: Full LTI 1.3 Advantage implementation
- **OpenID Connect**: Secure authentication flow
- **JWT Validation**: Cryptographic message verification
- **Pydantic Models**: Type-safe data validation
- **Template Rendering**: HTML templates with Jinja2
- **Health Checks**: Built-in monitoring endpoints

## 📋 Prerequisites

- Python 3.8+
- RSA key pair for JWT signing
- LTI platform (Canvas, Moodle, Blackboard, etc.)

## 🛠️ Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd examples/fastapi_example
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Generate RSA keys**:

   ```bash
   # Generate private key
   openssl genrsa -out private.key 2048

   # Extract public key
   openssl rsa -in private.key -pubout -out public.key
   ```

## ⚙️ Configuration

1. **Update LTI configuration** in `main.py`:

   ```python
   LTI_CONFIG = {
       "https://your-lms-domain.com": [{
           "default": True,
           "client_id": "your_client_id",
           "auth_login_url": "https://your-lms-domain.com/login/oauth2/auth",
           "auth_token_url": "https://your-lms-domain.com/login/oauth2/token",
           "auth_audience": "https://your-lms-domain.com/login/oauth2/token",
           "key_set_url": "https://your-lms-domain.com/api/lti/security/jwks",
           "private_key_file": "private.key",
           "public_key_file": "public.key",
           "deployment_ids": ["your_deployment_id"]
       }]
   }
   ```

2. **Configure your LTI platform** with these URLs:
   - **Login URL**: `https://your-tool-domain.com/login`
   - **Launch URL**: `https://your-tool-domain.com/launch`
   - **Public Key**: Content of `public.key` file

## 🚀 Running the Application

1. **Start the server**:

   ```bash
   python main.py
   ```

2. **Access the application**:
   - Main page: http://localhost:4000/
   - API docs: http://localhost:4000/docs
   - Health check: http://localhost:4000/health
   - JWKS endpoint: http://localhost:4000/jwks

## 🔗 API Endpoints

| Endpoint  | Method | Description                                |
| --------- | ------ | ------------------------------------------ |
| `/`       | GET    | Main page with LTI information             |
| `/login`  | GET    | OIDC login endpoint                        |
| `/launch` | POST   | LTI message launch endpoint                |
| `/launch` | GET    | Launch page (displays LTI data)            |
| `/jwks`   | GET    | JSON Web Key Set for platform verification |
| `/health` | GET    | Health check endpoint                      |

## 🔐 LTI 1.3 Flow

1. **Platform Initiation**: LMS sends login request to `/login`
2. **OIDC Authentication**: Tool authenticates with platform
3. **Redirect Back**: Tool redirects to platform with tokens
4. **Message Launch**: Platform sends launch message to `/launch`
5. **Content Display**: Tool validates launch and shows content

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   LTI Platform  │    │   FastAPI App    │    │   PyLTI1p3      │
│   (Canvas, etc.)│    │                  │    │   Core Logic    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │ 1. Login Request      │                       │
         ├───────────────────────►                       │
         │                       │                       │
         │                       │ 2. OIDC Auth          │
         │                       ├───────────────────────►│
         │                       │                       │
         │                       │ 3. Auth Response      │
         │                       │◄───────────────────────┤
         │                       │                       │
         │ 4. Redirect with      │                       │
         │    Auth Code          │                       │
         │◄───────────────────────┤                       │
         │                       │                       │
         │ 5. Launch Message     │                       │
         ├───────────────────────►                       │
         │                       │                       │
         │                       │ 6. Validate Launch    │
         │                       ├───────────────────────►│
         │                       │                       │
         │                       │ 7. Launch Data        │
         │                       │◄───────────────────────┤
         │                       │                       │
         │ 8. Display Content    │                       │
         │◄───────────────────────┤                       │
```

## 🔧 Customization

### Adding New LTI Services

```python
from pylti1p3.contrib.fastapi import FastAPIMessageLaunch

@app.post("/custom-service")
async def custom_service(request: Request):
    message_launch = FastAPIMessageLaunch(request, tool_conf)
    launch_data = message_launch.get_launch_data()

    # Access LTI services
    if message_launch.has_ags():
        # Use Assignments & Grades Service
        pass

    if message_launch.has_nrps():
        # Use Names & Roles Service
        pass
```

### Custom Session Storage

```python
from pylti1p3.contrib.fastapi import FastAPIRedisSessionService
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.post("/launch")
async def launch(request: Request):
    session_service = FastAPIRedisSessionService(request, redis_client)
    message_launch = FastAPIMessageLaunch(
        request=request,
        tool_config=tool_conf,
        session_service=session_service
    )
    # ... rest of the code
```

## 🧪 Testing

### Manual Testing

1. **Health Check**: Visit `/health` to verify the service is running
2. **JWKS Endpoint**: Visit `/jwks` to see the public keys
3. **Template Pages**: Navigate between `/` and `/launch` to see the UI

### LTI Platform Testing

1. **Configure the tool** in your LMS with the correct URLs
2. **Launch the tool** from within a course
3. **Verify the launch data** is received and displayed correctly

## 🚨 Troubleshooting

### Common Issues

1. **Key Files Not Found**:

   - Ensure `private.key` and `public.key` exist in the project directory
   - Check file permissions

2. **LTI Configuration Errors**:

   - Verify all URLs in `LTI_CONFIG` are correct
   - Ensure client ID and deployment ID match your LMS configuration

3. **Session Issues**:
   - The default in-memory session storage is not suitable for production
   - Consider using Redis or database-backed storage

### Debug Mode

Enable debug logging by setting environment variables:

```bash
export PYTHONPATH=/path/to/pylti1p3
export LOG_LEVEL=DEBUG
python main.py
```

## 📚 Additional Resources

- [LTI 1.3 Specification](https://www.imsglobal.org/spec/lti/v1p3)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PyLTI1p3 Documentation](https://github.com/dmitry-viskov/pylti1.3)
- [Canvas LTI Documentation](https://canvas.instructure.com/doc/api/file.lti_dev_key_config.html)

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
