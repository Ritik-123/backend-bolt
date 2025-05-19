from rest_framework.renderers import JSONRenderer


class SecurityHeaders(JSONRenderer):
    """
    Renderer which serializes to JSON.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options']= "nosniff"
        response['X-XSS-Protection']= "1"
        response['X-Frame-Options'] = 'SAMEORIGIN'
        # response['Content-Security-Policy'] = "default-src 'self'"
        response['Referrer-Policy'] = "no-referrer-when-downgrade"
        response['Strict-Transport-Security'] = "max-age=315536000; includeSubDomains"
        return response