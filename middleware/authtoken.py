
from django.contrib.auth.middleware import MiddlewareMixin
from django.http import HttpResponseForbidden
from fuzzer.models import BlacklistedToken
from utils.base import get_token
from rest_framework_simplejwt.tokens import UntypedToken


class TokenBlacklistMiddleware(MiddlewareMixin):
    """ Middleware for handling token blacklist
        return None if token is valid and
        returns Token is blacklisted
    """

    def process_request(self, request):
        
        header = request.META.get('HTTP_AUTHORIZATION')
        if header:
            try:
                token= get_token(header)
                UntypedToken(token)  # Decode the token without verifying signature
                if BlacklistedToken.objects.filter(token=token).exists():
                    return HttpResponseForbidden('Token is blacklisted')
            except:
                pass
        return None