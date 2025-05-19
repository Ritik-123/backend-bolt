from django.middleware.security import SecurityMiddleware

class CustomSecurityMiddleware(SecurityMiddleware):
    def process_response(self, request, response):
        response["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "  # Allow inline styles
            "script-src 'self' 'unsafe-inline' 'unsafe-eval';"  # Allow inline scripts
        )
        return response
