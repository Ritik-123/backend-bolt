# import logging
# import json

# logger = logging.getLogger('access')
# logger.propagate = False

# class RequestResponseLoggingMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Log the request
#         self.log_request(request)

#         # Process the response
#         response = self.get_response(request)

#         # Log the response
#         self.log_response(request, response)

#         return response

#     def log_request(self, request):
#         try:
#             body = request.body.decode('utf-8') if request.body else ''
#         except Exception as e:
#             body = f"Failed to decode body: {e}"

#         logger.info(f"""
#         [REQUEST]
#         Method: {request.method}
#         Path: {request.get_full_path()}
#         Headers: {dict(request.headers)}
#         Body: {body}
#         """)

#     def log_response(self, request, response):
#         content_type = response.get('Content-Type', '')

#         # Skip logging HTML responses
#         if 'text/html' in content_type:
#             return
#         try:
#             content = response.content.decode('utf-8')
#             try:
#                 content = json.dumps(json.loads(content), indent=2)
#             except Exception:
#                 pass
#         except Exception as e:
#             content = f"Failed to decode response: {e}"

#         logger.info(f"""
#         [RESPONSE]
#         Status Code: {response.status_code}
#         Path: {request.get_full_path()}
#         Body: {content}
#         """)






import logging
from django.utils.deprecation import MiddlewareMixin
# from fuzzer.components.customlog import EncryptedLogFormatter,MyFileHandler
from utils.base import get_uuid


class ContextFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.
    """
    def __init__(self,ip,user):
        self.ip = ip
        self.user = user
        super(ContextFilter, self).__init__()

    
    def filter(self, record):
        record.ip = self.ip
        record.user = self.user
        return True


_logger= logging.getLogger('access')
_logger.propagate = False

class LogRestMiddleware(MiddlewareMixin):
    """
    Middleware to log every request/response.
    """

    def _log_request(self, request):
        """Log the request"""
        ip = str(getattr(request, 'REMOTE_ADDR', ''))
        user = str(getattr(request, 'user', ''))
        method = str(getattr(request, 'method', '')).upper()
        request_path = str(getattr(request, 'path', ''))
        query_params = str(["%s: %s" %(k,v) for k, v in request.GET.items()])
        query_params = query_params if query_params else ''

        _logger.info(f"Log-Request: {ip} {user} {method} {request_path,} {query_params}")
        # _logger.debug(f"{ip} {user} {method} {request_path,} {query_params}")
        # _logger.debug("(%s) [%s] %s %s", ip, method, request_path, query_params)

    def _log_response(self, request, response):
        """Log the response using values from the request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = ''
        if x_forwarded_for:
            ip = x_forwarded_for
            
        else:
            ip = request.META.get('REMOTE_ADDR')
        # token = request.META.get('HTTP_AUTHORIZATION')
        # if token!=None:
        #     uuid = get_uuid(str(token[7::]))
        # else:
        #     uuid = "AnonymousUser"
        user_agent = request.META.get('HTTP_USER_AGENT')
        http_protocol = request.META.get('SERVER_PROTOCOL')
        user = getattr(request.user, 'username', 'AnonymousUser') # uuid
        method = str(getattr(request, 'method', '')).upper()
        status_code = str(getattr(response, 'status_code', ''))
        status_text = str(getattr(response, 'status_text', ''))
        request_path = str(getattr(request, 'path', ''))
        # size = str(len(response.content))
        f = ContextFilter(ip,user)
        _logger.addFilter(f)
        _logger.info(f"Log-Response: {method} {request_path,} {http_protocol} {status_code} {status_text} {user_agent}") #{size}
        # _logger.info("\"%s %s %s \"- %s (%s / %s) (%s)",method, request_path,http_protocol ,status_code, status_text, size,user_agent)

    def process_response(self, request, response):
        """Method call when the middleware is used in the `MIDDLEWARE_CLASSES` option in the settings."""
        self._log_request(request)
        self._log_response(request, response)
        return response# Getting the logger defined in customlog.py


    def __call__(self, request):
        """Method call when the middleware is used in the `MIDDLEWARE` option in the settings """
        self._log_request(request)
        response = self.get_response(request)
        self._log_response(request, response)
        return response