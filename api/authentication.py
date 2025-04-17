
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from companies.models import Company

class ApiKeyAuthentication(BaseAuthentication):
    """
    Authentication based on API key in request headers
    """
    
    def authenticate(self, request):
        # Get API key from request headers
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return None
        
        # Get company ID from request headers
        company_id = request.headers.get('X-Company-ID')
        if not company_id:
            return None
        
        try:
            # Find company by ID and API key
            company = Company.objects.get(id=company_id, api_key=api_key)
            return (company, None)
        except Company.DoesNotExist:
            raise AuthenticationFailed('Invalid API key or company ID')
