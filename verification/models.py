
from django.db import models
from companies.models import Company
import uuid
from datetime import timedelta
from django.utils import timezone

class VerificationCode(models.Model):
    """Model for storing verification codes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='verification_codes')
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    code = models.CharField(max_length=10)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Verification code for {self.email or self.phone}"
    
    def save(self, *args, **kwargs):
        # Set expiration time if not already set
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

class SMSConfig(models.Model):
    """Model for storing company-specific SMS configurations"""
    SMS_PROVIDERS = (
        ('twilio', 'Twilio'),
        ('nexmo', 'Nexmo/Vonage'),
        ('aws_sns', 'AWS SNS'),
    )
    
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='sms_config')
    provider = models.CharField(max_length=20, choices=SMS_PROVIDERS, default='twilio')
    
    # Twilio settings
    twilio_account_sid = models.CharField(max_length=255, blank=True, null=True)
    twilio_auth_token = models.CharField(max_length=255, blank=True, null=True)
    twilio_from_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Nexmo settings
    nexmo_api_key = models.CharField(max_length=255, blank=True, null=True)
    nexmo_api_secret = models.CharField(max_length=255, blank=True, null=True)
    nexmo_from_name = models.CharField(max_length=20, blank=True, null=True)
    
    # AWS SNS settings
    aws_access_key = models.CharField(max_length=255, blank=True, null=True)
    aws_secret_key = models.CharField(max_length=255, blank=True, null=True)
    aws_region = models.CharField(max_length=20, blank=True, null=True)
    aws_sender_id = models.CharField(max_length=20, blank=True, null=True)
    
    # Whether to use custom or default SMS settings
    use_custom_sms = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"SMS Config for {self.company.name}"

class SMSTemplate(models.Model):
    """Model for storing SMS templates for different purposes"""
    TEMPLATE_TYPES = (
        ('verification', 'Verification Code'),
        ('welcome', 'Welcome Message'),
        ('password_reset', 'Password Reset'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sms_templates')
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    content = models.TextField(help_text="Use {{placeholder}} syntax for dynamic content")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('company', 'template_type')
    
    def __str__(self):
        return f"{self.get_template_type_display()} for {self.company.name}"

class SMSLog(models.Model):
    """Model for logging SMS sending attempts"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sms_logs')
    template_type = models.CharField(max_length=20, choices=SMSTemplate.TEMPLATE_TYPES)
    recipient = models.CharField(max_length=20)
    content = models.TextField()
    status = models.CharField(max_length=20)  # success, failed
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"SMS to {self.recipient} ({self.status})"
