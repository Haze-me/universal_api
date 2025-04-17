
from django.db import models
from django.utils import timezone
from companies.models import Company
import uuid
import secrets


# Create your models here.
class ApiLog(models.Model):
    """Model for logging API requests"""
    company_id = models.UUIDField()
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    request_data = models.JSONField(blank=True, null=True)
    response_data = models.JSONField(blank=True, null=True)
    status_code = models.IntegerField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"



class AuthToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=255)  # Store the user ID from the company's database
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user_id} - {self.token[:10]}..."

    @classmethod
    def generate_token(cls, company, user_id, expiry_days=30):
        # Generate a secure random token
        token_value = secrets.token_hex(32)
        
        # Deactivate any existing tokens for this user
        cls.objects.filter(company=company, user_id=user_id, is_active=True).update(is_active=False)
        
        # Create a new token
        token = cls.objects.create(
            company=company,
            user_id=user_id,
            token=token_value,
            expires_at=timezone.now() + timezone.timedelta(days=expiry_days)
        )
        
        return token