
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class CompanyAnonRateThrottle(AnonRateThrottle):
    """
    Throttle for anonymous requests based on company ID
    """
    scope = 'company_anon'
    
    def get_cache_key(self, request, view):
        # Get company ID from request
        company_id = request.headers.get('X-Company-ID')
        if company_id:
            return self.cache_format % {
                'scope': self.scope,
                'ident': company_id
            }
        return super().get_cache_key(request, view)

class CompanyUserRateThrottle(UserRateThrottle):
    """
    Throttle for authenticated requests based on company ID
    """
    scope = 'company_user'
    
    def get_cache_key(self, request, view):
        # Get company ID from request
        company_id = request.headers.get('X-Company-ID')
        if company_id:
            return self.cache_format % {
                'scope': self.scope,
                'ident': company_id
            }
        return super().get_cache_key(request, view)
