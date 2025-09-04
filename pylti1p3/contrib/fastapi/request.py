from pylti1p3.request import Request


class FastAPIRequest(Request):
    _request = None
    _form_data = None

    def __init__(self, request, form_data):
        """
        Parameters:
            request: FastAPI request
            form_data: form data from FastAPI request
                To get form data from FastAPI request, must use async method.
                As we don't use async functions here, form data must be provided from outside.
        """

        super().__init__()

        self._request = request
        self._form_data = form_data

    @property
    def session(self):
        return self._request.session

    def get_param(self, key):
        if self._request.method == "GET":
            return self._request.query_params.get(key, None)
        return self._form_data.get(key)

    def get_cookie(self, key):
        return self._request.cookies.get(key, None)

    def is_secure(self):
        # Check if the request is using HTTPS
        # First check the URL scheme directly
        if self._request.url.scheme == 'https':
            return True
        
        # If behind a reverse proxy (like Vercel), check X-Forwarded-Proto header
        forwarded_proto = self._request.headers.get('X-Forwarded-Proto')
        if forwarded_proto == 'https':
            return True
        
        # Also check X-Forwarded-Ssl header (some proxies use this)
        forwarded_ssl = self._request.headers.get('X-Forwarded-Ssl')
        if forwarded_ssl and forwarded_ssl.lower() == 'on':
            return True
        
        return False