
from .models import ApiLog
import json
from django.utils.deprecation import MiddlewareMixin

class ApiLogMiddleware(MiddlewareMixin):
    """Middleware for logging API requests and responses"""
    
    def process_request(self, request):
        # Store request data for later use
        request.api_log_data = {
            'method': request.method,
            'path': request.path,
            'body': request.body.decode('utf-8') if request.body else None,
            'headers': {key: value for key, value in request.headers.items()},
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
    
    def process_response(self, request, response):
        # Only log API requests
        if not request.path.startswith('/api/'):
            return response
        
        # Get company ID from request headers
        company_id = request.headers.get('X-Company-ID')
        if not company_id:
            return response
        
        # Get request data
        if hasattr(request, 'api_log_data'):
            request_data = request.api_log_data
        else:
            request_data = {
                'method': request.method,
                'path': request.path,
                'body': None,
                'headers': {},
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
        
        # Parse request body as JSON
        try:
            request_body = json.loads(request_data['body']) if request_data['body'] else None
        except:
            request_body = request_data['body']
        
        # Parse response body as JSON
        try:
            response_body = json.loads(response.content.decode('utf-8')) if response.content else None
        except:
            response_body = response.content.decode('utf-8') if response.content else None
        
        # Create API log
        ApiLog.objects.create(
            company_id=company_id,
            endpoint=request_data['path'],
            method=request_data['method'],
            request_data=request_body,
            response_data=response_body,
            status_code=response.status_code,
            ip_address=request_data['ip_address'],
            user_agent=request_data['user_agent'],
        )
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
