
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from companies.models import Company
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from .models import AuthToken
from .db_handlers import get_user_by_id
import logging

logger = logging.getLogger(__name__)

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


class TokenAuthentication(BaseAuthentication):
    """
    Custom token-based authentication for the API
    """
    
    def authenticate(self, request):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
            
        # Check if the header starts with 'Token '
        parts = auth_header.split()
        if parts[0].lower() != 'token' or len(parts) != 2:
            return None
            
        token = parts[1]
        
        # Get company ID from request headers
        company_id = request.headers.get('X-Company-ID')
        if not company_id:
            return None
            
        try:
            # Find company by ID
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return None
            
        try:
            # Find token in database
            token_obj = AuthToken.objects.get(
                token=token,
                company=company,
                is_active=True
            )
            
            # Check if token is expired
            if token_obj.expires_at < timezone.now():
                token_obj.is_active = False
                token_obj.save()
                raise AuthenticationFailed('Token has expired')
                
            # Get user from company's database
            user = get_user_by_id(company, token_obj.user_id)
            if not user:
                raise AuthenticationFailed('User not found')
                
            # Return authenticated user and token
            return (user, token_obj)
            
        except AuthToken.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error authenticating token: {str(e)}")
            return None